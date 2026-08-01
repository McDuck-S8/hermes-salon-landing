#!/usr/bin/env python3
"""
cli.py — CLI entry points for herdr-multiagent skill.
"""
import os
import sys
import json
import argparse
from pathlib import Path

# Add scripts to path
_SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# Import modules
from skills.herdr_multiagent.scripts.herdr_multiagent import HerdrMultiAgent
from skills.herdr_multiagent.scripts.agent_bus import agent_send, agent_receive, agent_peek, agent_reply, agent_broadcast
from skills.herdr_multiagent.scripts.task_templates import TaskTemplateManager
from skills.herdr_multiagent.scripts.space_manager import HerdrSpaceManager


def cmd_setup(args):
    """Setup agent spaces."""
    orchestrator = HerdrMultiAgent()
    result = orchestrator.setup(args.roles, args.force)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["errors"]:
        sys.exit(1)


def cmd_teardown(args):
    """Teardown agent spaces."""
    orchestrator = HerdrMultiAgent()
    result = orchestrator.teardown(args.roles)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result["errors"]:
        sys.exit(1)


def cmd_status(args):
    """Show agent status."""
    orchestrator = HerdrMultiAgent()
    result = orchestrator.status()
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_send(args):
    """Send message to agent."""
    msg_id = agent_send(
        to_agent=args.to,
        type=args.type,
        payload=json.loads(args.payload) if args.payload else {},
        from_agent=args.from_agent,
        correlation_id=args.correlation_id,
        priority=args.priority,
    )
    print(f"Sent: {msg_id}")


def cmd_receive(args):
    """Receive messages for agent."""
    types = args.types.split(",") if args.types else None
    messages = agent_receive(args.agent, args.limit, types)
    for msg in messages:
        print(json.dumps({
            "id": msg.id,
            "from": msg.from_agent,
            "type": msg.type,
            "payload": msg.payload,
            "timestamp": msg.timestamp,
            "correlation_id": msg.correlation_id,
        }, ensure_ascii=False))


def cmd_peek(args):
    """Peek at agent's queue."""
    messages = agent_peek(args.agent, args.limit)
    for msg in messages:
        print(json.dumps({
            "id": msg.id,
            "from": msg.from_agent,
            "type": msg.type,
            "payload": msg.payload,
            "timestamp": msg.timestamp,
        }, ensure_ascii=False))


def cmd_template(args):
    """Manage task templates."""
    mgr = TaskTemplateManager()
    
    if args.template_action == "list":
        templates = mgr.list_templates()
        for t in templates:
            print(f"{t['name']} ({t['role']}): {t['description'][:60]}")
            print(f"  Params: {', '.join(t['params'])}")
    
    elif args.template_action == "render":
        if not args.params:
            args.params = "{}"
        params = json.loads(args.params)
        result = mgr.render(args.name, params)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.template_action == "create":
        # Interactive creation or from args
        print("Template creation - use YAML files in templates/ directory")


def cmd_space(args):
    """Manage Herdr spaces."""
    mgr = HerdrSpaceManager()
    
    if args.space_action == "list":
        spaces = mgr.list_spaces()
        for s in spaces:
            print(s)
    
    elif args.space_action == "info":
        info = mgr.get_space_info(args.name)
        if info:
            print(json.dumps({
                "name": info.name,
                "panes": [{"index": p.index, "name": p.name, "pid": p.pid} for p in info.panes],
                "created_at": info.created_at,
            }, indent=2, ensure_ascii=False))
        else:
            print(f"Space not found: {args.name}")
    
    elif args.space_action == "create":
        if mgr.create_space(args.name):
            print(f"Created space: {args.name}")
        else:
            print(f"Failed to create space: {args.name}")
            sys.exit(1)
    
    elif args.space_action == "remove":
        if mgr.remove_space(args.name):
            print(f"Removed space: {args.name}")
        else:
            print(f"Failed to remove space: {args.name}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="herdr-multiagent — Multi-agent orchestration via Herdr",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Setup agent workspace
  herdr-multiagent setup --roles orchestrator,coder,browser,researcher,deployer,cpa-operator
  
  # Send task to agent
  agent_send --to coder --type task --payload '{"task": "Fix auth bug"}'
  
  # Receive messages as agent
  agent_receive --agent coder --limit 5
  
  # Run task from template
  agent_task --template cpa-scrape --params '{"geo": "IN", "vertical": "gambling"}'
  
  # Check status
  herdr-multiagent status
        """
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # herdr-multiagent commands
    setup_parser = subparsers.add_parser("setup", help="Create agent spaces/panes")
    setup_parser.add_argument("--roles", nargs="+", help="Roles to setup")
    setup_parser.add_argument("--force", action="store_true", help="Force recreate")
    
    teardown_parser = subparsers.add_parser("teardown", help="Remove agent spaces")
    teardown_parser.add_argument("--roles", nargs="+", help="Roles to teardown")
    
    subparsers.add_parser("status", help="Show all agent spaces status")
    
    # agent_send command
    send_parser = subparsers.add_parser("send", help="Send message to agent")
    send_parser.add_argument("--to", required=True, help="Target agent")
    send_parser.add_argument("--type", default="task", help="Message type")
    send_parser.add_argument("--payload", default="{}", help="JSON payload")
    send_parser.add_argument("--from-agent", default="orchestrator", help="Sender")
    send_parser.add_argument("--correlation-id", help="Correlation ID for replies")
    send_parser.add_argument("--priority", type=int, default=0, help="Priority")
    
    # agent_receive command
    receive_parser = subparsers.add_parser("receive", help="Receive messages for agent")
    receive_parser.add_argument("--agent", required=True, help="Agent name")
    receive_parser.add_argument("--limit", type=int, default=10, help="Max messages")
    receive_parser.add_argument("--types", help="Comma-separated message types")
    
    # agent_peek command
    peek_parser = subparsers.add_parser("peek", help="Peek at agent's queue")
    peek_parser.add_argument("--agent", required=True, help="Agent name")
    peek_parser.add_argument("--limit", type=int, default=10, help="Max messages")
    
    # agent_template command
    template_parser = subparsers.add_parser("template", help="Manage task templates")
    template_sub = template_parser.add_subparsers(dest="template_action", required=True)
    template_sub.add_parser("list", help="List templates")
    render_parser = template_sub.add_parser("render", help="Render template")
    render_parser.add_argument("--name", required=True, help="Template name")
    render_parser.add_argument("--params", default="{}", help="JSON parameters")
    template_sub.add_parser("create", help="Create new template")
    
    # space command
    space_parser = subparsers.add_parser("space", help="Manage Herdr spaces")
    space_sub = space_parser.add_subparsers(dest="space_action", required=True)
    space_sub.add_parser("list", help="List spaces")
    info_parser = space_sub.add_parser("info", help="Show space info")
    info_parser.add_argument("--name", required=True, help="Space name")
    create_parser = space_sub.add_parser("create", help="Create space")
    create_parser.add_argument("--name", required=True, help="Space name")
    remove_parser = space_sub.add_parser("remove", help="Remove space")
    remove_parser.add_argument("--name", required=True, help="Space name")
    
    args = parser.parse_args()
    
    # Route to handler
    handlers = {
        "setup": cmd_setup,
        "teardown": cmd_teardown,
        "status": cmd_status,
        "send": cmd_send,
        "receive": cmd_receive,
        "peek": cmd_peek,
        "template": cmd_template,
        "space": cmd_space,
    }
    
    handler = handlers.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()