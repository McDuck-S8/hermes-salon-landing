#!/usr/bin/env python3
"""
War Room — Main Orchestrator

Handles /standup and /discuss commands for multi-agent council.
"""

import os
import sys
import json
import subprocess
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# ─── paths ──────────────────────────────────────────────────────────
HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))
SKILL_DIR = HERMES_HOME / "skills" / "devops" / "war-room"
TEMPLATES_DIR = SKILL_DIR / "templates"
REFERENCES_DIR = SKILL_DIR / "references"

# Kill switch check
WARROOM_TEXT_ENABLED = os.environ.get("WARROOM_TEXT_ENABLED", "true").lower() == "true"
WARROOM_VOICE_ENABLED = os.environ.get("WARROOM_VOICE_ENABLED", "false").lower() == "true"


class WarRoom:
    """Orchestrates multi-agent war room sessions."""

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

    def load_prompt_template(self, template_name: str) -> str:
        """Load prompt template from references."""
        template_file = REFERENCES_DIR / "WAR_ROOM_PROMPT_PATTERNS.md"
        if not template_file.exists():
            return ""
        content = template_file.read_text(encoding="utf-8")
        # Extract the relevant template section
        # Simplified: return the whole file for now
        return content

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

    def run_agent(self, agent_name: str, prompt: str) -> Dict[str, Any]:
        """Run a single agent with the given prompt via Claude Code CLI."""
        agent_dir = HERMES_HOME / "agents" / agent_name
        agent_yaml = agent_dir / "agent.yaml"

        # Read agent config
        model = "claude-sonnet-4"
        tools = ["Bash", "Read", "Write", "Edit", "Glob", "Grep", "Task"]
        if agent_yaml.exists():
            import yaml
            config = yaml.safe_load(agent_yaml.read_text(encoding="utf-8"))
            model = config.get("model", model)
            tools = config.get("tools", tools)

        # Run claude CLI
        cmd = [
            "claude",
            "--model", model,
            "--allowedTools", ",".join(tools),
            "--print",
            prompt
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=str(HERMES_HOME),
                capture_output=True,
                text=True,
                timeout=120
            )
            return {
                "agent": agent_name,
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip() if result.stderr else None
            }
        except subprocess.TimeoutExpired:
            return {
                "agent": agent_name,
                "success": False,
                "output": "",
                "error": "Timeout after 120s"
            }
        except Exception as e:
            return {
                "agent": agent_name,
                "success": False,
                "output": "",
                "error": str(e)
            }

    def standup(self) -> Dict[str, Any]:
        """Run /standup — each agent gives status report."""
        if not WARROOM_TEXT_ENABLED:
            return {"error": "WARROOM_TEXT_ENABLED=false"}

        print(f"[WAR ROOM] Starting standup with agents: {self.agents}")
        results = {}

        for agent in self.agents:
            print(f"[WAR ROOM] Running standup for {agent}...")
            prompt = self.build_standup_prompt(agent)
            result = self.run_agent(agent, prompt)
            results[agent] = result

            # Record in transcript
            self.transcript.append({
                "type": "standup",
                "agent": agent,
                "prompt": prompt,
                "response": result,
                "timestamp": datetime.now().isoformat()
            })

            if result["success"]:
                print(f"  [{agent}] {result['output'][:100]}...")
            else:
                print(f"  [{agent}] ERROR: {result['error']}")

        # Save transcript
        self.save_transcript("standup")
        return {"type": "standup", "results": results, "transcript": self.transcript}

    def discuss(self, question: str) -> Dict[str, Any]:
        """Run /discuss <question> — each agent weighs in, then consolidator synthesizes."""
        if not WARROOM_TEXT_ENABLED:
            return {"error": "WARROOM_TEXT_ENABLED=false"}

        print(f"[WAR ROOM] Starting discuss: {question}")
        agent_responses = {}

        # Phase 1: Each agent responds
        for agent in self.agents:
            print(f"[WAR ROOM] Running discuss for {agent}...")
            prompt = self.build_discuss_prompt(agent, question)
            result = self.run_agent(agent, prompt)
            agent_responses[agent] = result

            self.transcript.append({
                "type": "discuss",
                "agent": agent,
                "question": question,
                "prompt": prompt,
                "response": result,
                "timestamp": datetime.now().isoformat()
            })

            if result["success"]:
                print(f"  [{agent}] {result['output'][:100]}...")
            else:
                print(f"  [{agent}] ERROR: {result['error']}")

        # Phase 2: Consolidator synthesizes
        print(f"[WAR ROOM] Running consolidator ({self.consolidator})...")
        successful_responses = {k: v["output"] for k, v in agent_responses.items() if v["success"]}
        if successful_responses:
            prompt = self.build_consolidator_prompt(question, successful_responses)
            consolidator_result = self.run_agent(self.consolidator, prompt)
            agent_responses["consolidator"] = consolidator_result

            self.transcript.append({
                "type": "consolidator",
                "agent": self.consolidator,
                "question": question,
                "prompt": prompt,
                "response": consolidator_result,
                "timestamp": datetime.now().isoformat()
            })

            if consolidator_result["success"]:
                print(f"  [consolidator] {consolidator_result['output'][:10000]}...")
            else:
                print(f"  [consolidator] ERROR: {consolidator_result['error']}")

        # Save transcript
        self.save_transcript("discuss")
        return {"type": "discuss", "question": question, "results": agent_responses, "transcript": self.transcript}

    def save_transcript(self, session_type: str):
        """Save war room transcript to cache."""
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
        print(f"[WAR ROOM] Transcript saved: {transcript_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="War Room — Multi-agent council")
    parser.add_argument("command", choices=["standup", "discuss"], help="Command to run")
    parser.add_argument("--question", help="Question for discuss command")
    parser.add_argument("--agents", help="Comma-separated list of agents")
    parser.add_argument("--consolidator", help="Consolidator agent (default: main)")

    args = parser.parse_args()

    if not WARROOM_TEXT_ENABLED:
        print("War Room disabled: WARROOM_TEXT_ENABLED=false")
        sys.exit(1)

    agents = args.agents.split(",") if args.agents else ["main", "comms", "content", "ops", "research"]

    war_room = WarRoom(agents)
    if args.consolidator:
        war_room.consolidator = args.consolidator

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