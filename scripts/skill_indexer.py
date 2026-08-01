#!/usr/bin/env python3
"""
Skill Indexer — parses all SKILL.md files, classifies them, indexes into Knowledge Cube.
Also defines skill chains (pipelines) for workflow recommendations.

Usage:
    python scripts/skill_indexer.py          # index all skills + chains
    python scripts/skill_indexer.py --dry    # dry run, no writes
"""

import sys
import json
import re
import hashlib
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from knowledge_cube import get_db

HERMES_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = HERMES_ROOT / "skills"

# ── Action type classification ──────────────────────────────────────────────
ACTION_KEYWORDS = {
    "review":    ["review", "audit", "inspect", "check", "verify", "validation"],
    "generate":  ["generate", "create", "write", "draft", "produce", "build", "make"],
    "fix":       ["fix", "debug", "repair", "patch", "heal", "correct", "resolve"],
    "analyze":   ["analyze", "research", "investigate", "study", "examine", "explore"],
    "plan":      ["plan", "design", "architect", "strategy", "blueprint"],
    "deploy":    ["deploy", "release", "publish", "ship", "launch", "install", "setup"],
    "test":      ["test", "assert", "validate", "qa", "quality"],
    "search":    ["search", "find", "discover", "retrieve", "query", "lookup"],
    "monitor":   ["monitor", "watch", "track", "observe", "alert"],
    "learn":     ["learn", "study", "train", "improve", "evolve", "optimize"],
    "communicate": ["communicate", "message", "notify", "report", "summarize", "brief"],
    "integrate": ["integrate", "connect", "sync", "bridge", "link"],
}

DEFAULT_ACTION = "assist"

# ── Domain mapping (from directory) ────────────────────────────────────────
DOMAIN_FROM_DIR = {
    "agent-browser": "automation",
    "apple": "apple",
    "agent-native-architecture": "architecture",
    "auto-generated": "self-improvement",
    "automation": "automation",
    "autonomous-ai-agents": "ai-agents",
    "autonomous-coding-with-opencode-zen": "development",
    "background-task-discipline": "operations",
    "brainstorming": "planning",
    "branch-context-manager": "development",
    "coding-patterns": "development",
    "communication": "communication",
    "create-agent-skills": "development",
    "creative": "creative",
    "data-science": "data",
    "devops": "devops",
    "dogfood": "qa",
    "domain": "knowledge",
    "email": "communication",
    "file-todos": "productivity",
    "file_ops": "development",
    "finance": "finance",
    "gaming": "entertainment",
    "github": "development",
    "git-worktree": "development",
    "health": "lifestyle",
    "mcp": "integration",
    "media": "creative",
    "mlops": "mlops",
    "note-taking": "productivity",
    "productivity": "productivity",
    "red-teaming": "security",
    "research": "research",
    "response-language": "communication",
    "security": "security",
    "self-improvement": "self-improvement",
    "self-improvement-runtime": "self-improvement",
    "smart-home": "iot",
    "software-development": "development",
    "trend-scout": "research",
    "uncategorized": "general",
    "web-development": "development",
    "yuanbao": "communication",
}

# ── Skill chain definitions ────────────────────────────────────────────────
SKILL_CHAINS = {
    "dev-full-cycle": {
        "description": "Полный цикл разработки: от планирования до деплоя",
        "steps": [
            "plan", "spike", "subagent-driven-development",
            "github-code-review", "github-pr-workflow",
            "test-driven-development", "requesting-code-review"
        ],
        "tags": ["development", "pipeline"],
    },
    "bugfix": {
        "description": "Поиск и исправление бага: диагностика → фикс → проверка → деплой",
        "steps": [
            "systematic-debugging", "bugfix-patterns",
            "test-driven-development", "github-code-review"
        ],
        "tags": ["development", "bug", "fix"],
    },
    "content-pipeline": {
        "description": "Создание контента: исследование → написание → ревью → публикация",
        "steps": [
            "youtube-content", "research", "baoyu-article-illustrator",
            "baoyu-infographic", "design-md"
        ],
        "tags": ["content", "creative", "publishing"],
    },
    "research-pipeline": {
        "description": "Исследование темы: поиск → анализ → структурирование → запись",
        "steps": [
            "trend-scout", "arxiv", "web_search",
            "lavra-research", "lavra-knowledge", "note-taking"
        ],
        "tags": ["research", "knowledge"],
    },
    "deploy-pipeline": {
        "description": "Подготовка к деплою: проверка → сборка → деплой → мониторинг",
        "steps": [
            "requesting-code-review", "devops-patterns",
            "background-task-discipline", "webhook-subscriptions"
        ],
        "tags": ["devops", "deployment"],
    },
    "ai-agent-build": {
        "description": "Сборка AI-агента: проектирование → имплементация → тестирование",
        "steps": [
            "agent-native-architecture", "brainstorming",
            "subagent-driven-development", "claude-code",
            "kanban-orchestrator", "kanban-worker"
        ],
        "tags": ["ai-agents", "development"],
    },
    "security-review": {
        "description": "Аудит безопасности: сканирование → анализ → фикс → верификация",
        "steps": [
            "lavra-agent-security-sentinel", "oss-forensics",
            "requesting-code-review", "godmode"
        ],
        "tags": ["security", "audit"],
    },
    "creative-generate": {
        "description": "Генерация креатива: идея → визуал → доработка",
        "steps": [
            "ideation", "p5js", "excalidraw",
            "architecture-diagram", "baoyu-comic", "ascii-art"
        ],
        "tags": ["creative", "design"],
    },
    "github-workflow": {
        "description": "Работа с GitHub: клон → ветка → PR → ревью → мерж",
        "steps": [
            "github-repo-management", "git-worktree",
            "github-pr-workflow", "github-code-review",
            "codebase-inspection"
        ],
        "tags": ["development", "github"],
    },
}


def parse_frontmatter(filepath):
    """Parse YAML-like frontmatter between --- markers."""
    try:
        content = Path(filepath).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return {}, ""

    # Extract frontmatter
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    yaml_text = parts[1].strip()
    body = parts[2].strip()

    # Simple line-by-line YAML parser (no pyyaml dependency needed)
    meta = {}
    current_key = None
    in_list = False
    list_items = []

    for line in yaml_text.split("\n"):
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            continue

        # Multi-line list continuation
        if in_list and stripped.startswith("- "):
            list_items.append(stripped[2:].strip())
            continue
        elif in_list:
            meta[current_key] = list_items
            in_list = False
            list_items = []

        # Key: value
        if ":" in stripped and not stripped.startswith("-"):
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip()

            # Skip nested objects (e.g. metadata: hermes:)
            if val == "" and not stripped.startswith("  "):
                current_key = key
                # Check if next line starts with "- " -> list
                continue
            elif val == "" and key:
                current_key = key
                continue

            # Store scalar
            # Remove quotes
            val = val.strip("\"'")
            meta[key] = val
            current_key = key

        # List item
        if stripped.startswith("- "):
            if current_key:
                if isinstance(meta.get(current_key), list):
                    meta[current_key].append(stripped[2:].strip())
                else:
                    meta[current_key] = [stripped[2:].strip()]

    # Flush remaining list
    if in_list:
        meta[current_key] = list_items

    return meta, body


def classify_action(name, description, tags):
    """Determine primary action type from name, description, and tags."""
    text = f"{name} {description} {' '.join(tags)}".lower()

    scores = {}
    for action, keywords in ACTION_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[action] = score

    if not scores:
        return DEFAULT_ACTION

    # Return highest scoring action
    return max(scores, key=scores.get)


def extract_triggers(name, description, body, tags):
    """Extract trigger phrases from the skill."""
    triggers = []

    # From tags
    for tag in tags:
        if "_" in tag or "-" in tag:
            triggers.append(tag.replace("_", " ").replace("-", " "))

    # Name itself is a trigger
    triggers.append(name.replace("-", " "))

    # From description key phrases
    desc_lower = description.lower()
    trigger_patterns = [
        r'"([^"]+)"',  # quoted phrases
        r'(?i)trigger:?\s*([^\n.]+)',
        r'(?i)use when:?\s*([^\n.]+)',
        r'(?i)when\s+(you|the|a|your)\s+([^\n.]+)',
    ]
    for pat in trigger_patterns:
        matches = re.findall(pat, desc_lower)
        for m in matches:
            if isinstance(m, tuple):
                m = m[-1]
            if len(m) > 5:
                triggers.append(m.strip())

    return list(set(triggers))[:10]  # max 10


def extract_output_type(body, tags, description):
    """Guess what the skill produces."""
    text = f"{body} {description}".lower()
    outputs = {
        "report": ["report", "summary", "brief", "documentation", "doc"],
        "code": ["code", "script", "implementation", "patch", "diff"],
        "image": ["image", "diagram", "visual", "screenshot", "photo"],
        "data": ["data", "json", "csv", "query", "dataset"],
        "config": ["config", "yaml", "toml", "json", "ini"],
        "message": ["message", "email", "post", "notification", "alert"],
        "plan": ["plan", "design", "architecture", "blueprint"],
        "audio": ["audio", "music", "sound", "voice", "speech"],
        "video": ["video", "animation", "gif", "mp4"],
    }
    for out_type, keywords in outputs.items():
        if any(kw in text for kw in keywords):
            return out_type
    return "other"


def find_related_from_body(body):
    """Find skill references in the body (links to other skills)."""
    refs = []
    refs.extend(re.findall(r'`([a-z][a-z0-9_-]+)`', body))
    refs.extend(re.findall(r'\[([^\]]+)\]\(.*?skill', body))
    return list(r for r in refs if isinstance(r, str) and len(r) > 2)


def index_all_skills(dry_run=False):
    """Parse all SKILL.md files and index into Knowledge Cube."""
    conn = get_db()
    now = datetime.utcnow().isoformat()

    all_skills = []
    stats = {"total": 0, "indexed": 0, "skipped": 0, "errors": 0}

    # Find all SKILL.md files
    skill_files = list(SKILLS_DIR.rglob("SKILL.md"))
    # Also check skills/ directly for flat .md files
    skill_files.extend(SKILLS_DIR.glob("*.md"))

    print(f"Found {len(skill_files)} SKILL files to parse")
    print(f"{'='*60}")

    for fp in sorted(skill_files):
        stats["total"] += 1

        # Determine skill name from directory/file
        rel_path = fp.relative_to(SKILLS_DIR)
        parent_dir = fp.parent.name if fp.parent != SKILLS_DIR else "."

        # Get the directory-based category
        dir_parts = list(fp.relative_to(SKILLS_DIR).parts)
        category = "general"
        domain = "general"
        if len(dir_parts) >= 2:
            category = dir_parts[0]
            domain = DOMAIN_FROM_DIR.get(category, category)

        # Parse frontmatter
        meta, body = parse_frontmatter(fp)

        name = meta.get("name") or fp.stem
        description = meta.get("description") or ""
        version = meta.get("version", "0.1.0")
        author = meta.get("author", "unknown")

        # Get tags
        tags = []
        if "metadata" in meta and isinstance(meta["metadata"], dict):
            hermes_meta = meta["metadata"].get("hermes", {})
            if isinstance(hermes_meta, dict):
                tags = hermes_meta.get("tags", [])
        # Also check simple tags field
        if not tags and "tags" in meta:
            if isinstance(meta["tags"], list):
                tags = meta["tags"]
            else:
                tags = [meta["tags"]]

        # Get related skills from frontmatter
        related_skills = []
        if "metadata" in meta and isinstance(meta["metadata"], dict):
            hermes_meta = meta["metadata"].get("hermes", {})
            if isinstance(hermes_meta, dict):
                related_skills = hermes_meta.get("related_skills", [])

        # Classify
        action_type = classify_action(name, description, tags)
        triggers = extract_triggers(name, description, body, tags)
        output_type = extract_output_type(body, tags, description)

        # Also find related skills mentioned in body
        body_refs = find_related_from_body(body)

        # Merge related skills
        all_related = list(set(related_skills + body_refs))
        # Filter to valid-looking names
        all_related = [r for r in all_related if isinstance(r, str) and len(r) > 2]

        skill_entry = {
            "name": name,
            "description": description[:200] if description else "",
            "category": category,
            "domain": domain,
            "action_type": action_type,
            "output_type": output_type,
            "tags": tags,
            "triggers": triggers,
            "related_skills": all_related,
            "file_path": str(rel_path),
            "version": version,
            "author": author,
        }
        all_skills.append(skill_entry)

        # Write to Knowledge Cube
        if not dry_run:
            content = json.dumps(skill_entry, ensure_ascii=False)
            hash_val = hashlib.sha256(content.encode()).hexdigest()

            existing = conn.execute(
                "SELECT id FROM experiences WHERE hash = ?", (hash_val,)
            ).fetchone()
            if existing:
                stats["skipped"] += 1
                continue

            try:
                conn.execute(
                    """INSERT INTO experiences
                       (ts, content, raw_text, hash, axis_domain, axis_outcome,
                        tags, source)
                       VALUES (?, ?, ?, ?, 'skill', 'indexed', ?, 'skill-indexer')""",
                    (now, content, content, hash_val, json.dumps(tags + [f"action:{action_type}", f"domain:{domain}", f"output:{output_type}"]))
                )
                stats["indexed"] += 1
                print(f"  [+] {name:40s} action={action_type:12s} domain={domain:15s}")
            except Exception as e:
                stats["errors"] += 1
                print(f"  [ERR] {name}: {e}")

    conn.commit()

    # ── Index skill chains ────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"INDEXING SKILL CHAINS ({len(SKILL_CHAINS)} chains)")
    print(f"{'='*60}")

    chains_indexed = 0
    for chain_name, chain_data in SKILL_CHAINS.items():
        if dry_run:
            print(f"  [~] {chain_name}: {chain_data['description']}")
            continue

        content = json.dumps({
            "type": "skill_chain",
            "chain_name": chain_name,
            "description": chain_data["description"],
            "steps": chain_data["steps"],
            "tags": chain_data["tags"],
        }, ensure_ascii=False)
        hash_val = hashlib.sha256(content.encode()).hexdigest()

        existing = conn.execute(
            "SELECT id FROM experiences WHERE hash = ?", (hash_val,)
        ).fetchone()
        if existing:
            print(f"  [=] {chain_name} — exists")
            continue

        conn.execute(
            """INSERT INTO experiences
               (ts, content, raw_text, hash, axis_domain, axis_outcome,
                tags, source)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (now, content, content, hash_val, "skill_chain", "indexed",
             json.dumps(chain_data["tags"] + ["chain", chain_name]),
             "skill-indexer")
        )
        chains_indexed += 1
        print(f"  [+] Chain: {chain_name:25s} ({len(chain_data['steps'])} steps)")

    conn.commit()
    conn.close()

    # ── Summary ────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"  Total SKILL.md files found: {stats['total']}")
    if not dry_run:
        print(f"  Newly indexed:             {stats['indexed']}")
        print(f"  Already existed:           {stats['skipped']}")
        print(f"  Errors:                    {stats['errors']}")
        print(f"  Chains indexed:            {chains_indexed}")
    print(f"  Total unique skills:       {len(all_skills)}")
    print(f"  Chains defined:            {len(SKILL_CHAINS)}")

    # ── Stats ──────────────────────────────────────────────────────────────
    if all_skills:
        action_counts = defaultdict(int)
        domain_counts = defaultdict(int)
        for s in all_skills:
            action_counts[s["action_type"]] += 1
            domain_counts[s["domain"]] += 1

        print(f"\n── Action types ──")
        for action, count in sorted(action_counts.items(), key=lambda x: -x[1]):
            print(f"  {action:15s} {count}")

        print(f"\n── Domains ──")
        for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
            print(f"  {domain:15s} {count}")

    return all_skills


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    if dry:
        print("DRY RUN — no writes to Knowledge Cube\n")
    index_all_skills(dry_run=dry)
