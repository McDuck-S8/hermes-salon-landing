# KC Data Quality Audit — 2026-07-25

## Database: `cache/knowledge_cube.db`

### Table: `experiences` (12,979 rows — 95% noise)

| Source | Count | % | Nature |
|--------|-------|---|--------|
| `improvement_suggestions` | 9,262 | 71.4% | Auto-generated log patterns — `[suggestion:log_unknown]` noise |
| `skill-indexer` | 1,551 | 12.0% | Auto-indexed skill metadata |
| `kc_feeder` | 763 | 5.9% | Auto-rss and auto-parsed |
| `knowledge_filter` | 362 | 2.8% | Filtered RSS — clean-ish |
| `rss` | 201 | 1.5% | Actual RSS feed content |
| Other (agent-decision, research_*, arbi*) | 166 | 1.3% | Clean agent decisions |
| `github-research` | 80 | 0.6% | GitHub research |
| `arbitrage-research` | 54 | 0.4% | Arbitrage-specific research |

### Domain Distribution in `experiences`

| Domain | Count | % |
|--------|-------|---|
| `_suggestion_log` | 5,424 | 41.8% |
| `debugging` | 3,852 | 29.7% |
| `skill` | 1,551 | 11.9% |
| Other (uncategorized, testing, documentation, etc.) | ~2,200 | 16.6% |
| `arbitrage` | **0** | **0%** |

### Table: `kc_entries` (464 rows — actual curated knowledge)

| Source | Count |
|--------|-------|
| Script documentation | ~200 |
| Errors & fixes | ~100 |
| Research findings | ~80 |
| RSS content | ~50 |
| Agent decisions | ~30 |

### Key Takeaway

The `experiences` table is 95% noise. The `kc_entries` table is the actual knowledge base (only ~500 entries).

**When citation from KC is needed:**
- Query `kc_entries` table, NOT `experiences`
- Filter by source: `knowledge_filter`, `github-research`, `arbitrage-research`, `rss`, `agent-decision`
- Check confidence >= 0.5
- The wheel uses `experiences` by default — must be redirected to clean source

**Clean data view created 2026-07-25:**
- `wheel_data` — 768 clean records from all verified sources
- Can be recreated if needed
