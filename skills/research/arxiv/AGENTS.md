# arxiv — Skill Contract

## Purpose
No description provided

## Ownership
Hermes Agent — self-maintained via skill-forge. Category: general.

## Local Contracts
### Triggers
- When the task matches the skill's domain and purpose

### Required Tools
- bash
- web_extract
- python
- curl

### Configuration
- Standard skill configuration via SKILL.md frontmatter

## Work Guidance
### When to Use
- Tasks requiring this skill's domain expertise

### Common Patterns
- ```
curl -s "https://export.arxiv.org/api/query?search_query=all:GRPO+reinforcement+learning&max_results=5"
...```
- ```
curl -s "https://export.arxiv.org/api/query?search_query=all:GRPO+reinforcement+learning&max_results=5&sortBy=submit
- ```
# Latest 10 papers in cs.AI
...```
- **Discover**: `python scripts/search_arxiv.py "your topic" --sort date --max 10`
- **Assess impact**: `curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:ID?fields=citationCount,influentialCit
- **Read abstract**: `web_extract(urls=["https://arxiv.org/abs/ID"])`

### Integration Points
- the
- s
- ful

## Verification
- 10 papers in cs.AI
- the summary before treating a result as a valid paper
- Verification table present in SKILL.md

## Child DOX Index
- **scripts/** — 1 files: search_arxiv.py

---
*Generated: 2026-07-28 17:31*
*Source: SKILL.md frontmatter + content analysis*
