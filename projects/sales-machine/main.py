#!/usr/bin/env python3
"""
Sales Machine — International Lead Generation & Sales Automation

Quick start:
  python main.py scan budva_restaurants    # Scan Google Maps
  python main.py demo <lead_id>            # Generate demo
  python main.py campaign <lead_id>        # Start campaign
  python main.py dashboard                  # View stats

Modules:
  lead_finder.py   — International lead generation (Google Maps, etc.)
  demo_builder.py  — Landing page generator (salon, rest, hotel, etc.)
  closer.py        — Multi-channel communication (Tg, WA, VK, OK, Email)
  field_agent.py   — Field agent management & close scripts

Database: db/clients.db
  clients       — Leads with contact info
  demos         — Generated landing pages
  conversations — Message history
  deals         — Closed deals
  field_agents  — Human agents on the ground
"""

import sys, os, json, argparse
from datetime import datetime
from typing import Dict, Any

DB_PATH = r"D:\Portable_Soft\hermes\projects\sales-machine\db\clients.db"


def cmd_scan(args):
    """Scan Google Maps for leads."""
    from lead_finder import run_lead_generation, init_db
    init_db()
    stats = run_lead_generation(args.preset, max_results=args.limit, lang=args.lang)
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    print(f"\n📊 Summary:")
    print(f"  Found: {stats['total_scanned']} leads")
    print(f"  Need LP: {stats['leads_needing_lp']}")
    print(f"  Have website: {stats['leads_with_website']}")
    print(f"  Avg rating: {stats['avg_rating']:.1f}")


def cmd_leads(args):
    """List leads."""
    from lead_finder import get_leads_by_status, get_leads_needing_lp
    import sqlite3
    
    if args.needs_lp:
        leads = get_leads_needing_lp(limit=args.limit)
    else:
        leads = get_leads_by_status(args.status, limit=args.limit)
    
    print(f"\n{'='*80}")
    print(f"Leads ({args.status}):")
    print(f"{'='*80}")
    for l in leads:
        print(f"\n[{l['id']}] {l['name']}")
        print(f"  📞 {l['phone'] or 'N/A'} | ⭐ {l['rating']} ({l['review_count']} reviews)")
        print(f"  📍 {l['address'] or 'N/A'}")
    print(f"\nTotal: {len(leads)} leads")


def cmd_demo(args):
    """Generate demo for a lead."""
    from demo_builder import generate_demo, generate_and_save
    import sqlite3
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (args.lead_id,))
    lead = cursor.fetchone()
    conn.close()
    
    if not lead:
        print(f"❌ Lead {args.lead_id} not found")
        return
    
    lead_dict = dict(lead)
    filepath = generate_and_save(lead_dict, niche=args.niche, lang=args.lang)
    print(f"\n✅ Demo generated: {filepath}")
    if args.deploy:
        print(f"🚀 Deploy to GitHub Pages...")
        from demo_builder import deploy_to_github_pages
        url = deploy_to_github_pages(lead_dict, args.niche, args.lang)
        print(f"  URL: {url}")


def cmd_dashboard(args):
    """Show sales machine dashboard."""
    import sqlite3
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Stats
    stats = {}
    for status in ['new', 'contacted', 'demo_sent', 'meeting_scheduled', 'closed_won', 'closed_lost', 'assigned']:
        cursor.execute("SELECT COUNT(*) FROM clients WHERE status = ?", (status,))
        stats[status] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM deals WHERE status = 'closed_won'")
    deals_won = cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM deals WHERE status = 'closed_won'")
    revenue = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM field_agents WHERE active = 1")
    agents = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM demos")
    demos = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"  SALES MACHINE DASHBOARD")
    print(f"{'='*60}")
    print(f"\n📋 LEADS:")
    print(f"  New:              {stats['new']}")
    print(f"  Contacted:        {stats['contacted']}")
    print(f"  Demo sent:        {stats['demo_sent']}")
    print(f"  Meeting scheduled: {stats['meeting_scheduled']}")
    print(f"  Assigned to agent: {stats['assigned']}")
    print(f"  Won:              {stats['closed_won']}")
    print(f"  Lost:             {stats['closed_lost']}")
    print(f"  Total:            {sum(stats.values())}")
    
    print(f"\n💰 DEALS:")
    print(f"  Closed: {deals_won}")
    print(f"  Revenue: €{revenue:.0f}")
    
    print(f"\n👤 AGENTS: {agents}")
    print(f"\n📄 DEMOS GENERATED: {demos}")
    print(f"{'='*60}")


def cmd_agent(args):
    """Register or manage field agents."""
    from field_agent import register_agent, get_available_agents, get_agent_dashboard
    
    if args.action == "register":
        agent_id = register_agent(
            name=args.name,
            phone=args.phone,
            location=args.location,
            languages=args.languages.split(",") if args.languages else ["ru", "sr"],
            telegram=args.telegram or "",
            whatsapp=args.whatsapp or "",
            commission_rate=args.commission or 0.3
        )
        print(f"✅ Agent registered: {agent_id}")
        print(f"  Name: {args.name}")
        print(f"  Phone: {args.phone}")
        print(f"  Location: {args.location}")
    
    elif args.action == "list":
        agents = get_available_agents()
        print(f"\n{'='*60}")
        print(f"Field Agents ({len(agents)}):")
        print(f"{'='*60}")
        for a in agents:
            print(f"\n  [{a['id']}] {a['name']}")
            print(f"    📞 {a['phone']}")
            print(f"    📍 {a['location']}")
            print(f"    💰 Commission: {float(a['commission_rate'])*100:.0f}%")
    
    elif args.action == "dashboard":
        dashboard = get_agent_dashboard(args.agent_id)
        print(f"\n{'='*60}")
        print(f"Agent Dashboard: {dashboard['agent_id']}")
        print(f"{'='*60}")
        print(f"  Proposals: {dashboard['proposals']}")
        print(f"  Deals closed: {dashboard['closed_deals']}")
        print(f"  Revenue: €{dashboard['total_revenue']:.0f}")
        print(f"  Est. commission: €{dashboard['estimated_commission']:.0f}")


def main():
    parser = argparse.ArgumentParser(description="Sales Machine CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # scan
    p = subparsers.add_parser("scan", help="Scan Google Maps for leads")
    p.add_argument("preset", nargs="?", default="kiev_salons", 
                   help="Preset name (kiev_salons, budva_restaurants, etc.)")
    p.add_argument("--limit", type=int, default=30, help="Max leads")
    p.add_argument("--lang", default="ru", help="Language (ru/en/sr)")
    
    # leads
    p = subparsers.add_parser("leads", help="List leads")
    p.add_argument("--status", default="new", help="Filter by status")
    p.add_argument("--needs-lp", action="store_true", help="Only leads needing LP")
    p.add_argument("--limit", type=int, default=50, help="Max results")
    
    # demo
    p = subparsers.add_parser("demo", help="Generate demo for lead")
    p.add_argument("lead_id", help="Lead ID from database")
    p.add_argument("--niche", default="salon", help="Niche (salon/restaurant/hotel/auto_service/clinic)")
    p.add_argument("--lang", default="ru", help="Language (ru/en/sr)")
    p.add_argument("--deploy", action="store_true", help="Deploy to GitHub Pages")
    
    # dashboard
    subparsers.add_parser("dashboard", help="Show sales machine dashboard")
    
    # agent
    p = subparsers.add_parser("agent", help="Manage field agents")
    p.add_argument("action", choices=["register", "list", "dashboard"])
    p.add_argument("--name", help="Agent name")
    p.add_argument("--phone", help="Agent phone")
    p.add_argument("--location", default="Budva, Montenegro", help="Agent location")
    p.add_argument("--languages", default="ru,sr,en", help="Comma-separated languages")
    p.add_argument("--telegram", help="Agent Telegram")
    p.add_argument("--whatsapp", help="Agent WhatsApp")
    p.add_argument("--commission", type=float, default=0.3, help="Commission rate")
    p.add_argument("--agent-id", help="Agent ID for dashboard")
    
    args = parser.parse_args()
    
    # Change to module directory
    try:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        # Running via exec
        pass
    
    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "leads":
        cmd_leads(args)
    elif args.command == "demo":
        cmd_demo(args)
    elif args.command == "dashboard":
        cmd_dashboard(args)
    elif args.command == "agent":
        cmd_agent(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()