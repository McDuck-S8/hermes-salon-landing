# 1password — Skill

## Purpose
Set up and use 1Password CLI (op) for secrets management. Install CLI, enable desktop app integration, sign in, and read/inject secrets for commands.

## Ownership
Managed by Hermes Agent. Located in `security/1password/`.

## Local Contracts
- **Triggers**: Installing/configure 1Password CLI, signing in with `op signin`, reading secret references (`op://Vault/Item/field`), injecting secrets into config/templates via `op inject`, running commands with secret env vars via `op run`
- **Required tools**: `terminal` (for op CLI commands), `read_file`, `write_file` (for .env, configs)
- **Config**: Skill setup prompts for `OP_SERVICE_ACCOUNT_TOKEN` (stored in `~/.hermes/.env`). Desktop app integration requires `tmux` for stable sessions.
- **Related skills**: (none listed in SKILL.md)

## Work Guidance
**When to use**: Managing secrets through 1Password instead of plaintext env vars/files. Installing/configure CLI, signing in, reading secrets, injecting into templates, running commands with injected env vars.

**Authentication methods**:
1. **Service Account** (recommended for Hermes): Set `OP_SERVICE_ACCOUNT_TOKEN` in `~/.hermes/.env`. No desktop app needed. Supports `op read`, `op inject`, `op run`.
2. **Desktop App Integration** (interactive): Enable in 1Password app → Settings → Developer → Integrate with CLI. Requires `tmux` for stable auth across Hermes terminal calls.
3. **Connect Server** (self-hosted): Set `OP_CONNECT_HOST` and `OP_CONNECT_TOKEN`.

**Hermes execution pattern (desktop app)**: Use dedicated `tmux` session for `op signin` and subsequent commands since Hermes terminal calls are non-interactive and lose auth context. NOT needed with service account token.

**Common operations**:
- Read secret: `op read "op://Vault/Item/field"`
- Get OTP: `op read "op://Vault/Item/one-time password?attribute=otp"`
- Inject into template: `echo "db_password: {{ op://Vault/Item/field }}" | op inject`
- Run with secret env: `export VAR="op://Vault/Item/field" && op run -- sh -c 'echo $VAR'`

**Guardrails**: Never print raw secrets unless user explicitly asks. Prefer `op run`/`op inject` over writing secrets to files. If "account not signed in" → re-run `op signin` in same tmux session. Headless/CI → use service account token (requires CLI v2.18+).

## Verification
- No test scripts in skill directory
- No evals/ directory
- Verify by loading skill and checking SKILL.md loads
- Test with: `op --version` then `op whoami` after auth setup

## Child DOX Index
| File/Dir | Purpose |
|----------|---------|
| `references/get-started.md` | Installation and getting started guide |
| `references/cli-examples.md` | CLI usage examples |