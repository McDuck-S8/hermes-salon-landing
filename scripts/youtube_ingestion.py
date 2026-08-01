#!/usr/bin/env python3
"""
YouTube Ingestion + Schema Extraction Pipeline

Flow:
1. yt-dlp fetches video info + transcript
2. LLM extracts: scheme, offer_vertical, traffic_source, tools, steps, constraints, proof, keys
3. Writes to ripple_keys_{N}.json (append mode)
4. Emits knowledge_added event for Ripple Engine
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add scripts to path for KC integration
sys.path.insert(0, str(Path(__file__).resolve().parent))
from kc_rag import upsert

CACHE_DIR = Path("cache")
RIPPLE_KEYS_DIR = CACHE_DIR
RIPPLE_KEYS_DIR.mkdir(parents=True, exist_ok=True)

EXTRACTION_PROMPT = """Ты — эксперт по арбитражу трафика и CPA. Смотришь YouTube-видео где люди делятся рабочими схемами заработка.

Твоя задача: извлечь структурированную схему из транскрипта.

Верни ТОЛЬКО JSON (без markdown, без комментариев) с полями:

{
  "title": "Название видео (до 120 символов)",
  "source": "youtube",
  "url": "https://youtube.com/watch?v=...",
  "content_summary": "Краткое резюме: какая схема, какой вертикаль, какие инструменты, какой результат (до 500 символов)",
  "aspects": ["список аспектов: traffic_arbitrage, seo_traffic, pbn_networks, ai_tools, automation, case_studies, expert_knowledge, brand_strategy, link_building, community_building, market_trends, iGaming/gambling_vertical, saas_tools, cpa_arbitrage, video_content, lead_generation, email_marketing, paid_social"],
  "conflicts": ["конфликты/ограничения: geo_restrictions, platform_bans, budget_requirements, technical_complexity, legal_risks, saturation"],
  "gaps": ["пробелы в информации: no_step_by_step, no_cost_data, no_tool_names, no_proof, no_timeline, no_scaling_details"],
  "new_keys_generated": ["извлечённые ключи-схемы: snake_case, конкретные: pbn_network_automation, igaming_seo_playbook, traffic_arbitrage_methodology, ai_powered_ad_creation, youtube_cpa_content, mass_pbn_automation, fast_domain_authority_growth, saas_affiliate_programs, creator_network_growth, email_list_building, stablecoin_arbitrage, video_content_replication, open_source_tool_discovery, content_pipeline"],
  "scheme": {
    "vertical": "вертикаль: igaming, nutra, finance, crypto, dating, sweepstakes, ecom, saas, leadgen",
    "traffic_source": "источник: seo, pbn, youtube, tiktok, fb_ads, google_ads, native, push, email, referral, organic",
    "offer_type": "тип оффера: cpa, cpl, cpi, revshare, hybrid",
    "landing_needed": true/false,
    "tools": ["список инструментов: ahrefs, semrush, serpapi, gsa, xrumer, zenno, python, n8n, make, wordpress, cloudflare"],
    "steps": ["пошаговый план: 1. ... 2. ... 3. ..."],
    "budget_estimate": "оценка бюджета: $0-100, $100-500, $500-2000, $2000+",
    "timeline": "время до первых результатов: days, weeks, months",
    "scaling_potential": "low/medium/high",
    "proof_mentioned": true/false
  },
  "key_strength": 0-100,
  "confidence": 0-100,
  "actionable": true/false,
  "reason": "Почему эта схема ценна/проблемна (1-2 предложения)"
}

Правила:
- aspects: выбери 3-7 релевантных из списка выше
- conflicts: только явные ограничения из видео
- gaps: что НЕ сказано, но критично для запуска
- new_keys_generated: 1-5 ключей, snake_case, конкретные названия схем
- scheme: заполни максимально детально из того, что есть в видео
- key_strength: 100 = готово к запуску сейчас, 50 = нужна доработка, 10 = только идея
- confidence: насколько ты уверен в извлечённом (транскрипт может быть неполным)
- actionable: true если есть достаточно деталей для запуска БЕЗ доп. исследований
- reason: честная оценка
"""

def get_video_id(url_or_id: str) -> str:
    """Extract video ID from URL or return as-is if already ID."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$'
    ]
    for pat in patterns:
        m = re.search(pat, url_or_id)
        if m:
            return m.group(1)
    raise ValueError(f"Invalid YouTube URL/ID: {url_or_id}")

def fetch_transcript(video_id: str, lang: str = "ru") -> Optional[str]:
    """Fetch transcript using yt-dlp."""
    try:
        # Try to get auto-generated subtitles first
        cmd = [
            "yt-dlp",
            "--skip-download",
            "--write-auto-sub",
            "--sub-lang", lang,
            "--sub-format", "vtt",
            "-o", "-",
            f"https://youtube.com/watch?v={video_id}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            # Try manual subs
            cmd = [
                "yt-dlp",
                "--skip-download",
                "--write-sub",
                "--sub-lang", lang,
                "--sub-format", "vtt",
                "-o", "-",
                f"https://youtube.com/watch?v={video_id}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and result.stdout:
            # Parse VTT
            lines = result.stdout.split('\n')
            text_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('WEBVTT') and not line.startswith('NOTE') and '-->' not in line and not re.match(r'^\d+$', line):
                    # Remove timestamps and tags
                    clean = re.sub(r'<[^>]+>', '', line)
                    clean = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}', '', clean)
                    if clean:
                        text_lines.append(clean)
            return ' '.join(text_lines)
    except Exception as e:
        print(f"  ⚠️ Transcript fetch failed: {e}")
    return None

def fetch_video_info(video_id: str) -> Dict[str, Any]:
    """Fetch video metadata via yt-dlp."""
    try:
        cmd = [
            "yt-dlp",
            "--skip-download",
            "--print", "title",
            "--print", "description",
            "--print", "channel",
            "--print", "upload_date",
            "--print", "duration",
            f"https://youtube.com/watch?v={video_id}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            return {
                "title": lines[0] if len(lines) > 0 else "",
                "description": lines[1] if len(lines) > 1 else "",
                "channel": lines[2] if len(lines) > 2 else "",
                "upload_date": lines[3] if len(lines) > 3 else "",
                "duration": lines[4] if len(lines) > 4 else ""
            }
    except Exception as e:
        print(f"  ⚠️ Video info fetch failed: {e}")
    return {}

def extract_schema_with_llm(video_id: str, title: str, transcript: str, description: str) -> Dict[str, Any]:
    """Call LLM to extract schema from transcript."""
    # Use the existing LLM infrastructure
    try:
        from openrouter_client import chat_completion
    except ImportError:
        # Fallback: create minimal structure without LLM
        print("  ⚠️ LLM not available, using heuristic extraction")
        return heuristic_extract(video_id, title, transcript, description)
    
    prompt = EXTRACTION_PROMPT + f"\n\n---\nVIDEO ID: {video_id}\nTITLE: {title}\nDESCRIPTION: {description[:1000]}\nTRANSCRIPT (first 15000 chars):\n{transcript[:15000]}"
    
    try:
        response = chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=3000
        )
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        print(f"  ⚠️ LLM extraction failed: {e}")
    
    return heuristic_extract(video_id, title, transcript, description)

def heuristic_extract(video_id: str, title: str, transcript: str, description: str) -> Dict[str, Any]:
    """Heuristic extraction when LLM unavailable."""
    text = f"{title} {description} {transcript}".lower()
    
    # Detect aspects
    aspect_keywords = {
        "traffic_arbitrage": ["арбитраж", "трафик", "медиабай"],
        "seo_traffic": ["seo", "пбн", "яндекс", "гугл", "поиск"],
        "pbn_networks": ["пбн", "pbn", "сателлит", "сеть сайтов"],
        "ai_tools": ["ai", "нейросеть", "чатгпт", "midjourney", "автоматиз"],
        "automation": ["автомат", "скрипт", "бот", "n8n", "make", "зенно"],
        "case_studies": ["кейс", "пример", "результат", "доказательств"],
        "expert_knowledge": ["эксперт", "профессионал", "опыт", "год"],
        "iGaming/gambling_vertical": ["игейминг", "igaming", "казино", "беттинг", "ставки"],
        "cpa_arbitrage": ["cpa", "кост пер акшн", "партнерка", "оффер"],
        "video_content": ["ютуб", "youtube", "видео", "шортс", "reels"],
    }
    
    aspects = []
    for aspect, keywords in aspect_keywords.items():
        if any(kw in text for kw in keywords):
            aspects.append(aspect)
    if not aspects:
        aspects = ["general_knowledge"]
    
    # Detect conflicts
    conflicts = []
    if "крим" in text or "crimea" in text:
        conflicts.append("geo_restrictions")
    if "бан" in text or "банят" in text:
        conflicts.append("platform_bans")
    
    # Detect gaps
    gaps = []
    if "пошаг" not in text and "шаг" not in text:
        gaps.append("no_step_by_step")
    if "бюджет" not in text and "стоимост" not in text and "$" not in text:
        gaps.append("no_cost_data")
    if "инструмент" not in text and "сервис" not in text:
        gaps.append("no_tool_names")
    
    # Generate keys
    keys = []
    if "пбн" in text or "pbn" in text:
        keys.append("pbn_network_automation")
    if "сео" in text or "seo" in text:
        keys.append("seo_traffic_playbook")
    if "арбитраж" in text:
        keys.append("traffic_arbitrage_methodology")
    if "ai" in text or "нейросет" in text:
        keys.append("ai_powered_ad_creation")
    if "ютуб" in text or "youtube" in text:
        keys.append("youtube_cpa_content")
    if not keys:
        keys = ["general_affiliate_marketing"]
    
    # Determine vertical
    vertical = "general"
    if "игейминг" in text or "igaming" in text or "казино" in text:
        vertical = "igaming"
    elif "нутра" in text or "nutra" in text:
        vertical = "nutra"
    elif "финанс" in text or "кредит" in text:
        vertical = "finance"
    
    # Traffic source
    traffic_source = "organic"
    if "fb" in text or "facebook" in text:
        traffic_source = "fb_ads"
    elif "google" in text or "адвордс" in text:
        traffic_source = "google_ads"
    elif "тикток" in text or "tiktok" in text:
        traffic_source = "tiktok"
    elif "пбн" in text or "pbn" in text or "seo" in text:
        traffic_source = "seo"
    
    return {
        "title": title[:120],
        "source": "youtube",
        "url": f"https://youtube.com/watch?v={video_id}",
        "content_summary": (transcript[:500] if transcript else description[:500]) + "...",
        "aspects": aspects,
        "conflicts": conflicts,
        "gaps": gaps,
        "new_keys_generated": keys,
        "scheme": {
            "vertical": vertical,
            "traffic_source": traffic_source,
            "offer_type": "cpa",
            "landing_needed": "лендинг" in text or "landing" in text,
            "tools": [],
            "steps": [],
            "budget_estimate": "unknown",
            "timeline": "unknown",
            "scaling_potential": "medium",
            "proof_mentioned": "доказательств" in text or "пруф" in text or "скрин" in text
        },
        "key_strength": 50,
        "confidence": 60,
        "actionable": len(gaps) < 3,
        "reason": "Heuristic extraction - limited detail without LLM"
    }

def save_to_ripple_keys(entry: Dict[str, Any]) -> str:
    """Append entry to ripple_keys_N.json (rotating files)."""
    # Find existing files
    existing = sorted(RIPPLE_KEYS_DIR.glob("ripple_keys_*.json"))
    target_file = None
    
    for f in existing:
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
            if len(data.get("keys", [])) < 50:  # Max 50 per file
                target_file = f
                break
        except:
            continue
    
    if not target_file:
        # Create new file
        next_num = len(existing) + 1
        target_file = RIPPLE_KEYS_DIR / f"ripple_keys_{next_num}.json"
        data = {"keys": []}
    else:
        with open(target_file, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
    
    # Check for duplicate by URL
    url = entry.get("url", "")
    if not any(k.get("url") == url for k in data["keys"]):
        data["keys"].append(entry)
        with open(target_file, 'w', encoding='utf-8') as fp:
            json.dump(data, fp, ensure_ascii=False, indent=2)
        print(f"  💾 Saved to {target_file.name} (total keys: {len(data['keys'])})")
    else:
        print(f"  ⏭️ Duplicate URL, skipped")
    
    return str(target_file)

def emit_knowledge_added(entry: Dict[str, Any]) -> None:
    """Emit knowledge_added event for chain heartbeat."""
    try:
        content = f"New scheme extracted from YouTube: {entry['title']}. Keys: {', '.join(entry['new_keys_generated'])}. Aspects: {', '.join(entry['aspects'])}."
        upsert(
            content=content,
            tags=",".join(["youtube", "scheme", *entry.get("new_keys_generated", [])]),
            source="youtube_ingestion",
            category="ripple_engine",
            importance=entry.get("key_strength", 50) // 20 + 1,
            confidence=entry.get("confidence", 50) / 100.0,
            verification_method="auto_extracted"
        )
        print(f"  📡 Emitted knowledge_added event")
    except Exception as e:
        print(f"  ⚠️ KC event emit failed: {e}")

def process_video(url_or_id: str) -> Dict[str, Any]:
    """Main pipeline: fetch → extract → save → emit."""
    video_id = get_video_id(url_or_id)
    print(f"\n🎬 Processing video: {video_id}")
    
    # 1. Fetch metadata
    print("  📥 Fetching video info...")
    info = fetch_video_info(video_id)
    title = info.get("title", f"Video {video_id}")
    description = info.get("description", "")
    print(f"    Title: {title[:80]}")
    
    # 2. Fetch transcript
    print("  📝 Fetching transcript...")
    transcript = fetch_transcript(video_id)
    if transcript:
        print(f"    Got {len(transcript)} chars")
    else:
        print(f"    ⚠️ No transcript available")
        transcript = description
    
    # 3. Extract schema
    print("  🧠 Extracting schema...")
    entry = extract_schema_with_llm(video_id, title, transcript, description)
    
    # Ensure required fields
    entry.setdefault("url", f"https://youtube.com/watch?v={video_id}")
    entry.setdefault("source", "youtube")
    
    # 4. Save to ripple_keys
    print("  💾 Saving to ripple_keys...")
    save_to_ripple_keys(entry)
    
    # 4. Emit event
    print("  📡 Emitting knowledge_added...")
    emit_knowledge_added(entry)
    
    print(f"  ✅ Done. Keys generated: {entry.get('new_keys_generated', [])}")
    return entry

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python youtube_ingestion.py <youtube_url_or_id>")
        print("Example: python youtube_ingestion.py 'https://youtube.com/watch?v=dQw4w9WgXcQ'")
        sys.exit(1)
    
    process_video(sys.argv[1])