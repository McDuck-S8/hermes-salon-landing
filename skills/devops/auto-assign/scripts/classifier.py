#!/usr/bin/env python3
"""
Auto-Assign Classifier — Routes goals to specialist agents using Gemini Flash.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "D:/Portable_Soft/hermes"))

# Agent capability matrix for classifier prompt
AGENT_CAPABILITIES = {
    "main": {
        "role": "Coordinator / Decision Maker",
        "keywords": ["coordinate", "decide", "synthesize", "prioritize", "route", "war room", "cross-cutting", "strategy"],
        "domains": ["all"],
        "tools": ["all"],
        "typical_goals": ["routing decisions", "war room sessions", "conflict resolution", "priority setting"]
    },
    "comms": {
        "role": "Communications Specialist",
        "keywords": ["telegram", "email", "notify", "message", "bridge", "send", "broadcast", "alert", "channel", "chat"],
        "domains": ["communication", "notification"],
        "tools": ["telegram", "email", "web"],
        "typical_goals": ["send message", "fix bridge", "setup notifications", "manage channels"]
    },
    "content": {
        "role": "Content Creator",
        "keywords": ["write", "publish", "repurpose", "article", "video", "post", "blog", "thread", "carousel", "script", "copy"],
        "domains": ["content", "creative", "marketing"],
        "tools": ["web", "browser", "write_file", "web_search"],
        "typical_goals": ["create content", "content pipeline", "repurpose assets", "publish to platforms"]
    },
    "ops": {
        "role": "Infrastructure & Operations",
        "keywords": ["deploy", "cron", "server", "monitor", "cost", "infra", "docker", "kubernetes", "ci", "cd", "pipeline", "backup", "migrate"],
        "domains": ["devops", "system", "infrastructure"],
        "tools": ["terminal", "cron", "file", "web"],
        "typical_goals": ["fix server", "add cron job", "reduce costs", "deploy service", "monitor health"]
    },
    "research": {
        "role": "Research Analyst",
        "keywords": ["search", "analyze", "trend", "paper", "hn", "github", "competitor", "market", "keyword", "seo", "signal", "discover"],
        "domains": ["research", "data", "analysis"],
        "tools": ["web_search", "web_fetch", "terminal", "file"],
        "typical_goals": ["find information", "analyze trends", "competitive intel", "literature review"]
    }
}

CLASSIFIER_PROMPT = """You are a router for the Hermes Hive Mind.
Agents: main, comms, content, ops, research.

Given a user goal, return JSON: {"agent": "...", "confidence": 0.xx, "reasoning": "..."}

Rules:
- Main: coordination, decisions, unclear/broad goals, cross-cutting
- Comms: messaging, telegram, email, notifications, bridges
- Content: writing, publishing, content pipeline, creative assets
- Ops: infrastructure, cron, servers, deployment, costs, monitoring
- Research: external search, trends, papers, competitive intel, market analysis

Goal: {goal}
Context: {context}"""


def load_gemini_key() -> Optional[str]:
    """Load GEMINI_API_KEY from env or .env"""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    # Try .env
    env_path = HERMES_HOME / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("GEMINI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"\'')
    return None


def call_gemini_flash(prompt: str, api_key: str) -> Dict[str, Any]:
    """Call Gemini Flash via REST API."""
    import urllib.request
    import urllib.error
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 512,
            "responseMimeType": "application/json"
        }
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(content)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")[:500]
        raise RuntimeError(f"Gemini API error {e.code}: {error_body}")
    except Exception as e:
        raise RuntimeError(f"Gemini call failed: {e}")


def classify_goal(goal: str, context: str = "") -> Dict[str, Any]:
    """
    Classify a goal to the appropriate agent.
    
    Returns:
        {"agent": "main|comms|content|ops|research", "confidence": 0.0-1.0, "reasoning": "..."}
    """
    # Kill switch check
    if os.environ.get("HERMES_AUTO_ASSIGN_ENABLED", "true").lower() != "true":
        return {"agent": "main", "confidence": 1.0, "reasoning": "Auto-assign disabled, defaulting to main"}
    
    api_key = load_gemini_key()
    if not api_key:
        # Fallback: keyword-based classification
        return fallback_classify(goal)
    
    prompt = CLASSIFIER_PROMPT.format(goal=goal, context=context or "none")
    
    try:
        result = call_gemini_flash(prompt, api_key)
        agent = result.get("agent", "main").lower()
        confidence = float(result.get("confidence", 0.5))
        reasoning = result.get("reasoning", "Gemini classification")
        
        # Validate agent
        if agent not in AGENT_CAPABILITIES:
            agent = "main"
            confidence = 0.5
            reasoning = "Invalid agent from Gemini, defaulted to main"
        
        return {"agent": agent, "confidence": confidence, "reasoning": reasoning}
    except Exception as e:
        logging.warning(f"Gemini classification failed: {e}, using fallback")
        return fallback_classify(goal)


def fallback_classify(goal: str) -> Dict[str, Any]:
    """Keyword-based fallback classification."""
    goal_lower = goal.lower()
    scores = {}
    
    for agent, caps in AGENT_CAPABILITIES.items():
        score = 0
        for kw in caps["keywords"]:
            if kw in goal_lower:
                score += 1
        for dom in caps["domains"]:
            if dom != "all" and dom in goal_lower:
                score += 2
        scores[agent] = score
    
    if max(scores.values()) == 0:
        return {"agent": "main", "confidence": 0.4, "reasoning": "No keyword matches, defaulting to main"}
    
    best_agent = max(scores, key=scores.get)
    confidence = min(0.7, 0.3 + scores[best_agent] * 0.1)
    
    return {"agent": best_agent, "confidence": confidence, "reasoning": f"Keyword fallback: {scores}"}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Auto-Assign Classifier")
    parser.add_argument("--goal", required=True, help="Goal to classify")
    parser.add_argument("--context", default="", help="Additional context")
    args = parser.parse_args()
    
    result = classify_goal(args.goal, args.context)
    print(json.dumps(result, indent=2))