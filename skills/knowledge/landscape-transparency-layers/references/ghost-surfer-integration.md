# Ghost-Surfer → Landscape + Transparency Layers Integration

## How Ghost-Surfer Feeds the Knowledge Architecture

| Ghost-Surfer Output | Landscape Layer | Transparency Layer | Example |
|---------------------|-----------------|-------------------|---------|
| **Service status** (Fal.ai loaded, Leonardo blocked) | — | **Situation** (Layer 1) | `type: situation, name: "Fal.ai доступность", current_state: "works", risk_level: "low", confidence: 0.9` |
| **Registration success/fail** per platform | — | **Situation** (Layer 1) | `type: situation, name: "YouTube регистрация", current_state: "verified", risk_level: "none", confidence: 0.95` |
| **Connection arrows with real ROI** (tested posting) | — | **Plans** (Layer 2) | `type: plans, name: "Fal.ai -> YouTube Shorts", arrows: [{from: "Fal.ai", to: "YouTube", prob: 0.9, expected_roi: 2.1}]` |
| **Creative/account gaps** (no avatar, no phone, CAPTCHA blocked) | — | **Logistics** (Layer 3) | `type: logistics, name: "Аватар для Алисы", status: "critical_gap", required_for: ["YouTube", "TikTok"]` |
| **Proxy/identity health** (ban score, fingerprint quality) | **Landscape** (Layer 0) | — | `type: landscape, name: "Антидетект: ротация отпечатков", essence: "Уникальные Canvas/WebGL/Navigator на аккаунт", confidence: 0.95` |
| **Platform-specific mechanics** (Shorts algorithm, TikTok limits) | **Landscape** (Layer 0) | — | `type: landscape, name: "YouTube Shorts алгоритм", essence: "Продвигает удерживающий вертикальный контент <60с", confidence: 0.9` |

## Live Integration (Operation "First Account")

### Situation Layer Updates (Real-time)
```python
# From ghost-surfer health checks
landscape.add_situation(
    name="Fal.ai status",
    overlay_on=["traffic:ai-generation", "content:images"],
    current_state="works",
    confidence=0.9
)

landscape.add_situation(
    name="Leonardo AI status",
    overlay_on=["traffic:ai-generation", "content:images"],
    current_state="blocked_network",
    risk_level="high",
    confidence=0.8
)

landscape.add_situation(
    name="Bing Image Creator status",
    overlay_on=["traffic:ai-generation", "content:images"],
    current_state="works",
    confidence=0.9
)
```

### Plans Layer (From Successful Postings)
```python
# After testing Fal.ai generation -> YouTube Shorts upload
landscape.add_plan(
    name="Fal.ai generation -> YouTube Shorts posting",
    overlay_on=["traffic:ai-generation", "platform:youtube"],
    arrows=[
        {"from": "Fal.ai", "to": "YouTube Shorts", "prob": 0.85, "expected_roi": 2.3}
    ],
    confidence=0.7
)
```

### Logistics Layer (From Registration Gaps)
```python
# From Operation "First Account" blockers
landscape.add_logistics(
    name="mail.ru app password for IMAP",
    overlay_on=["accounts:email_verification"],
    status="critical_gap",
    required_for=["Fal.ai", "Bing", "YouTube", "TikTok"],
    confidence=0.95
)

landscape.add_logistics(
    name="2captcha API key for CAPTCHA",
    overlay_on=["accounts:registration"],
    status="critical_gap",
    required_for=["Leonardo", "RunwayML", "TikTok"],
    confidence=0.95
)

landscape.add_logistics(
    name="5sim SMS API for phone verification",
    overlay_on=["accounts:phone_verification"],
    status="critical_gap",
    required_for=["YouTube", "TikTok", "VK"],
    confidence=0.9
)

landscape.add_logistics(
    name="V2RayN proxy for IP rotation",
    overlay_on=["accounts:identity_rotation"],
    status="pending_config",
    required_for=["All platforms"],
    confidence=0.8
)
```

## Fractal Wheel Integration

### Mode 1 (Analysis) → Reads Landscape
```python
# Fundamental aspects from Landscape layer
wheel = FractalWheel(center="AI OFM Pipeline", domain="ai-ofm")
# Landscape provides: Traffic, Content, Monetization, Compliance, Team, Legal, Scale, Platforms
```

### Mode 2 (Synthesis) → Reads Situation + Plans
```python
# Real service status + tested connections -> new hypotheses
synthesis = wheel.run_synthesis_mode(days=7)
# Finds: "Fal.ai works + YouTube works -> Fal.ai->YouTube pipeline viable"
```

### Mode 3 (Euler) → Finds Golden Sections
```python
# Situation (Fal.ai🟢, Leonardo🔴, YouTube🟢) + Plans (Fal.ai->YouTube🟢)
# Euler detects: 
# 🟢 GREEN: Fal.ai ∩ YouTube = ready pipeline
# 🔴 RED: Leonardo ∩ Creative = blocked
# 🟡🔴 CONFLICT: Traffic (Fal.ai🟢) ∩ Creative (Leonardo🔴) = wasted capacity
```

### Key Strength → Identity Repertoire
```python
# KeyStrengthEstimator evaluates "Ghost-Surfer Identity Pipeline" key
# Viability: 0.85 (demand for automated identities)
# Cohesion: 0.75 (some red blockers: CAPTCHA, SMS, IMAP)
# Growth: 0.9 (scales to 100s of identities)
# Key Strength = 0.85*0.4 + 0.75*0.3 + 0.9*0.3 = 0.835
```

## Automation

### Cron Jobs (Ghost-Surfer → Landscape)
```bash
# Daily: Service health -> Situation layer
ghost-surfer health-check --all --output=situation_layer

# Weekly: Posting results -> Plans layer (ROI updates)
ghost-surfer analyze-roi --last=7d --output=plans_layer

# On registration: Gap detection -> Logistics layer
ghost-surfer register --identity=X --platform=Y --log-gaps=logistics_layer
```

### Knowledge Cube Writers
```python
# In ghost-surfer health-check
kc.write_entry(
    layer="situation",
    name=f"{platform} status",
    overlay_on=["traffic:source", "content:type"],
    current_state=state,
    risk_level=risk,
    confidence=0.9
)

# In posting orchestrator
kc.write_entry(
    layer="plans",
    name=f"{source} -> {platform}",
    overlay_on=["traffic:source", "platform:name"],
    arrows=[{"from": source, "to": platform, "prob": p, "expected_roi": roi}],
    confidence=0.7
)

# In registration
kc.write_entry(
    layer="logistics",
    name=f"Gap: {gap_name}",
    overlay_on=[f"accounts:{stage}"],
    status="critical_gap",
    required_for=[platform1, platform2],
    confidence=0.95
)
```

## Files
- `references/operation-first-account.md` — Full trace of first identity creation and service tests
- `scripts/landscape_layers.py` — Implementation (to be created)

---
*Generated from Operation "First Account" (2026-07-16)*