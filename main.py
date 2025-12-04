#!/usr/bin/env python3

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import requests
import re
from collections import defaultdict
import os
from dotenv import load_dotenv

# ==========================================
# CONFIGURATION
# ==========================================
load_dotenv()
JELLYFIN_URL = os.getenv("JELLYFIN_URL")
API_KEY = os.getenv("JELLYFIN_API_KEY")
USER_ID = os.getenv("JELLYFIN_USER_ID") # Optionnal, None if empty

if not JELLYFIN_URL or not API_KEY:
    raise ValueError("❌ ERROR: The JELLYFIN_URL and JELLYFIN_API_KEY environment variables are required.")

# clean url
JELLYFIN_URL = JELLYFIN_URL.rstrip('/')

app = FastAPI(title="JellyMerger")
templates = Jinja2Templates(directory="templates")

class FileItem(BaseModel):
    name: str
    quality: str
    path: str

class MergeGroup(BaseModel):
    label: str
    files: List[FileItem]
    ids: List[str]

class MergeRequest(BaseModel):
    groups: List[MergeGroup]

class JellyfinManager:
    def __init__(self):
        self.headers = {
            'X-Emby-Token': API_KEY,
            'Authorization': f'MediaBrowser Client="FastAPI Merger", Device="Web", Version="1.0.0", Token="{API_KEY}"',
            'Content-Type': 'application/json'
        }

    def _get(self, endpoint, params={}):
        if USER_ID:
            params['UserId'] = USER_ID
        try:
            r = requests.get(f"{JELLYFIN_URL}{endpoint}", headers=self.headers, params=params)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error API: {e}")
            return {}

    def search_series(self, query: str):
        params = {
            'Recursive': 'true',
            'IncludeItemTypes': 'Series',
            'SearchTerm': query,
            'Fields': 'Name,Id,ProductionYear'
        }
        data = self._get("/Items", params)
        return data.get('Items', [])

    def get_all_episodes_recursive(self, series_id: str):
        params = {
            'Recursive': 'true',
            'ParentId': series_id,
            'IncludeItemTypes': 'Episode',
            'Fields': 'ParentIndexNumber,IndexNumber,Path,Name,MediaSources'
        }
        data = self._get("/Items", params)
        return data.get('Items', [])

    def merge_versions(self, ids: List[str]):
        endpoint = f"{JELLYFIN_URL}/Videos/MergeVersions"
        ids_param = ",".join(ids)
        params = {'Ids': ids_param}
        try:
            r = requests.post(endpoint, headers=self.headers, params=params)
            r.raise_for_status()
            return True
        except Exception as e:
            print(f"Error Merge: {e}")
            return False

manager = JellyfinManager()

# --- Helpers ---

def extract_episode_info(item):
    s = item.get('ParentIndexNumber')
    e = item.get('IndexNumber')
    if s is None or e is None:
        path = item.get('Path', '')
        match = re.search(r'[sS](\d+)[eE](\d+)', path)
        if match:
            s = int(match.group(1))
            e = int(match.group(2))
    return s, e

def normalize_path(path):
    if not path: return ""
    return path.replace('\\', '/').strip()

# ==========================================
# API ROUTES
# ==========================================

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/search")
def search(q: str = ""):
    if len(q) < 2:
        return []
    return manager.search_series(q)

@app.get("/api/analyze/{series_id}")
def analyze(series_id: str):
    episodes = manager.get_all_episodes_recursive(series_id)
    grouped = defaultdict(list)
    
    for ep in episodes:
        s, e = extract_episode_info(ep)
        if s is not None and e is not None:
            key = f"S{s:02d}E{e:02d}"
            grouped[key].append(ep)

    candidates = []

    for key, items in grouped.items():
        if len(items) < 2:
            continue

        # --- Detection Already Merged ---
        detected_paths = set()
        for item in items:
            if item.get('Path'):
                detected_paths.add(normalize_path(item['Path']))
        
        already_merged = False
        for item in items:
            sources = item.get('MediaSources', [])
            if len(sources) > 1:
                known_paths = set()
                for src in sources:
                    if src.get('Path'):
                        known_paths.add(normalize_path(src['Path']))
                
                if detected_paths.issubset(known_paths):
                    already_merged = True
                    break
        
        if already_merged:
            continue
        # --------------------------------

        files = []
        ids = []
        for item in items:
            path = item.get('Path', 'Inconnu')
            filename = path.split('/')[-1].split('\\')[-1]
            # simple quality detection
            quality = "4K/HDR" if any(x in filename for x in ["2160", "4K", "HDR", "DV"]) else "1080p" if "1080" in filename else "SD"
            
            files.append({
                'name': filename,
                'quality': quality,
                'path': path
            })
            ids.append(item['Id'])

        candidates.append({
            'label': key,
            'files': files,
            'ids': ids
        })

    candidates.sort(key=lambda x: x['label'])
    
    return {
        'count': len(candidates),
        'results': candidates
    }

@app.post("/api/merge")
def run_merge(request: MergeRequest):
    success = 0
    errors = 0
    
    for group in request.groups:
        if manager.merge_versions(group.ids):
            success += 1
        else:
            errors += 1
            
    return {'success': success, 'errors': errors}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
