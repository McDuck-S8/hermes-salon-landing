# CC Harness Skills — Installed 2026-06-07

Source: https://github.com/LearnPrompt/cc-harness-skills
Location: D:/Portable_Soft/hermes/skills/self-improvement/
Original repo: D:/Portable_Soft/cc-harness-skills/

## Installed Skills (all zero-dependency, Python 3 stdlib only)

### 1. dream-memory
- **Purpose:** Consolidate scattered notes, session logs, memory files into clean long-term memory
- **Script:** `dream-memory/scripts/dream_memory.py --memory-root /path/to/memory [--transcripts-dir /path] [--recent N] [--json]`
- **Prompt:** `dream-memory/references/prompt-template.md` — 4-phase pass: ORIENT → GATHER → CONSOLIDATE → PRUNE
- **Key rule:** MEMORY.md is an INDEX, not a content dump. Convert relative dates to absolute. Max 200 lines / 25KB.

### 2. verification-gate
- **Purpose:** Force agent to prove task is actually done, not just claimed done
- **Script:** `verification-gate/scripts/verification_context.py --repo /path/to/repo [--json]`
- **Prompt:** `verification-gate/references/prompt-template.md` — 4 questions: matches request? evidence? regressions? overstated?
- **Key rule:** Default to read-only during verification. Findings first in output.

### 3. structured-context-compressor
- **Purpose:** Compress long conversations into 9-part structured continuation summary
- **Script:** `structured-context-compressor/scripts/render_template.py` — prints 9-section scaffold
- **Prompt:** `structured-context-compressor/references/prompt-template.md`
- **9 sections:** intent, concepts, files, errors, problem-solving, all user messages, pending, current work, next step
- **Key rule:** Preserve ALL user messages. Never compress away corrections.

### 4. memory-extractor
- **Purpose:** Extract durable memories from conversation turns (user prefs, feedback, constraints, references)
- **Script:** `memory-extractor/scripts/memory_manifest.py --memory-root /path/to/memory`
- **Avoid:** storing code structure, short-lived task state, duplicating existing topics

### 5. swarm-coordinator
- **Purpose:** Split large work into 4 phases: research → synthesis → implementation → verification
- **Script:** `swarm-coordinator/scripts/task_board.py --goal "..." --worker research --worker implementation --worker verification`
- **Use for:** broad codebase exploration, cross-file bug hunts, parallel review

### 6. kairos-lite
- **Purpose:** Lightweight proactive jobs with scheduling, sleep, expiry safeguards
- **Script:** `kairos-lite/scripts/job_spec.py --name "..." --prompt "..." --schedule "..." --expires-in "2h"`
- **Use for:** scheduled repo patrols, unattended follow-up checks, short user briefs

## How These Relate to Hermes

- **dream-memory** → complements Lavra knowledge capture; could consolidate memory_tree/wiki
- **verification-gate** → pairs with requesting-code-review skill; adds "did it actually work?" layer
- **structured-context-compressor** → useful for session handoff and context window management
- **swarm-coordinator** → overlaps with delegate_task batch mode; provides structured phase gating
- **memory-extractor** → complements auto_recall; extracts structured memories from raw conversation
- **kairos-lite** → overlaps with Hermes cron system; provides portable job spec format
