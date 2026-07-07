#!/usr/bin/env python3
"""Collecte les téléchargements APK par version depuis GitHub Releases.

Produit:
- stats/downloads.json: état courant agrégé.
- history/downloads-YYYY-MM-DD.json: snapshot quotidien.
"""

import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OWNER = "exec-d"
REPO = "terminus-32"
API = f"https://api.github.com/repos/{OWNER}/{REPO}/releases"


def fetch_releases():
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "terminus-32-download-stats",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(API, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def select_apk_asset(release):
    for asset in release.get("assets", []):
        name = asset.get("name", "")
        if name.endswith(".apk"):
            return asset
    return None


def build_snapshot(releases):
    versions = []
    total_downloads = 0

    for release in releases:
        if release.get("draft") or release.get("prerelease"):
            continue

        asset = select_apk_asset(release)
        if not asset:
            continue

        download_count = int(asset.get("download_count", 0))
        total_downloads += download_count
        versions.append(
            {
                "tag": release.get("tag_name"),
                "publishedAt": release.get("published_at"),
                "apkName": asset.get("name"),
                "downloadCount": download_count,
            }
        )

    versions.sort(key=lambda item: item.get("publishedAt") or "", reverse=True)

    return {
        "meta": {
            "updatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source": "github-releases",
            "repo": f"{OWNER}/{REPO}",
        },
        "versions": versions,
        "totals": {
            "allApkDownloads": total_downloads,
        },
    }


def main():
    snapshot = build_snapshot(fetch_releases())

    stats_dir = ROOT / "stats"
    stats_dir.mkdir(exist_ok=True)
    (stats_dir / "downloads.json").write_text(
        json.dumps(snapshot, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    history_dir = ROOT / "history"
    history_dir.mkdir(exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    (history_dir / f"downloads-{day}.json").write_text(
        json.dumps(snapshot, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    print("stats/downloads.json et history/downloads-YYYY-MM-DD.json à jour")


if __name__ == "__main__":
    main()
