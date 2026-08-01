#!/usr/bin/env python3
"""
War Room — Test Runner (Mock Mode)

Runs war room with mock agent responses for testing without Claude CLI.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))


class MockWarRoom:
    """Mock war room for testing prompt templates and flow."""

    def __init__(self, agents: List[str] = None):
        self.agents = agents or ["main", "comms", "content", "ops", "research"]
        self.consolidator = "main"
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.transcript = []

    def load_agent_persona(self, agent_name: str) -> str:
        """Load agent's CLAUDE.md persona."""
        agent_dir = HERMES_HOME / "agents" / agent_name
        claude_md = agent_dir / "CLAUDE.md"
        if claude_md.exists():
            return claude_md.read_text(encoding="utf-8")
        return f"Agent {agent_name} - no persona file found."

    def build_standup_prompt(self, agent_name: str) -> str:
        """Build standup prompt for an agent."""
        persona = self.load_agent_persona(agent_name)
        return f"""{persona}

QUICK STANDUP STATUS — 2-3 sentences MAX.

Cover:
1. What you wrapped (completed) since last standup
2. What's queued (in progress / planned)
3. Any blockers (what you need help with)

Be concise. No fluff. Other agents are waiting."""

    def build_discuss_prompt(self, agent_name: str, question: str) -> str:
        """Build discuss prompt for an agent."""
        persona = self.load_agent_persona(agent_name)
        return f"""{persona}

The user just asked: "{question}"

From YOUR perspective and based on what YOU have access to (your skills, memory, tools, persona), give your take in 3-5 sentences.

Do NOT speak for other agents. Do NOT hedge. Give YOUR angle."""

    def build_consolidator_prompt(self, question: str, agent_responses: Dict[str, str]) -> str:
        """Build consolidator prompt."""
        responses_text = "\n".join([f"- {agent}: {response}" for agent, response in agent_responses.items()])
        persona = self.load_agent_persona(self.consolidator)
        return f"""{persona}

The user asked: "{question}"

Below are the responses from each agent. Your job: synthesize a clear recommendation.

AGENT RESPONSES:
{responses_text}

Provide:
1. **Consensus** — where agents agree
2. **Divergence** — where they differ (and why)
3. **Recommendation** — what should happen next, with reasoning
4. **Action Items** — concrete next steps, assigned to agents if applicable

Be decisive. The user needs a decision, not a summary."""

    def mock_agent_response(self, agent_name: str, prompt: str) -> str:
        """Generate mock response based on agent persona."""
        mock_responses = {
            "main": {
                "standup": "[Main] ✓ Wrapped: Test Harness skill creation, War Room skill creation. Queued: Three-Layer Memory integration, Kill Switches. Blockers: None.",
                "discuss": "[Main] As coordinator, I see this enables the Playbook's three-layer memory pattern. All agents see value. Ops concern about migration is valid but solvable. Recommendation: proceed with conditions."
            },
            "comms": {
                "standup": "[Comms] ✓ Wrapped: Telegram bridge stability fixes, proxy_intermittent skill updated. Queued: Voice notes inbound, exfiltration guard. Blockers: Telegram API rate limits on free tier.",
                "discuss": "[Comms] LanceDB improves /search and auto-recall for user queries. Better semantic search = fewer 'I already told you this' frustrations. Low risk, high user value. Migration must not break live /search."
            },
            "content": {
                "standup": "[Content] ✓ Wrapped: Content pipeline templates, repurposing workflows. Queued: Semantic similarity for content repurposing, analytics dashboard. Blockers: Need vector search (LanceDB) for similarity matching.",
                "discuss": "[Content] Three-layer memory IS the Playbook pattern (p.148). LanceDB IS the vector layer. Without it, content repurposing stays manual. This is the force multiplier for content velocity. Strong yes."
            },
            "ops": {
                "standup": "[Ops] ✓ Wrapped: Procedural executor Test Harness integration, cron health monitoring. Queued: Kill switches, LanceDB migration script, cost tracking. Blockers: Migration script needs Test Harness verification.",
                "discuss": "[Ops] LanceDB is file-based, ~50MB, no external deps — fits our architecture. Only risk: migrating 10K+ KC entries. Need: (1) migration script with Test Harness, (2) rollback plan, (3) behind KC_LANCE_ENABLED kill switch. Conditions met = green light."
            },
            "research": {
                "standup": "[Research] ✓ Wrapped: AI-First Playbook analysis, content-studio repo review, EverOS architecture study. Queued: LanceDB vs pgvector benchmark, Gemini Flash for cheap classification. Blockers: Need cheap embedding API for Tier 3 memory.",
                "discuss": "[Research] External evidence: LanceDB is emerging standard for local vector search (5.2K stars, active). Beats pgvector for file-based arch (no Postgres). Beats Chroma (lighter, no server). For our architecture, LanceDB is correct choice."
            }
        }

        if "STANDUP" in prompt.upper() or "standup" in prompt.lower():
            return mock_responses.get(agent_name, {}).get("standup", f"[{agent_name}] Mock standup response")
        else:
            return mock_responses.get(agent_name, {}).get("discuss", f"[{agent_name}] Mock discuss response")

    def standup(self) -> Dict[str, Any]:
        """Run mock /standup."""
        print(f"[WAR ROOM MOCK] Starting standup with agents: {self.agents}")
        results = {}

        for agent in self.agents:
            print(f"[WAR ROOM MOCK] Running standup for {agent}...")
            prompt = self.build_standup_prompt(agent)
            response = self.mock_agent_response(agent, prompt)
            results[agent] = {"success": True, "output": response, "error": None}

            self.transcript.append({
                "type": "standup",
                "agent": agent,
                "prompt": prompt,
                "response": results[agent],
                "timestamp": datetime.now().isoformat()
            })
            print(f"  [{agent}] {response[:80]}...")

        self.save_transcript("standup")
        return {"type": "standup", "results": results, "transcript": self.transcript}

    def discuss(self, question: str) -> Dict[str, Any]:
        """Run mock /discuss <question>."""
        print(f"[WAR ROOM MOCK] Starting discuss: {question}")
        agent_responses = {}

        # Phase 1: Each agent responds
        for agent in self.agents:
            print(f"[WAR ROOM MOCK] Running discuss for {agent}...")
            prompt = self.build_discuss_prompt(agent, question)
            response = self.mock_agent_response(agent, prompt)
            agent_responses[agent] = {"success": True, "output": response, "error": None}

            self.transcript.append({
                "type": "discuss",
                "agent": agent,
                "question": question,
                "prompt": prompt,
                "response": agent_responses[agent],
                "timestamp": datetime.now().isoformat()
            })
            print(f"  [{agent}] {response[:80]}...")

        # Phase 2: Consolidator
        print(f"[WAR ROOM MOCK] Running consolidator ({self.consolidator})...")
        successful = {k: v["output"] for k, v in agent_responses.items() if v["success"]}
        prompt = self.build_consolidator_prompt(question, successful)
        consolidator_response = self.mock_agent_response(self.consolidator, prompt)
        agent_responses["consolidator"] = {"success": True, "output": consolidator_response, "error": None}

        self.transcript.append({
            "type": "consolidator",
            "agent": self.consolidator,
            "question": question,
            "prompt": prompt,
            "response": agent_responses["consolidator"],
            "timestamp": datetime.now().isoformat()
        })
        print(f"  [consolidator] {consolidator_response[:100]}...")

        self.save_transcript("discuss")
        return {"type": "discuss", "question": question, "results": agent_responses, "transcript": self.transcript}

    def save_transcript(self, session_type: str):
        """Save transcript to cache."""
        cache_dir = HERMES_HOME / "cache" / "war_room"
        cache_dir.mkdir(parents=True, exist_ok=True)
        transcript_file = cache_dir / f"{session_type}_{self.session_id}.json"
        transcript_file.write_text(
            json.dumps({
                "session_id": self.session_id,
                "type": session_type,
                "agents": self.agents,
                "consolidator": self.consolidator,
                "transcript": self.transcript
            }, indent=2, default=str),
            encoding="utf-8"
        )
        print(f"[WAR ROOM MOCK] Transcript saved: {transcript_file}")


def main():
    parser = argparse.ArgumentParser(description="War Room Mock — Test prompt templates and flow")
    parser.add_argument("command", choices=["standup", "discuss"], help="Command to run")
    parser.add_argument("--question", help="Question for discuss command")
    parser.add_argument("--agents", help="Comma-separated list of agents")

    args = parser.parse_args()

    agents = args.agents.split(",") if args.agents else ["main", "comms", "content", "ops", "research"]
    war_room = MockWarRoom(agents)

    if args.command == "standup":
        result = war_room.standup()
    elif args.command == "discuss":
        if not args.question:
            print("Error: --question required for discuss")
            sys.exit(1)
        result = war_room.discuss(args.question)

    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()