# YouTube Channel Directory — Monitored Channels

## Active Channels (validated 2026-07-23)

| ID | Channel Handle | URL | Topic | Last Verified | Videos/Run | Status |
|----|---------------|-----|-------|---------------|------------|--------|
| `easy_traff` | @YOSArun | https://www.youtube.com/@YOSArun/videos | cpa-arbitrage | 2026-07-23 | 5 | ✅ Active |
| `partnerkin` | @partnerkin | https://www.youtube.com/@partnerkin/videos | cpa-affiliate | 2026-07-23 | 5 | ✅ Active |

## Irrelevant / Low-Value Channels (validated 2026-07-23)

| ID | Channel Handle | URL | Topic | Last Verified | Videos/Run | Status |
|----|---------------|-----|-------|---------------|------------|--------|
| `icpsquad` | @icpsquad | https://www.youtube.com/@icpsquad/videos | crypto/ICP | 2026-07-23 | 5 | ⚠️ Irrelevant — ICP/crypto content, no CPA/arbitrage, last video 2023 |

**Recommendation:** Remove `icpsquad` from `CHANNELS` in `scripts/youtube_watch.py` — wastes quota on irrelevant content.

## Broken Channels (validated 2026-07-23)

| ID | Channel Handle | URL | Error | Status |
|----|---------------|-----|-------|--------|
| `traffic_hunter` | @TrafficHunter | https://www.youtube.com/@TrafficHunter/videos | "This channel does not have a videos tab" | ❌ Broken — channel may use `/streams`, `/featured`, or custom handle |
| `webvork` | @webvork | https://www.youtube.com/@webvork/videos | "This channel does not have a videos tab" | ❌ Broken — verify handle exists or uses different URL structure |

**Recommendation:** Remove both from `CHANNELS` in `scripts/youtube_watch.py` until correct URLs are found.

## Channel Details

### easy_traff (@YOSArun)
- **Language:** Russian/English mixed
- **Content:** CPA arbitrage case studies, conference coverage, traffic source reviews, team management
- **Frequency:** ~1-2 videos/week
- **Notable series:** "EasyTraff Unfiltered", conference vlogs (MAC, AffPapa), traffic quality debates

### partnerkin (@partnerkin)
- **Language:** Russian
- **Content:** Affiliate marketing, arbitrage team operations, SEO for iGaming, mental health for affiliates
- **Frequency:** ~1-2 videos/week
- **Notable series:** MAC conference proofs, BlackHat SEO, "RIP" reality checks, psychology content

## Candidate Channels (not yet added)

| Channel | Handle | Topic | Notes |
|---------|--------|-------|-------|
| CPA.RU | @cparu | cpa-network | Russian CPA network official channel |
| Affiliate World | @affiliateworld | conferences | Global conference recordings |
| STM Forum | @stmforum | affiliate-education | Paid forum, some free content |
| AdCombo | @adcombo | cpa-network | Network updates, case studies |
| MaxBounty | @maxbounty | cpa-network | Network updates |

## Adding a Channel — Checklist

- [ ] Channel has `/videos` endpoint returning public videos
- [ ] `yt-dlp --flat-playlist --playlist-end 1 --dump-json "<url>"` returns valid JSON
- [ ] Topic tag aligns with existing taxonomy (cpa-arbitrage, cpa-affiliate, cpa-network, conferences, seo, psychology)
- [ ] Added to `CHANNELS` list in `scripts/youtube_watch.py`
- [ ] Manual test passes: `python scripts/youtube_watch.py`
- [ ] Cache updates with new channel data
- [ ] This directory updated with channel metadata

## Channel Audit — 2026-07-23

Ran `python scripts/youtube_watch.py` → 3/5 channels OK, 2 errors, 15 total videos.

| Channel | Result | Action |
|---------|--------|--------|
| easy_traff | ✅ 5 videos | Keep |
| partnerkin | ✅ 5 videos | Keep |
| icpsquad | ✅ 5 videos (all 2023, crypto) | **Remove** — irrelevant topic |
| traffic_hunter | ❌ No videos tab | **Remove** — find correct URL or drop |
| webvork | ❌ No videos tab | **Remove** — find correct URL or drop |

**Next step:** Edit `scripts/youtube_watch.py` CHANNELS list to remove icpsquad, traffic_hunter, webvork. Retest.