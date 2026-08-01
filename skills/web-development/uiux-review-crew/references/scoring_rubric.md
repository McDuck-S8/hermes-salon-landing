# UI/UX Scoring Rubric (0-10 per dimension)

## Layout & Hierarchy (25%)
| Score | Criteria |
|-------|----------|
| 10 | Perfect F/Z-pattern, hero > fold, crystal clear hierarchy, grid-aligned |
| 8-9 | Good hierarchy, minor alignment issues, hero mostly above fold |
| 6-7 | Confusing flow, weak hero, some grid breaks |
| 4-5 | No clear pattern, hero buried, major alignment chaos |
| 1-3 | Random layout, no hierarchy, content buried |

## Typography (15%)
| Score | Criteria |
|-------|----------|
| 10 | Modern pairing, H1≥48px, H2≥32px, Body≥16px/1.6, perfect contrast |
| 8-9 | Good pairing, minor size/line-height issues, readable |
| 6-7 | Decent but inconsistent, body <16px or tight leading |
| 4-5 | Poor pairing, small text, low contrast, hard to scan |
| 1-3 | Unreadable, decorative fonts for body, no hierarchy |

## Color & Contrast (20%)
| Score | Criteria |
|-------|----------|
| 10 | Brand-consistent, WCAG AAA (7:1), harmony, psychology aligned |
| 8-9 | WCAG AA (4.5:1), good harmony, minor contrast slips |
| 6-7 | AA mostly, some text fails, muddy palette |
| 4-5 | Multiple AA fails, clashing colors, no psychology |
| 1-3 | Inaccessible, random colors, strain to read |

## CTA Effectiveness (20%) — CRITICAL
| Score | Criteria |
|-------|----------|
| 10 | Obvious above fold, high contrast, action copy, large touch target, clear hierarchy |
| 8-9 | Visible, good copy, minor size/placement tweak needed |
| 6-7 | Exists but weak: low contrast, vague copy, below fold, small |
| 4-5 | Hard to find, ghost button as primary, passive copy |
| 1-3 | No CTA, or completely invisible/broken |

## Whitespace & Balance (10%)
| Score | Criteria |
|-------|----------|
| 10 | Generous breathing room, balanced visual weight, consistent spacing scale |
| 8-9 | Good balance, minor cramped sections |
| 6-7 | Uneven, some crowded areas, inconsistent spacing |
| 4-5 | Cluttered, no rhythm, elements touching |
| 1-3 | Wall of content, no whitespace |

## Content & Trust (10%)
| Score | Criteria |
|-------|----------|
| 10 | Clear value prop, strong social proof, trust badges, guarantees, easy contact |
| 8-9 | Good content, trust signals present but could be stronger |
| 6-7 | Basic info, weak/no social proof, contact buried |
| 4-5 | Vague value, no trust signals, hard to contact |
| 1-3 | No value prop, anonymous, no contact info |

---

## Automatic FAIL Conditions (score capped at 60)
- [ ] Any text contrast < 4.5:1 (WCAG AA fail)
- [ ] No visible primary CTA above fold
- [ ] H1 < 32px or illegible
- [ ] Body text < 16px OR line-height < 1.5
- [ ] Major grid/alignment chaos
- [ ] Zero trust signals (reviews, logos, guarantees, contact)

---

## Weight Summary
| Dimension | Weight |
|-----------|--------|
| Layout & Hierarchy | 25% |
| Color & Contrast | 20% |
| CTA Effectiveness | 20% |
| Typography | 15% |
| Whitespace & Balance | 10% |
| Content & Trust | 10% |
| **Total** | **100%** |

---

## Composite Score Formula
```
composite = sum(dimension_score * weight for each dimension) * 10
# Results in 0-100 scale
# e.g., (8*0.25 + 9*0.15 + 7*0.20 + 9*0.20 + 8*0.10 + 9*0.10) * 10 = 82.5
```

## Thresholds
| Threshold | Meaning |
|-----------|---------|
| ≥ 85 | ✅ PASS — Publication allowed |
| 70-84 | ⚠️ REVIEW — Fix critical issues first |
| < 70 | ❌ FAIL — Major redesign needed |