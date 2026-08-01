---
id: {{entity_id}}
type: {{entity_type}}  # agent | skill | tool | rule | workflow | knowledge | data | memory | output | project | command
namespace: {{namespace}}  # e.g., knowledge/ai-core, knowledge/arbitrage, knowledge/finance
status: scratch  # scratch | research | candidate | canon | deprecated | archived
version: 1.0.0
owner: operator  # operator | agent
created: {{iso_timestamp}}
summary: {{one_line_summary}}
description: |
  {{detailed_description}}
depends_on:
  - {{dependency_id_1}}
  - {{dependency_id_2}}
tags:
  - {{tag_1}}
  - {{tag_2}}
confidence: 0.8
retrieval_class: warm  # hot | warm | cold
export_class: operator  # public | private | operator
---

# {{Entity Title}}

{{Detailed documentation here...}}

## Dependencies

- {{dependency_id_1}} — {{brief description}}
- {{dependency_id_2}} — {{brief description}}

## Related Entities

- {{related_entity_1}} — {{relation type}}
- {{related_entity_2}} — {{relation type}}