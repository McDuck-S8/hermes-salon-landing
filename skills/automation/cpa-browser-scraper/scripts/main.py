#!/usr/bin/env python3
"""
CPA Browser Scraper - Main CLI entry point
Uses browser-harness (CDP) to scrape CPA networks, creatives, competitors, and local businesses.
"""

import sys
import os
import json
import argparse
from datetime import datetime
from typing import List, Dict, Any

# Add browser-harness to path
sys.path.insert(0, '/d/Portable_Soft/hermes/browser-harness/src')
sys.path.insert(0, '/d/Portable_Soft/hermes/skills/automation/cpa-browser-scraper/scripts')

from browser_harness.helpers import *


def setup_browser():
    """Ensure browser-harness daemon is running and connected."""
    try:
        info = page_info()
        print(f"✓ Connected to browser: {info.get('title', 'Unknown')}")
        return True
    except Exception as e:
        print(f"✗ Browser not connected: {e}")
        print("Start browser-harness daemon first:")
        print("  cd /d/Portable_Soft/hermes/browser-harness")
        print("  python -m src.browser_harness.daemon")
        return False


def scan_offers(args):
    """Scan CPA networks for offers."""
    from scripts.networks.adcombo import scan_adcombo_offers
    from scripts.networks.cpalead import scan_cpalead_offers
    from scripts.networks.alfaleads import scan_alfaleads_offers
    
    all_offers = []
    
    if args.network in ['all', 'adcombo']:
        print(f"\n🔍 Scanning AdCombo ({args.geo}, {args.vertical})...")
        offers = scan_adcombo_offers(geo=args.geo, vertical=args.vertical, max_pages=args.pages)
        all_offers.extend(offers)
        print(f"  Found {len(offers)} offers")
    
    if args.network in ['all', 'cpalead']:
        print(f"\n🔍 Scanning CPAlead ({args.geo}, {args.vertical})...")
        offers = scan_cpalead_offers(geo=args.geo, vertical=args.vertical, max_pages=args.pages)
        all_offers.extend(offers)
        print(f"  Found {len(offers)} offers")
    
    if args.network in ['all', 'alfaleads']:
        print(f"\n🔍 Scanning Alfaleads ({args.geo}, {args.vertical})...")
        offers = scan_alfaleads_offers(geo=args.geo, vertical=args.vertical, max_pages=args.pages)
        all_offers.extend(offers)
        print(f"  Found {len(offers)} offers")
    
    # Filter by min payout and cap
    filtered = [o for o in all_offers if o.payout >= args.min_payout and o.cap_daily >= args.min_cap]
    
    # Sort by ROI estimate
    filtered.sort(key=lambda x: x.roi_estimate, reverse=True)
    
    # Output
    output = {
        "scanned_at": datetime.now().isoformat(),
        "networks": args.network,
        "geo": args.geo,
        "vertical": args.vertical,
        "filters": {"min_payout": args.min_payout, "min_cap": args.min_cap},
        "total_found": len(all_offers),
        "after_filters": len(filtered),
        "offers": [o.to_dict() for o in filtered[:args.limit]]
    }
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Saved to {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    
    # Print summary table
    print(f"\n📊 Top {min(args.limit, len(filtered))} offers:")
    print("-" * 100)
    print(f"{'Network':<12} {'Name':<30} {'Payout':<8} {'Flow':<6} {'Cap':<8} {'ROI%':<6} {'Geo':<4}")
    print("-" * 100)
    for o in filtered[:args.limit]:
        print(f"{o.network:<12} {o.name[:28]:<30} ${o.payout:<7} {o.flow:<6} {o.cap_daily:<8} {o.roi_estimate:<6.1f} {o.geo:<4}")


def scan_creatives(args):
    """Scan FB Library and TikTok Creative Center for creatives."""
    from scripts.creative.fb_ad_library import scan_fb_ad_library
    from scripts.creative.tiktok_creative_center import scan_tiktok_creative_center
    
    all_creatives = []
    
    if args.platform in ['all', 'fb']:
        print(f"\n🔍 Scanning FB Ad Library ({args.query}, {args.country})...")
        creatives = scan_fb_ad_library(
            query=args.query,
            country=args.country,
            ad_type=args.ad_type,
            max_results=args.limit
        )
        all_creatives.extend(creatives)
        print(f"  Found {len(creatives)} creatives")
    
    if args.platform in ['all', 'tiktok']:
        print(f"\n🔍 Scanning TikTok Creative Center ({args.region}, {args.category})...")
        creatives = scan_tiktok_creative_center(
            region=args.region,
            category=args.category,
            max_results=args.limit
        )
        all_creatives.extend(creatives)
        print(f"  Found {len(creatives)} creatives")
    
    # Output
    output = {
        "scanned_at": datetime.now().isoformat(),
        "platforms": args.platform,
        "query": args.query,
        "country": args.country,
        "total": len(all_creatives),
        "creatives": [c.__dict__ for c in all_creatives[:args.limit]]
    }
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Saved to {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    
    # Print summary
    print(f"\n🎨 Top {min(args.limit, len(all_creatives))} creatives:")
    print("-" * 100)
    for c in all_creatives[:args.limit]:
        print(f"[{c.platform}] {c.advertiser[:20]} | {c.format} | {c.cta[:20]} | Impr: {c.impressions_est}")


def analyze_competitors(args):
    """Analyze competitor landing pages."""
    from scripts.competitor.lander_analyzer import analyze_competitor_lander, analyze_multiple_landers
    
    urls = args.urls
    if args.file:
        with open(args.file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    
    if not urls:
        print("No URLs provided. Use --urls or --file")
        return
    
    print(f"\n🔍 Analyzing {len(urls)} competitor landers...")
    reports = analyze_multiple_landers(urls)
    
    output = {
        "scanned_at": datetime.now().isoformat(),
        "total": len(reports),
        "reports": [r.to_dict() for r in reports]
    }
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Saved to {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    
    # Print summary
    for r in reports:
        print(f"\n📄 {r.url}")
        print(f"  Hook: {r.hook[:100]}")
        print(f"  Type: {r.structure.get('lander_type', 'unknown')}")
        print(f"  Tech: {', '.join(r.tech_stack) or 'none'}")
        print(f"  Spend signals: {r.spend_signals}")


def scan_local_biz(args):
    """Scan Google Maps for local businesses needing landing pages."""
    from scripts.maps.maps_scanner import scan_area_for_leads, QUERIES
    
    query = args.query
    if args.preset and args.preset in QUERIES:
        query = QUERIES[args.preset]
        print(f"Using preset '{args.preset}': {query}")
    
    if not query:
        print("Provide --query or --preset")
        return
    
    print(f"\n🔍 Scanning Google Maps: {query}")
    leads = scan_area_for_leads(
        query=query,
        max_results=args.limit,
        analyze_websites=not args.no_website_analysis
    )
    
    output = {
        "scanned_at": datetime.now().isoformat(),
        "query": query,
        "total_scanned": len(leads),
        "leads_needing_lp": len([b for b in leads if b.needs_landing_page]),
        "leads": [b.__dict__ for b in leads]
    }
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Saved to {args.output}")
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    
    # Print leads summary
    print(f"\n🎯 Leads needing landing pages:")
    print("-" * 100)
    for b in leads:
        if b.needs_landing_page:
            print(f"{b.name[:30]} | {b.phone} | {b.address[:40]} | Site: {b.website or 'NONE'} | Rating: {b.rating} | Quality: {b.website_quality_score}")


def list_presets(args):
    """List available preset queries."""
    from scripts.maps.maps_scanner import QUERIES
    
    print("\n📋 Available presets:")
    for key, query in QUERIES.items():
        print(f"  {key}: {query}")


def main():
    parser = argparse.ArgumentParser(
        description="CPA Browser Scraper - CPA/Arbitrage intelligence via browser-harness (CDP)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan CPA offers
  python -m cpa_browser_scraper scan-offers --network all --geo IN --vertical gambling --min-payout 3 --min-cap 1000
  
  # Scan creatives
  python -m cpa_browser_scraper scan-creatives --platform fb --query "cricket betting" --country IN
  python -m cpa_browser_scraper scan-creatives --platform tiktok --region IN --category gaming
  
  # Analyze competitor landers
  python -m cpa_browser_scraper analyze-competitors --urls "https://comp1.com" "https://comp2.com"
  
  # Scan local businesses for landing page leads
  python -m cpa_browser_scraper scan-local --preset kiev_salons
  python -m cpa_browser_scraper scan-local --query "салон красоты Позняки Киев"
  
  # List presets
  python -m cpa_browser_scraper list-presets
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # scan-offers
    p_offers = subparsers.add_parser('scan-offers', help='Scan CPA networks for offers')
    p_offers.add_argument('--network', choices=['all', 'adcombo', 'cpalead', 'alfaleads'], default='all')
    p_offers.add_argument('--geo', default='IN', help='Target country (IN, BR, US, DE, etc.)')
    p_offers.add_argument('--vertical', default='gambling', help='Vertical (gambling, dating, nutra, finance, etc.)')
    p_offers.add_argument('--min-payout', type=float, default=3.0, help='Minimum payout $')
    p_offers.add_argument('--min-cap', type=int, default=1000, help='Minimum daily cap $')
    p_offers.add_argument('--pages', type=int, default=3, help='Pages per network')
    p_offers.add_argument('--limit', type=int, default=20, help='Max results to show')
    p_offers.add_argument('--output', help='Output JSON file')
    
    # scan-creatives
    p_creatives = subparsers.add_parser('scan-creatives', help='Scan ad libraries for creatives')
    p_creatives.add_argument('--platform', choices=['all', 'fb', 'tiktok'], default='all')
    p_creatives.add_argument('--query', default='cricket betting', help='Search query for FB Library')
    p_creatives.add_argument('--country', default='IN', help='Country for FB Library')
    p_creatives.add_argument('--ad-type', default='all', help='Ad type (all, political, etc.)')
    p_creatives.add_argument('--region', default='IN', help='Region for TikTok CC')
    p_creatives.add_argument('--category', default='gaming', help='Category for TikTok CC')
    p_creatives.add_argument('--limit', type=int, default=30, help='Max results per platform')
    p_creatives.add_argument('--output', help='Output JSON file')
    
    # analyze-competitors
    p_comp = subparsers.add_parser('analyze-competitors', help='Analyze competitor landing pages')
    p_comp.add_argument('--urls', nargs='+', help='URLs to analyze')
    p_comp.add_argument('--file', help='File with URLs (one per line)')
    p_comp.add_argument('--output', help='Output JSON file')
    
    # scan-local
    p_local = subparsers.add_parser('scan-local', help='Scan Google Maps for local business leads')
    p_local.add_argument('--query', help='Custom search query')
    p_local.add_argument('--preset', help='Preset query (kiev_salons, budva_restaurants, etc.)')
    p_local.add_argument('--limit', type=int, default=50, help='Max results')
    p_local.add_argument('--no-website-analysis', action='store_true', help='Skip website quality analysis')
    p_local.add_argument('--output', help='Output JSON file')
    
    # list-presets
    subparsers.add_parser('list-presets', help='List available preset queries')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Check browser connection
    if not setup_browser():
        sys.exit(1)
    
    # Execute command
    commands = {
        'scan-offers': scan_offers,
        'scan-creatives': scan_creatives,
        'analyze-competitors': analyze_competitors,
        'scan-local': scan_local_biz,
        'list-presets': list_presets,
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()