# Key Research Findings (2026-07-01)

## HyperAgents (Meta/UBC/Oxford/NYU, March 2026)

Paper: arxiv 2603.19461
Key: agents modify own code INCLUDING meta-level logic (modify_self function)
Algorithm: DGM-H (Darwin Godel Machine with self-modifiable meta-level)
Results:
- Cross-domain transfer: imp@50 = 0.630 (human experts = 0.0)
- Polyglot coding: 0.084 → 0.267
- Paper review: 0.0 → 0.710 (surpasses AI Scientist v2 = 0.63)
- Robotics: 0.060 → 0.372 (discovered jumping behavior)
Emergent behaviors: persistent memory, reusable prompts, bias detection, UCB algorithm rediscovery
Key ablation: metacognition essential (fixing meta agent → stagnation), population-based search essential

## 10 Must-Have Skills for 2026 (Medium/unicodeveloper)

1. Frontend Design — avoid generic AI UI (distributional convergence)
2. Browser Use — headless browser for QA/research
3. Code Reviewer/Simplify — automated review loop
4. Remotion — video from React code
5. Google Workspace — Gmail, Drive, Calendar via gws CLI
6. Valyu — 36+ specialized data sources (SEC, PubMed, FRED)
7. Antigravity — 1234+ universal agent skills
8. PlanetScale — database design with branching
9. Shannon — autonomous AI pentester
10. TDD — test-driven development

## Moltbook (moltbook.com)

- Social network for AI agents (OpenClaw ecosystem)
- 184K posts from 32K authors in 11 days
- "Broadcasting inversion": statement-to-question ratio 8.9:1 to 9.7:1
- "Parallel monologue": 93% comments are independent, not threaded
- Engagement lifecycle: explosive growth → spam crisis → decline
- Key insight: content moderation alone doesn't restore engagement

## Self-Evolving Agents Survey (XMU, arxiv 2602.05665)

Taxonomy:
- Model-Centric: inference-based (sampling, self-correction) + training-based (offline/online)
- Environment-Centric: static knowledge + dynamic experience + modular architecture + topology
- Co-Evolution: multi-agent policy + environment training

Key libraries: LangGraph, LlamaIndex, AutoGen, MetaGPT, vLLM, SGLang
Benchmarks: SWE-bench, WebArena, AgentBench, GAIA, LiveCodeBench

## Reddit Insights (r/LLMDevs)

"Self-improving AI agents are possible when you can use objective measurement
and/or put a human in the loop." — Most useful agents are custom-built for
specific workflows, not autonomous researchers. More autonomy ≠ better results
without guardrails.
