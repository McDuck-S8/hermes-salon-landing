# Telegram Post Content Quality Standards

## What BAD AI posts look like (from real channel audit)

Every post in the user's channels had these problems:

### 1. Reasoning leakage
Posts started with "Thought for 2 seconds" followed by the model's internal reasoning:
```
Thought for 2 seconds  Мы видим запрос на пост про промпт-инженерию на практике...
```
This is the CoT (chain-of-thought) leaking into published content.

**Root cause:** The model's reasoning output was not stripped before sending to Telegram API.

### 2. Repetitive content
Same "кулинарные метафоры" (culinary metaphors) theme posted 8+ times. The model kept writing "Мы уже готовили такие посты" (we already made similar posts) and then making another one.

### 3. No variety across channels
4 channels with different purposes got essentially the same content style and topics.

## Quality rules for Telegram posts

1. **NEVER publish reasoning/thinking output.** Strip all "Thought for..." prefixes. The post text should start with the actual content.

2. **No repetition.** Before posting, check recent posts in the channel. If a similar topic was covered, pick a different one.

3. **Match channel identity:**
   - @neuro_kitchen_ai — practical recipes, how-tos, templates (culinary metaphor OK but not mandatory)
   - @max_brain_chef_official — system announcements, architecture, capabilities
   - @ai_frontier_you — philosophical, analytical, frontier-thinking
   - @max_brain_chef_ai — practical AI tips, mistakes, workflow optimization

4. **Structure:** Hook → Content → Takeaway. No filler. No "в мире AI много нового" openers.

5. **Verify facts.** Don't invent news. Write analysis, opinions, frameworks — things that don't require date-specific accuracy.

6. **Hashtags at the end.** 3-5 relevant tags. Not more.

## Good post anatomy

```
⚡️ Hook title (emoji + short)

First paragraph: bold claim or question. No preamble.

Body: 3-5 short paragraphs. Each with a concrete point.
Use numbers, examples, comparisons.

Takeaway: one memorable line.

#tag1 #tag2 #tag3
```
