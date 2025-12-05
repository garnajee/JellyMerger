<div align="center">

  <img src="https://github.com/user-attachments/assets/030529fd-3a27-42e0-bfe3-e0fb377a265e" alt="JellyMerger Logo" width="200">

[![license MIT badge](https://img.shields.io/github/license/garnajee/JellyMerger)](https://opensource.org/licenses/MIT)
![docker badge](https://img.shields.io/badge/docker-image-blue?logo=docker)
![ci cd badge](https://github.com/garnajee/jellymerger/actions/workflows/docker-publish.yml/badge.svg)

<br>
<em>Easily merge multiple versions of your media in Jellyfin.</em>
</div>

# About

This application provides a simple Web Interface to detect and merge duplicate episodes of TV Shows in your Jellyfin library (e.g., grouping a 1080p version and a 4K version into a single item).

It uses the official Jellyfin API to perform the merge cleanly without direct database manipulation.

> [!IMPORTANT]
> Series Only: Currently, this tool only supports TV Shows. Movies are not yet supported.

No File Management: This tool does not move, rename, or download files.

You must manually place the different versions (e.g., `S01E01 - 1080p.mkv` and `S01E01 - 4K.mkv`) in your library folders.

Jellyfin must have scanned them and show them as separate episodes before this tool can merge them.

## Getting Started
### Option 1: Docker (Recommended)

Create a docker-compose.yml file:

```yaml
services:
  jellymerger:
    image: ghcr.io/garnajee/jellymerger:latest
    container_name: jellymerger
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - JELLYFIN_URL=http://192.168.1.10:8096
      - JELLYFIN_API_KEY=your_jellyfin_api_key
      # - JELLYFIN_USER_ID=optional_user_id
```

Run it:

```bash
docker compose up -d
```

Access the interface at `http://your-server-ip:8000`.

### Option 2: Local Installation

Clone the repo:

```bash
git clone https://github.com/garnajee/jellymerger.git
cd jellymerger
```

Install dependencies (using [`uv`](https://docs.astral.sh/uv)):

```bash
uv sync
```

Configure Environment:
Create a .env file in the root directory:

```
JELLYFIN_URL=http://localhost:8096
JELLYFIN_API_KEY=your_api_key
```

Run:

```bash
uv run uvicorn main:app --reload
```

## Usage

Open the web interface.

Search for a TV Show (e.g., "The Witcher").

The tool will scan all seasons and detect episodes that exist in multiple versions but are not yet merged.

Review the list and click Merge to group them in Jellyfin.

# License

Distributed under the [MIT](LICENSE) License. See [LICENSE](LICENSE) for more information.
