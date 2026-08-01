# Python `diagrams` Library — PNG Architecture Diagrams

Alternative to SVG/HTML and Mermaid approaches. Produces standalone PNGs via Python.

## Setup (Windows)

```bash
pip install diagrams
choco install graphviz
export PATH="$PATH:/d/Program Files/Graphviz/bin"
```

## Basic Pattern

```python
from diagrams import Diagram, Edge
from diagrams.onprem.client import User
from diagrams.programming.language import Python

with Diagram("System", show=False, direction="LR",
             filename="output/arch", outformat="png"):
    user = User("User")
    agent = Python("Agent")
    user >> agent
```

## When To Use vs Mermaid vs SVG

| Need | Tool |
|---|---|
| Self-contained HTML, dark theme | `architecture-diagram` (SVG/HTML) |
| PNG for docs/embedding | `diagrams` (mingrammer) |
| Inline in markdown, simple flows | `diagram-maker` (Mermaid) |
| Hand-drawn sketches | `excalidraw` |

## Pitfalls

- Only built-in icons available. Use `Server`/`Client`/`Blank` for unsupported services
- Graphviz `dot.exe` must be in PATH on Windows
- Too granular for deep file maps — emit as Mermaid mindmap instead
- Generate separate files per C4 level (the library has no multi-level concept)