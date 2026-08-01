#!/usr/bin/env python3
"""
Skill Audit — сканирует skills/ и выдаёт отчёт:
- валидные / битые / пустые / дубликаты SKILL.md
- отсутствующие AGENTS.md (DOX child index)
- старые скиллы (>90 дней без изменений)
- скиллы без связанных других (isolated)
- skill_chains: какие цепочки поломаны (нехватка скиллов)

Запускается через cron каждые 6 часов + event-driven при изменении skills/
Вывод: JSON в cache/skill_audit.json + событие skill_audit_complete
"""

import json
import os
import sqlite3
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
SKILLS_DIR = HERMES_HOME / "skills"
CACHE_DIR = HERMES_HOME / "cache"
KC_DB = CACHE_DIR / "knowledge_cube.db"
EVENTS_DB = CACHE_DIR / "events.db"
AUDIT_CACHE = CACHE_DIR / "skill_audit.json"

EXPECTED_DOMAINS = {
    "auto-generated", "automation", "autonomous-ai-agents", "background-task-discipline",
    "brainstorming", "branch-context-manager", "bugfix", "caveman", "coding-patterns",
    "communication", "computer-use", "create-agent-skills", "creative", "crimea-job-search",
    "crystal", "crystal-ai-core-5226", "crystal-ai-core-6160", "crystal-ai-core-6373",
    "crystal-self-learning", "crystal-telegram-bots-106", "crystal-telegram-bots-1345",
    "crystal-telegram-bots-5685", "crystal-test-4132", "crystal-test-572", "crystal-test-chain-2228",
    "crystal-user-needs-1999", "crystal-user-needs-6833", "crystal-user-needs-8407",
    "crystal-websites-1917", "crystal-websites-3673", "crystal-websites-918",
    "crystal-youtube-8073", "crystal-youtube-820", "crystal_will", "data-science",
    "deploy-cosmetologist", "design", "devops", "dogfood", "ego-windows", "file-todos",
    "file_ops", "finance", "general", "git-worktree", "herdr-multiagent", "hermes-agent",
    "hermes-desktop-plugins", "human-source", "human_source", "income-research-methodology",
    "integration", "knowledge", "lavra-agent-agent-native-reviewer", "lavra-agent-ankane-readme-writer",
    "lavra-agent-architecture-strategist", "lavra-agent-best-practices-researcher",
    "lavra-agent-bug-reproduction-validator", "lavra-agent-code-simplicity-reviewer",
    "lavra-agent-data-integrity-guardian", "lavra-agent-data-migration-expert",
    "lavra-agent-deployment-verification-agent", "lavra-agent-design-implementation-reviewer",
    "lavra-agent-design-iterator", "lavra-agent-dhh-rails-reviewer", "lavra-agent-every-style-editor",
    "lavra-agent-figma-design-sync", "lavra-agent-framework-docs-researcher",
    "lavra-agent-git-history-analyzer", "lavra-agent-goal-verifier", "lavra-agent-julik-frontend-races-reviewer",
    "lavra-agent-kieran-python-reviewer", "lavra-agent-kieran-rails-reviewer",
    "lavra-agent-kieran-typescript-reviewer", "lavra-agent-learnings-researcher",
    "lavra-agent-lint", "lavra-agent-migration-drift-detector",
    "lavra-agent-pattern-recognition-specialist", "lavra-agent-performance-oracle",
    "lavra-agent-pr-comment-resolver", "lavra-agent-repo-research-analyst",
    "lavra-agent-security-sentinel", "lavra-agent-spec-flow-analyzer", "lavra-brainstorm",
    "lavra-ceo-review", "lavra-eng-review", "lavra-knowledge", "lavra-memory-system",
    "lavra-plan", "lavra-research", "lavra-review", "lavra-work", "lavra-work-multi",
    "lavra-work-single", "max-brain-lessons", "mcp", "media", "meta", "mlops",
    "mlops/evaluation", "mlops/inference", "mlops/models", "mlops/research", "note-taking",
    "omh-autopilot", "omh-deep-interview", "omh-deep-research", "omh-ralph",
    "omh-ralph-driver", "omh-ralph-task", "omh-ralplan", "omh-ralplan-driver",
    "omh-triage", "omh-triage-driver", "personalities", "ponytail", "procedural-logic",
    "productivity", "response-language", "security", "self-improvement",
    "self-improvement-from-channels", "self-improvement-runtime", "session_management",
    "shadscan", "shadscan/.agents/skills", "site-mapper", "site-maps", "skill-pathfinder",
    "skillspector/tests/fixtures", "skillspector/tests/fixtures/sdi",
    "skillspector/tests/fixtures/sqp", "skillspector/tests/fixtures/ssd",
    "social-media", "software-development", "superpowers", "tool-catalog",
    "trend-scout", "trendshift-monitor", "ui-ux-pro-max/.claude/skills",
    "ui-ux-pro-max/cli/assets/skills", "uncategorized", "uncategorized-to-domain",
    "web-development", "youtube-channel-monitor", "yuanbao", "coding-patterns-agentsky"
}

SKILL_CHAINS = {
    "dev-full-cycle": ["plan", "spike", "subagent-driven-development", "github-code-review", "github-pr-workflow", "test-driven-development", "requesting-code-review"],
    "bugfix": ["systematic-debugging", "bugfix-patterns", "test-driven-development", "github-code-review"],
    "content-pipeline": ["youtube-content", "research", "baoyu-article-illustrator", "baoyu-infographic", "design-md"],
    "research-pipeline": ["trend-scout", "arxiv", "web-search", "lavra-research", "lavra-knowledge", "note-taking"],
    "deploy-pipeline": ["requesting-code-review", "devops-patterns", "background-task-discipline", "webhook-subscriptions"],
    "ai-agent-build": ["agent-native-architecture", "brainstorming", "subagent-driven-development", "claude-code", "kanban-orchestrator", "kanban-worker"],
    "security-review": ["lavra-agent-security-sentinel", "oss-forensics", "requesting-code-review", "godmode"],
    "creative-generate": ["ideation", "p5js", "excalidraw", "architecture-diagram", "baoyu-comic", "ascii-art"],
    "github-workflow": ["github-repo-management", "git-worktree", "github-pr-workflow", "github-code-review", "codebase-inspection"],
}


def parse_skill_md(path: Path) -> dict:
    """Parse SKILL.md frontmatter + body."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"error": f"read failed: {e}", "path": str(path)}

    # Extract frontmatter
    meta = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            yaml_text = parts[1].strip()
            body = parts[2].strip()
            for line in yaml_text.split("\n"):
                if ":" in line and not line.strip().startswith("#"):
                    key, _, val = line.partition(":")
                    meta[key.strip()] = val.strip().strip('"\'')

    # Basic fields
    name = meta.get("name") or path.parent.name
    description = meta.get("description", "")
    category = meta.get("category", path.parent.parent.name if path.parent.parent != SKILLS_DIR else "general")
    version = meta.get("version", "0.1.0")
    author = meta.get("author", "unknown")

    # Tags
    tags = []
    if "metadata" in meta and isinstance(meta["metadata"], dict):
        hermes_meta = meta["metadata"].get("hermes", {})
        if isinstance(hermes_meta, dict):
            tags = hermes_meta.get("tags", [])
    if not tags and "tags" in meta:
        if isinstance(meta["tags"], list):
            tags = meta["tags"]
        else:
            tags = [meta["tags"]]

    # Related skills
    related = []
    if "metadata" in meta and isinstance(meta["metadata"], dict):
        hermes_meta = meta["metadata"].get("hermes", {})
        if isinstance(hermes_meta, dict):
            related = hermes_meta.get("related_skills", [])

    # Check for AGENTS.md in skill dir
    has_agents = (path.parent / "AGENTS.md").exists()

    # File stats
    stat = path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime)
    age_days = (datetime.now() - mtime).days
    size = stat.st_size

    # Content hash
    content_hash = hashlib.md5(content.encode()).hexdigest()[:12]

    return {
        "name": name,
        "path": str(path.relative_to(SKILLS_DIR)),
        "description": description[:200],
        "category": category,
        "version": version,
        "author": author,
        "tags": tags,
        "related_skills": related,
        "has_agents_md": has_agents,
        "mtime": mtime.isoformat(),
        "age_days": age_days,
        "size": size,
        "content_hash": content_hash,
        "body_preview": body[:300],
        "valid": "error" not in locals(),
    }


def check_skill_chains(skills: list[dict]) -> dict:
    """Check which skill chains are broken (missing skills)."""
    skill_names = {s["name"] for s in skills if "name" in s}
    results = {}
    for chain_name, steps in SKILL_CHAINS.items():
        missing = [s for s in steps if s not in skill_names]
        present = [s for s in steps if s in skill_names]
        results[chain_name] = {
            "total_steps": len(steps),
            "present": len(present),
            "missing": missing,
            "complete": len(missing) == 0,
        }
    return results


def find_duplicates(skills: list[dict]) -> list[dict]:
    """Find skills with duplicate content hashes or names."""
    by_hash = {}
    by_name = {}
    dupes = []

    for s in skills:
        if "content_hash" in s:
            h = s["content_hash"]
            if h in by_hash:
                dupes.append({"type": "content_hash", "hash": h, "skills": [by_hash[h]["name"], s["name"]]})
            else:
                by_hash[h] = s
        n = s.get("name", "")
        if n in by_name:
            dupes.append({"type": "name", "name": n, "skills": [by_name[n]["path"], s["path"]]})
        else:
            by_name[n] = s

    return dupes


def main():
    print("=== SKILL AUDIT ===")
    print(f"Scanning: {SKILLS_DIR}")

    # Find all SKILL.md files
    skill_files = list(SKILLS_DIR.rglob("SKILL.md"))
    print(f"Found {len(skill_files)} SKILL.md files")

    # Parse each
    skills = []
    errors = []
    for sf in skill_files:
        parsed = parse_skill_md(sf)
        if "error" in parsed:
            errors.append(parsed)
        else:
            skills.append(parsed)

    # Categorize
    valid = [s for s in skills if s.get("valid", True) and s.get("size", 0) > 100]
    empty = [s for s in skills if s.get("size", 0) <= 100]
    stale = [s for s in skills if s.get("age_days", 0) > 90]
    no_agents = [s for s in skills if not s.get("has_agents_md", False)]
    isolated = [s for s in skills if not s.get("related_skills") and not s.get("tags")]

    # Skill chains
    chain_status = check_skill_chains(skills)

    # Duplicates
    dupes = find_duplicates(skills)

    # Domain coverage
    categories = {}
    for s in skills:
        cat = s.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1

    missing_domains = EXPECTED_DOMAINS - set(categories.keys())

    # Build report
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_files": len(skill_files),
            "valid": len(valid),
            "empty": len(empty),
            "errors": len(errors),
            "stale_90d": len(stale),
            "no_agents_md": len(no_agents),
            "isolated": len(isolated),
            "duplicates": len(dupes),
            "categories": len(categories),
            "missing_domains": len(missing_domains),
        },
        "details": {
            "valid_skills": [{"name": s["name"], "path": s["path"], "category": s["category"], "age_days": s["age_days"]} for s in valid],
            "empty_skills": [{"name": s["name"], "path": s["path"], "size": s["size"]} for s in empty],
            "errors": errors,
            "stale_skills": [{"name": s["name"], "path": s["path"], "age_days": s["age_days"]} for s in stale],
            "missing_agents_md": [{"name": s["name"], "path": s["path"]} for s in no_agents],
            "isolated_skills": [{"name": s["name"], "path": s["path"]} for s in isolated],
            "duplicates": dupes,
            "categories": dict(sorted(categories.items(), key=lambda x: -x[1])),
            "missing_domains": sorted(list(missing_domains)),
            "skill_chains": chain_status,
        }
    }

    # Save to cache
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_CACHE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n💾 Report saved: {AUDIT_CACHE}")

    # Fire event to events.db
    try:
        conn = sqlite3.connect(str(EVENTS_DB))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                timestamp TEXT,
                data TEXT,
                source TEXT DEFAULT 'system',
                priority INTEGER DEFAULT 5,
                processed INTEGER DEFAULT 0
            )
        """)
        conn.execute(
            "INSERT INTO events (event_type, timestamp, data, source) VALUES (?, ?, ?, ?)",
            ("skill_audit_complete", datetime.now().isoformat(), json.dumps({"summary": report["summary"]}), "skill_audit")
        )
        conn.commit()
        conn.close()
        print("📡 Event fired: skill_audit_complete")
    except Exception as e:
        print(f"⚠️ Event fire failed: {e}")

    # Also fire heartbeat event
    try:
        from chain_heartbeat import event_beat
        event_beat("skill_audit_complete")
    except Exception as e:
        print(f"⚠️ Heartbeat fire failed: {e}")

    # Print summary
    print(f"""
SUMMARY:
  Total SKILL.md:     {report['summary']['total_files']}
  Valid:              {report['summary']['valid']}
  Empty/Trivial:      {report['summary']['empty']}
  Parse Errors:       {report['summary']['errors']}
  Stale (>90d):       {report['summary']['stale_90d']}
  Missing AGENTS.md:  {report['summary']['no_agents_md']}
  Isolated (no refs): {report['summary']['isolated']}
  Duplicates:         {report['summary']['duplicates']}
  Categories:         {report['summary']['categories']}
  Missing domains:    {report['summary']['missing_domains']}
""")

    # Skill chains
    for chain, status in chain_status.items():
        icon = "✅" if status["complete"] else "⚠️"
        print(f"  {icon} {chain}: {status['present']}/{status['total_steps']} steps")
        if status["missing"]:
            print(f"      Missing: {', '.join(status['missing'])}")

    return 0 if report['summary']['errors'] == 0 and report['summary']['empty'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())