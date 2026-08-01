# Blogwatcher Skill — Agent Binding Contract (AGENTS.md)

## Purpose
Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool. Supports automatic feed discovery, HTML scraping fallback, OPML import, and read/unread article management.

## Ownership
Owner: Hermes Agent
Maintainer: Auto-maintained via skill-forge

## Local Contracts

### Triggers (from SKILL.md metadata)
- User asks to monitor, track, or follow blogs/feeds
- User wants to scan for new articles from tracked sources
- User wants to manage read/unread articles from RSS feeds
- Keywords: blog, RSS, Atom, feed, monitor, track, articles, OPML

### Required Tools
- `terminal` — execute blogwatcher-cli commands
- `web_extract` — for fetching feed content when needed
- `search_files` — for finding OPML files or feed configurations

### Configuration (from SKILL.md)
- **Prerequisites**: `blogwatcher-cli` command must be available
- **Installation methods**: Go install, Docker, or binary downloads for Linux/macOS/Windows
- **Database**: Default at `~/.blogwatcher-cli/blogwatcher-cli.db` (override with `BLOGWATCHER_DB` env var)
- **Environment variables**: `BLOGWATCHER_DB`, `BLOGWATCHER_WORKERS`, `BLOGWATCHER_SILENT`, `BLOGWATCHER_YES`, `BLOGWATCHER_CATEGORY`

## Work Guidance

### When to Use This Skill
- User wants to track blog updates without manually checking each site
- User needs to import feeds from OPML (Feedly, Inoreader, NewsBlur exports)
- User wants to manage read/unread status of articles
- User needs HTML scraping fallback when RSS/Atom feeds aren't available

### Common Patterns
1. **Add a blog**: `blogwatcher-cli add "Blog Name" https://example.com`
2. **Add with custom feed**: `blogwatcher-cli add "Blog Name" https://example.com --feed-url https://example.com/feed.xml`
3. **Add with HTML scraping**: `blogwatcher-cli add "Blog Name" https://example.com --scrape-selector "article h2 a"`
4. **Scan for updates**: `blogwatcher-cli scan` (all) or `blogwatcher-cli scan "Blog Name"` (single)
5. **List unread**: `blogwatcher-cli articles`
6. **List all**: `blogwatcher-cli articles --all`
7. **Filter by blog**: `blogwatcher-cli articles --blog "Blog Name"`
8. **Filter by category**: `blogwatcher-cli articles --category "Engineering"`
9. **Mark read/unread**: `blogwatcher-cli read 1` / `blogwatcher-cli unread 1`
10. **Import OPML**: `blogwatcher-cli import subscriptions.opml`

### Docker Usage (for persistent storage)
```bash
# Named volume (simplest)
docker run --rm -v blogwatcher-cli:/data -e BLOGWATCHER_DB=/data/blogwatcher-cli.db ghcr.io/julientant/blogwatcher-cli scan

# Host bind mount
docker run --rm -v /path/on/host:/data -e BLOGWATCHER_DB=/data/blogwatcher-cli.db ghcr.io/julientant/blogwatcher-cli scan
```

## Verification
No `scripts/`, `tests/`, or `evals/` directory exists in this skill directory.

**Manual verification steps:**
1. Verify `blogwatcher-cli` is installed: `blogwatcher-cli --help`
2. Test adding a blog: `blogwatcher-cli add "Test" https://example.com`
3. Test scan: `blogwatcher-cli scan`
4. Test listing: `blogwatcher-cli articles`

## Child DOX Index
No child directories (references/, templates/, scripts/) exist in this skill.

---

*Generated from SKILL.md frontmatter and content. Follows DOX framework for agent binding contracts.*