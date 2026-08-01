# Spec: Arbitrage Execution Skill

## Requirements
- Full-cycle arbitrage: find gaps → match traffic → launch → withdraw
- Skill-first architecture: SKILL.md (brief) + SKILL_FULL.md (lazy load)
- Git repo structure: scripts/, data/, history/, .github/workflows/
- CI validation on every push

## Acceptance Criteria
- [ ] find_gaps.py returns valid JSON with ROI > 30%
- [ ] launch_scheme.py creates scheme_id, tracks metrics
- [ ] monitor_scheme.py checks kill switches
- [ ] withdraw.py executes USDT → Binance P2P → Tbank card
- [ ] All scripts pass pytest validation
- [ ] SKILL.md frontmatter valid YAML
- [ ] CI workflow runs on push

## Technical Details
- Data sources: Mock CPA offers (replace with real API)
- Traffic costs: Per-geo, per-platform estimates
- Bayesian scoring integration for gap validation
- Finance Core logging for all spends/revenues

## Dependencies
- finance-core (P&L, tax, withdrawals)
- forge-dynamic-tools (code gen for new schemes)
- session-recall (pattern learning)