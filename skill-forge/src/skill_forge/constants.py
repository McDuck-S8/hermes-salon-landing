"""Shared constants for Skill Forge."""

import re

# Frontmatter pattern: file must start with ---\n...\n---\n
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Valid semver: N.N.N
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
