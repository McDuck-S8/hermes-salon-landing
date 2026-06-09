# AGENTS.md — config/

## Purpose

Configuration files and domain definitions for the Hermes system. Controls behavior of cron jobs, agent profiles, and domain-specific settings.

## Ownership

Core module — modified by user and system scripts. Sensitive — changes affect runtime behavior.

## Files

| File | Purpose |
|---|---|
| `domain_definitions.yaml` | Domain-specific configuration and categorization rules |
| `backups/` | Backup copies of configuration files |

## Local Contracts

- **Format**: YAML for structured config, Markdown for documentation.
- **Sensitivity**: Changes to config files can break cron jobs and agent behavior. Always verify after editing.
- **Backups**: Before modifying any config file, check if `backups/` has a recent copy.

## Work Guidance

- Read `domain_definitions.yaml` before modifying domain-related scripts in `scripts/`.
- When adding new domains or categories, update both the config and relevant Knowledge Cube entries.
- Test cron jobs after changing schedule-related configuration.
- Prefer `scripts/` for programmatic config changes over manual YAML edits.

## Verification

- Validate YAML syntax before saving (python -c "import yaml; yaml.safe_load(open('file'))").
- Verify changes don't break existing cron job definitions in `cron/jobs.json`.

## Child DOX Index

| Directory | Purpose |
|---|---|
| `backups/` | Backup copies of configuration files before modifications |
