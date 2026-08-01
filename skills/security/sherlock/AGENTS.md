# sherlock — Skill

## Purpose
OSINT username search across 400+ social networks. Hunt down social media accounts by username using the Sherlock Project.

## Ownership
Managed by Hermes Agent. Located in `security/sherlock/`.

## Local Contracts
- **Triggers**: User asks to find accounts for a username, check username availability across platforms, conduct OSINT/reconnaissance, or queries like "where is this username registered?"
- **Required tools**: `terminal` (for sherlock CLI), `read_file` (for output files)
- **Config**: No config.yaml required. Prerequisite: `sherlock` CLI command available (install via `pipx install sherlock-project` or Docker).
- **Related skills**: (none listed in SKILL.md)

## Work Guidance
**When to use**: Finding social media accounts by username, checking username availability, OSINT/reconnaissance research.

**Procedure**:
1. **Check installation**: Run `sherlock --version` first. If not installed → offer `pipx install sherlock-project` (recommended) or `pip install sherlock-project`. Don't try multiple methods.
2. **Extract username**: Get exact username from user message (preserve case/numbers/underscores). Only clarify if multiple/ambiguous/missing usernames.
3. **Build command**: Default: `sherlock --print-found --no-color "<username>" --timeout 90`. Only add `--nsfw` or `--tor` if user explicitly requests.
4. **Execute**: Run via `terminal` tool (30-120 seconds typical).
5. **Parse and present**: Summary line ("Found X accounts for 'Y'"), categorized links by platform type, note output file location (`<username>.txt`).

**Pitfalls**:
- No results → check spelling, try wildcards (`user?name`), consider privacy settings
- Timeout → increase `--timeout 120` or limit with `--site`
- Tor → requires Tor daemon; suggest alternative proxy if unavailable
- False positives → cross-reference manually
- Rate limiting → add delays for bulk searches

**Ethical use**: Only search owned/permitted usernames. Respect platform ToS. No harassment/stalking/illegal activities. Consider privacy before sharing results.

**Installation options**: pipx (recommended), pip, Docker, Linux packages (Debian 13+, Ubuntu 22.10+, Homebrew, Kali, BlackArch).

## Verification
- No test scripts in skill directory
- No evals/ directory
- Verify by loading skill and checking SKILL.md loads
- Test: `sherlock --version` then run a known username search

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| (none) | No references/, templates/, or scripts/ directories in this skill |