---
id: {{ENTITY_ID}}
type: {{TYPE}}  # command | agent | skill | rule | workflow | tool | knowledge | data | memory | output | project
namespace: {{NAMESPACE}}  # e.g., knowledge/ai-core, knowledge/arbitrage, knowledge/telegram-bots
status: {{STATUS}}  # scratch | research | candidate | canon | deprecated | archived
version: 1.0.0
owner: {{OWNER}}  # operator | agent
created: {{CREATED_ISO8601}}  # e.g., 2026-06-29T00:00:00Z
summary: {{ONE_LINE_SUMMARY}}
description: |
  {{DETAILED_DESCRIPTION_MULTILINE}}
  
  Can span multiple lines. YAML literal block scalar (|) preserves newlines.
depends_on:
  - {{DEPENDENCY_ID_1}}
  - {{DEPENDENCY_ID_2}}
tags:
  - {{TAG_1}}
  - {{TAG_2}}
confidence: {{0.0_TO_1.0}}  # e.g., 0.95
retrieval_class: {{hot|warm|cold}}  # hot = frequently accessed, warm = occasionally, cold = archive
export_class: {{public|private|operator}}  # public = shareable, private = internal, operator = sensitive
promotes_from: []  # for candidate: source synthesis node IDs
promotes_to: []    # for support/synthesis: target canon node IDs
---

# {{ENTITY_TITLE}}

## Overview

{{HIGH_LEVEL_DESCRIPTION}}

## Key Features

- {{FEATURE_1}}
- {{FEATURE_2}}
- {{FEATURE_3}}

## Integration

{{HOW_THIS_INTEGRATES_WITH_HERMES}}

## Related Entities

- [[{{RELATED_ENTITY_1}}]] — {{RELATION}}
- [[{{RELATED_ENTITY_2}}]] — {{RELATION}}

## Configuration

{{CONFIGURATION_DETAILS_IF_ANY}}

## Lifecycle Notes

{{STATUS_SPECIFIC_NOTES}}

---

**Template Usage:**
1. Copy this file to appropriate directory: `entities/{{TYPE}}s/{{ENTITY_ID}}.md`
2. Replace all `{{PLACEHOLDERS}}` with actual values
3. Ensure `status` matches lifecycle stage:
   - `scratch` — new, experimental, unvalidated
   - `research` — validated, worth refining
   - `candidate` — nominated for canon (requires `promotes_from`)
   - `canon` — operator-approved (requires `owner: operator`)
   - `deprecated` — superseded, not for new use
   - `archived` — historical reference
4. Run validation: `python scripts/ibos_entity_sensor.py validate`