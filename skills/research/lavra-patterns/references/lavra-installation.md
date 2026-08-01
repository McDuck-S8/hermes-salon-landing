# Lavra Installation on Windows (OpenCode)

## Source
GitHub: https://github.com/roberto-mello/lavra

## Prerequisites
- jq (installed)
- sqlite3 (installed)
- git (installed)
- OpenCode installed and configured

## Installation Steps

### 1. Clone Repository
```bash
cd D:/Portable_Soft
git -c http.proxy="" -c https.proxy="" clone https://github.com/roberto-mello/lavra.git lavra-install
```

### 2. Run Installer
```bash
cd D:/Portable_Soft/lavra-install
USER=Asus ./install.sh --opencode -y
```

**Pitfall:** `USER` variable must be set explicitly on Windows. The installer
expects it to be defined.

### 3. Copy Generated Files (if installer doesn't complete)
```bash
cp -r D:/Portable_Soft/lavra-install/plugins/lavra/opencode/* C:/Users/Asus/.config/opencode/
```

### 4. Set Up Memory Directory
```bash
mkdir -p C:/Users/Asus/.config/opencode/.lavra/memory
cp D:/Portable_Soft/lavra-install/.beads/memory/knowledge.jsonl C:/Users/Asus/.config/opencode/.lavra/memory/
cp D:/Portable_Soft/lavra-install/.beads/memory/recall.sh C:/Users/Asus/.config/opencode/.lavra/memory/
cp D:/Portable_Soft/lavra-install/.beads/memory/knowledge-db.sh C:/Users/Asus/.config/opencode/.lavra/memory/
```

### 5. Create Config
```bash
mkdir -p C:/Users/Asus/.config/opencode/.lavra/config
cat > C:/Users/Asus/.config/opencode/.lavra/config/lavra.json << 'EOF'
{
  "workflow": {
    "research": true,
    "plan_review": true,
    "goal_verification": true,
    "review_scope": "targeted",
    "testing_scope": "targeted"
  },
  "execution": {
    "max_parallel_agents": 3,
    "commit_granularity": "task"
  },
  "model_profile": "balanced"
}
EOF
```

## Installed Components

### Commands (18)
- /lavra-design — planning
- /lavra-work — execution
- /lavra-ship — deployment
- /lavra-qa — testing
- /lavra-learn — learning
- /lavra-recall — memory search
- /lavra-checkpoint — save progress
- /lavra-retro — analytics
- /lavra-import — import
- /lavra-triage — sorting
- /lavra-quick — fast path
- /lavra-plan — plan
- /lavra-research — research
- /lavra-eng-review — engineering review
- /lavra-review — 15 specialized review agents
- /lavra-work-ralph — autonomous retry
- /lavra-work-teams — persistent workers

### Agents (30)
Located in: C:/Users/Asus/.config/opencode/agents/

### Skills (16)
Located in: C:/Users/Asus/.config/opencode/skills/

### Memory
- knowledge.jsonl: 138KB of Lavra knowledge
- recall.sh: memory search script
- knowledge-db.sh: knowledge database script

## Installation Location
All files: C:/Users/Asus/.config/opencode/

## Pitfalls
1. `USER` variable must be set on Windows
2. Installer may timeout — copy files manually if needed
3. Memory directory must be created explicitly
4. Config file must be created manually
5. Proxy must be bypassed for git clone (git -c http.proxy="" -c https.proxy="")