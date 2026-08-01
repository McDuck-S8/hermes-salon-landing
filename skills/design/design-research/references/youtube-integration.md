# YouTube Integration for Design Research

## Overview
YouTube is a critical source for design trends, especially for:
- UI/UX walkthroughs
- Design system deep-dives
- Component library reviews
- Live coding sessions showing implementation
- Agency portfolio reviews

## YouTube Research Pipeline (via video-learner + youtube-research)

### 1. Channel Curation
Maintain a curated list of high-signal design channels:

| Channel | Focus | Signal |
|---------|-------|--------|
| DesignCourse | Full-stack design + code | High |
| WebDevSimplified | Modern CSS/JS patterns | High |
| Kevin Powell | CSS deep-dives | Very High |
| Fireship | Quick tech overviews | Medium |
| Traversy Media | Project-based tutorials | High |
| Design+Code | Design systems, SwiftUI | High |
| Caler Edwards | UI design process | High |
| Design with Arash | Figma, UI kits | Medium |
| Jesse Showalter | Design systems, careers | Medium |

### 2. Search Queries for Design Trends
```python
DESIGN_QUERIES = [
    "glassmorphism UI design 2024",
    "dark mode design system",
    "CSS container queries tutorial",
    "variable fonts web design",
    "micro-interactions CSS",
    "design system components Figma",
    "accessibility design patterns",
    "mobile-first responsive design 2024",
    "tailwindcss design patterns",
    "framer motion animations",
    "shadcn/ui component library",
    "radix ui primitives"
]
```

### 3. Extraction Strategy (via video-learner)
```python
# For each video found:
1. Get metadata via oembed (fast, works through proxy)
2. If high-signal channel → attempt full extraction
3. Extract concepts: design patterns, color schemes, component APIs, CSS techniques
4. Adapt via PatternAdapter (translate to local context)
5. Store in Tactical Buffer with tags: {design, trend, component, technique}
```

### 4. Fallback Chain (from youtube-research learning)
```
oembed (SOCKS5) → WORKS for metadata
  ↓ (if need full content)
yt-dlp with proxy → BLOCKED (429, PO Token)
  ↓ 
Invidious instances → UNRELIABLE (timeouts, 429)
  ↓
Manual/browser session → WORKS but slow
```

**Lesson**: For design research, oembed metadata (title + channel) is often enough to identify the trend. Queue high-value videos for manual deep extraction later.

### 5. Tactical Buffer Integration
```python
# When design trend detected from YouTube:
tb.add(
    param=f"design_trend_{video_id}_{topic}",
    value={
        "topic": topic,
        "source": "youtube",
        "video_id": video_id,
        "channel": channel,
        "title": title,
        "confidence": 0.4,
        "tags": ["design", "trend", topic_category]
    }
)

# After 3+ occurrences across sources → promote to Strategic DB
```

### 6. Cross-Reference with Other Sources
- Awwwards/SiteInspire → visual patterns
- GitHub → implementation code
- YouTube → implementation walkthroughs
- Blogs → rationale/context

**Pattern**: When same trend appears in 2+ sources → confidence boost to 0.7+

## Commands
```bash
# Collect design references (includes YouTube via video-learner)
python scripts/design_reference_collector.py collect

# Generate skills from detected patterns
python scripts/design_skill_generator.py generate

# Write generated skills
python scripts/design_skill_generator.py write
```

## Related Skills
- `video-learner` — core video processing
- `youtube-research` — deep YouTube mining
- `design-adaptation` — translate patterns to local context
- `design-code-generator` — generate components from patterns
- `design-critic` — evaluate against trends