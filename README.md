<div align="center">

  <img src="https://private-user-images.githubusercontent.com/62147746/522686461-030529fd-3a27-42e0-bfe3-e0fb377a265e.png?jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NjQ4ODY0NzYsIm5iZiI6MTc2NDg4NjE3NiwicGF0aCI6Ii82MjE0Nzc0Ni81MjI2ODY0NjEtMDMwNTI5ZmQtM2EyNy00MmUwLWJmZTMtZTBmYjM3N2EyNjVlLnBuZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTEyMDQlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUxMjA0VDIyMDkzNlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPWEyYTJjZmU2ZWI5OGRmMmM0MmUzNDZlMDQ5Y2VkYWE2NDUxZTQwOTU3YWEzMjdjMGYwYzk0NTliYzcyYzdkNDgmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.KZjV43qEOQPvO6n0X_BbYD-tKVnZAes6uwijaWBhops" alt="JellyMerger Logo" width="200">

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
