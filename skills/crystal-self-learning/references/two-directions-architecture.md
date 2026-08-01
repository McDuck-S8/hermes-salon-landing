# Crystal: Two Complementary Directions

## The Insight

Crystal has TWO directions that complement each other (not alternatives):

1. **Understanding from conversations** - what the user is trying to do
2. **Self-development from external world** - growing capabilities to serve those needs

Direction 1 informs Direction 2: "зачем расти" comes from understanding the user.

## Implementation

### Direction 1: Understanding (conversation_analyzer.py)

Four new analysis methods:

```python
def _analyze_intents(self, messages):
    """What is the user TRYING to accomplish?
    Patterns: earn_money, research, build, setup, fix, optimize, understand, plan
    Returns: sorted by frequency across sessions
    """

def _track_goals(self, messages):
    """What concrete outcomes does the user want?
    Patterns: desired_outcome, explicit_goal, expected_state, planned_path
    Returns: deduplicated goal texts
    """

def _predict_needs(self, messages, intents):
    """What will the user need NEXT based on current trajectory?
    Maps intent types to predicted needs with confidence scores
    Returns: sorted by confidence
    """

def _detect_frustration(self, messages):
    """What is frustrating the user and why?
    Types: stop_talking, anger, system_failure, slow, confusion, low_quality, action_not_talk
    Returns: events list + by_type counts
    """
```

### Direction 2: Self-Development (core.py cycle)

The cycle integrates conversation analysis as Phase 3.5:

```
Phase 1: read_sessions -> signals
Phase 2: detect_patterns -> patterns
Phase 3: analyze_needs -> needs
Phase 3.5: analyze_conversation -> conv_proposals  (NEW)
Phase 4: propose -> proposals (from both error patterns AND conversation)
Phase 5: execute -> assess
Phase 6: evolve
```

Proposals from conversation analysis (user-needs, user-experience departments) PREDOMINATE over error-pattern proposals (ai-core, telegram-bots departments).

### Proposal Generation

```python
# From intents (what user tries to do)
intent_proposals = {
    "earn_money": ("create_feature", 0.9, "Help with earning: "),
    "build": ("create_feature", 0.85, "Create: "),
    "fix": ("fix_problem", 0.9, "Fix: "),
    ...
}

# From frustration (what user is angry about)
if frustration["total"] > 3:
    for t, count in frustration["by_type"].items():
        if count >= 2:
            Proposal(action="fix_problem", priority=0.95)

# From predicted needs (what user will need next)
for pred in predictions:
    if pred["confidence"] > 0.3:
        Proposal(action="create_feature", priority=pred["confidence"])
```

## Confidence Formula

```python
# WRONG: count / 10 (gives 0.1 for count=1)
confidence = min(count / 10, 1.0)

# RIGHT: freq / 50 (uses actual frequency from intent analysis)
freq = next((i["frequency"] for i in intents if i["intent"] == intent), count)
confidence = min(freq / 50, 1.0)
```

## Key Learnings

1. Keyword analysis is shallow - finding keywords does not tell you what the user wants
2. Frustration detection matters - 60x "action_not_talk" tells you the user wants DOING, not TALKING
3. Intent analysis reveals priorities - 25x "earn_money" means the user goal is earning
4. Predictions must use real frequency - the confidence formula must normalize properly
5. Integration is mandatory - standalone analysis commands generate reports nobody reads
