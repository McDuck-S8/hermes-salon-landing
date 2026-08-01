#!/usr/bin/env python3
"""
Stock Footage Fetcher — Pexels/Pixabay API
Downloads vertical (9:16) clips for video composition
"""

import os
import json
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass

CACHE = Path("D:/Portable_Soft/hermes/cache/stock_footage")
CACHE.mkdir(parents=True, exist_ok=True)

PEXELS_KEY = os.environ.get("PEXELS_API_KEY")
PIXABAY_KEY = os.environ.get("PIXABAY_API_KEY")

SEARCH_QUERIES = {
    "gaming": ["mobile gaming", "gamer playing phone", "excited gamer", "phone screen gaming", "video game mobile"],
    "tech": ["smartphone app", "phone screen recording", "tech review", "mobile app demo", "digital lifestyle"],
    "crypto": ["cryptocurrency", "bitcoin trading", "crypto charts", "digital money", "blockchain"],
    "default": ["mobile phone", "smartphone", "happy person phone", "technology lifestyle"],
}

TOPIC_NICHE = {
    "Free V-Bucks": "gaming",
    "Free Robux": "gaming",
    "Free GTA Money": "gaming",
    "Netflix Generator": "tech",
    "Spotify Premium": "tech",
    "Free Crypto": "crypto",
    "Amazon Gift Card": "tech",
}

@dataclass
class StockClip:
    url: str
    width: int
    height: int
    duration: float
    filename: str
    source: str  # pexels/pixabay

class StockFetcher:
    def __init__(self):
        self.pexels_key = PEXELS_KEY
        self.pixabay_key = PIXABAY_KEY
        if not self.pexels_key:
            print("WARNING: PEXELS_API_KEY not set")
        if not self.pixabay_key:
            print("WARNING: PIXABAY_API_KEY not set")
    
    def _get_niche(self, topic: str) -> str:
        return TOPIC_NICHE.get(topic, "default")
    
    def _get_queries(self, topic: str) -> List[str]:
        niche = self._get_niche(topic)
        return SEARCH_QUERIES.get(niche, SEARCH_QUERIES["default"])
    
    async def search_pexels(self, query: str, per_page: int = 10) -> List[Dict]:
        if not self.pexels_key:
            return []
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.pexels_key}
        params = {"query": query, "per_page": per_page, "orientation": "portrait"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("videos", [])
                else:
                    print(f"Pexels error {resp.status}: {await resp.text()}")
        return []
    
    async def search_pixabay(self, query: str, per_page: int = 10) -> List[Dict]:
        if not self.pixabay_key:
            return []
        url = "https://pixabay.com/api/videos/"
        params = {
            "key": self.pixabay_key,
            "q": query,
            "per_page": per_page,
            "orientation": "vertical",
            "video_type": "all",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("hits", [])
                else:
                    print(f"Pixabay error {resp.status}: {await resp.text()}")
        return []
    
    async def fetch_clips(self, topic: str, count: int = 5) -> List[StockClip]:
        """Fetch vertical clips for a topic"""
        queries = self._get_queries(topic)
        clips = []
        niche = self._get_niche(topic)
        safe_topic = topic.replace(" ", "_").lower()
        
        for query in queries:
            if len(clips) >= count:
                break
            
            # Try Pexels first
            videos = await self.search_pexels(query, per_page=5)
            for v in videos:
                if len(clips) >= count:
                    break
                # Find best vertical file
                for f in v.get("video_files", []):
                    if f.get("height", 0) >= f.get("width", 0) * 1.5:  # vertical
                        clip = StockClip(
                            url=f["link"],
                            width=f.get("width", 0),
                            height=f.get("height", 0),
                            duration=v.get("duration", 10),
                            filename=f"pexels_{v['id']}_{f['id']}.mp4",
                            source="pexels",
                        )
                        clips.append(clip)
                        break
            
            # Then Pixabay
            videos = await self.search_pixabay(query, per_page=5)
            for v in videos:
                if len(clips) >= count:
                    break
                for f in v.get("videos", {}).values():
                    if f.get("height", 0) >= f.get("width", 0) * 1.5:
                        clip = StockClip(
                            url=f["url"],
                            width=f.get("width", 0),
                            height=f.get("height", 0),
                            duration=v.get("duration", 10),
                            filename=f"pixabay_{v['id']}_{f.get('file_size',0)}.mp4",
                            source="pixabay",
                        )
                        clips.append(clip)
                        break
        
        return clips[:count]
    
    async def download(self, clip: StockClip, topic: str) -> Optional[Path]:
        """Download clip to cache"""
        safe_topic = topic.replace(" ", "_").lower()
        dest = CACHE / safe_topic / clip.filename
        dest.parent.mkdir(exist_ok=True)
        
        if dest.exists() and dest.stat().st_size > 10000:
            return dest
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(clip.url, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                    if resp.status == 200:
                        async with aiofiles.open(dest, 'wb') as f:
                            async for chunk in resp.content.iter_chunked(8192):
                                await f.write(chunk)
                        print(f"  Downloaded: {clip.filename} ({dest.stat().st_size/1024/1024:.1f}MB)")
                        return dest
        except Exception as e:
            print(f"  Download failed: {e}")
        return None
    
    async def get_clips_for_topic(self, topic: str, count: int = 5) -> List[Path]:
        """Search, download, return local paths"""
        clips = await self.fetch_clips(topic, count)
        paths = []
        for clip in clips:
            path = await self.download(clip, topic)
            if path:
                paths.append(path)
        return paths


async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    parser.add_argument("--count", type=int, default=5)
    args = parser.parse_args()
    
    fetcher = StockFetcher()
    paths = await fetcher.get_clips_for_topic(args.topic, args.count)
    print(f"\nGot {len(paths)} clips for {args.topic}")
    for p in paths:
        print(f"  {p}")

if __name__ == "__main__":
    asyncio.run(main())