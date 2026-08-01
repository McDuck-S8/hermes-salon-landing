# YouTube Ingestion Pipeline — yt-dlp + Transcript + LLM Extraction → ripple_keys

**Added:** 2026-07-20 | **Session:** Autonomous Ripple Engine deployment

## Overview

Automated pipeline that takes a YouTube URL, fetches video metadata + transcript, extracts structured arbitrage/CPA scheme data via LLM, and writes to `cache/ripple_keys_{N}.json` for the Ripple Engine to consume.

```
YouTube URL
    ↓
yt-dlp (video info + auto-generated subtitles)
    ↓
Transcript (VTT → plain text, ru/en)
    ↓
LLM Extraction (schema: title, aspects, conflicts, gaps, keys, scheme, metrics)
    ↓
Append to ripple_keys_{N}.json (dedup by URL)
    ↓
Emit knowledge_added event → chain_heartbeat → KC categorization
```

## Implementation: `scripts/youtube_ingestion.py`

### Key Functions

```python
fetch_video_info(video_id)          # yt-dlp --dump-json
fetch_transcript(video_id, lang)    # yt-dlp --write-auto-sub --sub-format vtt
extract_schema_llm(info, transcript) # LLM with EXTRACTION_PROMPT (see below)
extract_schema_heuristic(info)      # Fallback when LLM unavailable
save_to_ripple_keys(data)           # Append to ripple_keys_{N}.json, dedup by URL
emit_knowledge_added(key, source)   # event_beat("knowledge_added")
```

### LLM Extraction Prompt (`EXTRACTION_PROMPT`)

Structured prompt requesting JSON with fields:
- `title`, `source`, `url`, `content_summary`
- `aspects` (from controlled vocab: traffic_arbitrage, seo_traffic, pbn_networks, ai_tools, automation, case_studies, expert_knowledge, community_building, market_trends, iGaming/gambling_vertical, saas_tools, cpa_arbitrage, video_content, lead_generation, email_marketing, paid_social)
- `conflicts` (geo_restrictions, platform_bans, budget_requirements, technical_complexity, legal_risks, saturation)
- `gaps` (no_step_by_step, no_cost_data, no_tool_names, no_proof, no_timeline, no_scaling_details)
- `new_keys_generated` (snake_case scheme names: pbn_network_automation, igaming_seo_playbook, traffic_arbitrage_methodology, ai_powered_ad_creation, youtube_cpa_content, mass_pbn_automation, fast_domain_authority_growth, saas_affiliate_programs, creator_network_growth, email_list_building, stablecoin_arbitrage, video_content_replication, open_source_tool_discovery, content_pipeline)
- `scheme` object (vertical, traffic_source, offer_type, landing_needed, tools[], steps[], budget_estimate, timeline, scaling_potential, proof_mentioned)
- `key_strength` (0-100), `confidence` (0-100), `actionable` (bool), `reason` (string)

### Heuristic Fallback (when LLM unavailable)

Uses title/description keywords to populate fields:
- Keyword → aspect mapping (e.g., "SEO" → seo_traffic, "PBN" → pbn_networks)
- Keyword → new_key mapping (e.g., "PBN" → pbn_network_automation)
- Simple scheme object from detected vertical/traffic source

### Deduplication

Dedup by URL hash — same video processed twice → skipped with "Duplicate URL, skipped".

### Event Emission

```python
from chain_heartbeat import event_beat
event_beat("knowledge_added")
# Triggers: cube-categorizer, knowledge-gap-filler
```

## Integration Points

| Component | Role |
|-----------|------|
| `scripts/youtube_ingestion.py` | Main pipeline |
| `scripts/ripple_engine.py` | Consumes ripple_keys JSON daily at 09:00 |
| `scripts/chain_heartbeat.py` | Receives `knowledge_added` event |
| `scripts/kc_rag.py` | Categorizes new entries (cube-categorizer) |
| `cache/ripple_keys_{1,2,3}.json` | Persistent stone storage |

## Usage

```bash
# Single video
python scripts/youtube_ingestion.py "https://youtube.com/watch?v=VIDEO_ID"

# Batch (from file with URLs)
python scripts/youtube_ingestion.py --batch urls.txt
```

## Pitfalls & Fixes

| Issue | Fix |
|-------|-----|
| No transcript available | Heuristic fallback extracts from title/description |
| LLM unavailable (no API key) | Heuristic fallback works offline |
| Geo-restricted videos | yt-dlp fails gracefully, logs warning |
| Duplicate URLs | Dedup by URL before append |
| Transcript in wrong language | `--sub-lang ru,en` tries multiple |
| yt-dlp version | Requires yt-dlp ≥ 2024.01 (auto-subs improvements) |

## Related Skills

- `autonomous-system-operations` — Ripple Engine pattern (consumes these stones daily)
- `daily-monitoring` — YouTube channel list for batch ingestion
- `chain-heartbeat` — Event emission integration
- `self-improvement` — New stones feed improvement suggestions

## Files in This Session

- `scripts/youtube_ingestion.py` — Pipeline implementation
- `cache/ripple_keys_1.json` — 54 existing stones (EASY_TRAFF, PARTNERKIN, ICPSQUAD)
- `cache/ripple_keys_2.json` — Partnerkin YouTube extractions
- `cache/ripple_keys_3.json` — Additional extractions