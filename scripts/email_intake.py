#!/usr/bin/env python3
"""
Email Intake — Connects to IMAP mailbox, scans emails, extracts intelligence,
feeds Knowledge Cube with offers, CPA opportunities, financial data.
"""

import imaplib
import email
import json
import re
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import urllib.request
import urllib.parse

HERMES_HOME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERMES_HOME / "scripts"))

# Import Knowledge Cube
from knowledge_cube import add_experience, get_db

# DeepSeek endpoint
LLM_URL = "http://localhost:9655/v1/chat/completions"
LLM_MODEL = "deepseek-chat"

# IMAP config from env
IMAP_HOST = os.environ.get("IMAP_HOST", "imap.gmail.com")
IMAP_PORT = int(os.environ.get("IMAP_PORT", "993"))
IMAP_USER = os.environ.get("IMAP_USER", "")
IMAP_PASS = os.environ.get("IMAP_PASS", "")
IMAP_FOLDER = os.environ.get("IMAP_FOLDER", "INBOX")

# Categories matching gbrain + our needs
CATEGORIES = {
    "purchase": ["order", "receipt", "invoice", "payment", "purchase", "bought", "confirmed", "shipped"],
    "subscription": ["subscription", "renewal", "recurring", "monthly", "yearly", "plan", "billing cycle"],
    "finance": ["bank", "statement", "transaction", "transfer", "deposit", "withdrawal", "balance", "crypto", "wallet"],
    "social": ["notification", "follow", "like", "comment", "message", "friend", "connection", "linkedin", "twitter", "facebook"],
    "news": ["newsletter", "digest", "weekly", "daily", "product hunt", "indie hackers", "hacker news", "morning brew"],
    "offer": ["affiliate", "cpa", "offer", "commission", "partner", "network", "epc", "conversion", "payout", "new offer", "exclusive"],
    "arbitrage": ["arbitrage", "traffic", "roi", "campaign", "creative", "landing", "cloak", "tracker", "voluum", "binom", "keitaro"]
}

def call_llm(prompt: str, max_tokens: int = 1000) -> str:
    """Call local DeepSeek API."""
    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.2
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(LLM_URL, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"LLM_ERROR: {e}"

def classify_email(subject: str, body: str, sender: str) -> List[str]:
    """Classify email into categories based on keywords."""
    text = f"{subject} {body} {sender}".lower()
    matches = []
    for cat, keywords in CATEGORIES.items():
        if any(kw in text for kw in keywords):
            matches.append(cat)
    return matches if matches else ["other"]

def extract_email_intelligence(email_data: Dict, llm_ok: bool = True) -> Dict:
    """Use LLM to extract structured intelligence from email."""
    if not llm_ok:
        # Rule-based fallback
        return rule_based_extraction(email_data)
    
    prompt = f"""Extract structured data from this email. Return ONLY valid JSON.

Email:
From: {email_data['sender']}
Subject: {email_data['subject']}
Date: {email_data['date']}
Body: {email_data['body'][:2000]}

Extract:
1. category: one of [purchase, subscription, finance, social, news, offer, arbitrage, other]
2. entities: list of companies/products/services mentioned
3. offer_details: if affiliate/CPA offer detected -> {{network, offer_name, geo, payout, epc, vertical}}
4. financial: if purchase/subscription -> {{amount, currency, product, merchant}}
5. action_required: boolean - does this need follow-up?
6. summary: 1-sentence summary
7. tags: relevant tags for knowledge cube

Return format:
{{"category": "...", "entities": [...], "offer_details": {{...}}, "financial": {{...}}, "action_required": true/false, "summary": "...", "tags": [...]}}"""

    response = call_llm(prompt, max_tokens=800)
    try:
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except:
        pass
    return {"category": "other", "entities": [], "summary": "LLM parsing failed", "tags": ["llm_error"]}


def rule_based_extraction(email_data: Dict) -> Dict:
    """Rule-based extraction when LLM is unavailable."""
    text = f"{email_data['subject']} {email_data['body']} {email_data['sender']}".lower()
    
    # Determine category
    category = "other"
    for cat, keywords in CATEGORIES.items():
        if any(kw in text for kw in keywords):
            category = cat
            break
    
    # Extract entities (simple heuristic)
    entities = []
    known_companies = ["maxbounty", "cpagrip", "producthunt", "digitalocean", "affiliatefix", "netflix", "cityads", "github", "admitad", "indiehackers", "semrush", "hostinger", "fiverr", "next.js", "supabase", "stripe"]
    for company in known_companies:
        if company in text:
            entities.append(company.title())
    
    # Check for offer details
    offer_details = None
    if category == "offer" or "cpa" in text or "affiliate" in text:
        offer_details = {
            "network": "unknown",
            "offer_name": "unknown",
            "geo": "unknown",
            "payout": "unknown",
            "epc": "unknown",
            "vertical": "unknown"
        }
        # Try to extract network
        for net in ["maxbounty", "cpagrip", "cityads", "admitad", "ogads", "clickbank", "impact", "partnerstack", "rewardful"]:
            if net in text:
                offer_details["network"] = net.title()
                break
        # Try to extract payout
        import re
        payout_match = re.search(r'\$(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:cpa|CPA|payout)', text)
        if payout_match:
            offer_details["payout"] = f"${payout_match.group(1)}"
        # Try to extract offer name from subject
        offer_details["offer_name"] = email_data['subject'][:100]
    
    # Check for financial
    financial = None
    if category in ["purchase", "subscription"]:
        financial = {"amount": "unknown", "currency": "USD", "product": "unknown", "merchant": "unknown"}
        import re
        amt_match = re.search(r'\$(\d+(?:,\d+)*(?:\.\d+)?)', text)
        if amt_match:
            financial["amount"] = f"${amt_match.group(1)}"
        financial["product"] = email_data['subject'][:100]
        # Extract merchant from sender
        sender = email_data['sender'].lower()
        for merchant in ["digitalocean", "netflix", "github", "maxbounty", "cpagrip", "admitad"]:
            if merchant in sender:
                financial["merchant"] = merchant.title()
                break
    
    # Action required
    action_required = category in ["offer", "arbitrage"] or "action" in text or "urgent" in text or "exclusive" in text
    
    # Summary
    summary = f"Email from {email_data['sender']}: {email_data['subject'][:80]}"
    
    # Tags
    tags = [category, "email"]
    if offer_details:
        tags.extend(["cpa", "offer", "affiliate"])
    if action_required:
        tags.append("action_required")
    
    return {
        "category": category,
        "entities": entities,
        "offer_details": offer_details,
        "financial": financial,
        "action_required": action_required,
        "summary": summary,
        "tags": tags
    }

def connect_imap() -> imaplib.IMAP4_SSL:
    """Connect to IMAP server."""
    if not IMAP_USER or not IMAP_PASS:
        raise ValueError("IMAP_USER and IMAP_PASS environment variables required")
    
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    mail.login(IMAP_USER, IMAP_PASS)
    mail.select(IMAP_FOLDER)
    return mail

def fetch_recent_emails(mail: imaplib.IMAP4_SSL, count: int = 50) -> List[Dict]:
    """Fetch last N emails."""
    status, messages = mail.search(None, "ALL")
    if status != "OK":
        return []
    
    email_ids = messages[0].split()
    recent_ids = email_ids[-count:] if len(email_ids) > count else email_ids
    
    emails = []
    for eid in reversed(recent_ids):  # Newest first
        status, msg_data = mail.fetch(eid, "(RFC822)")
        if status != "OK":
            continue
        
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        # Extract parts
        subject = msg.get("Subject", "")
        sender = msg.get("From", "")
        date = msg.get("Date", "")
        
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode(errors="ignore")
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(errors="ignore")
        
        emails.append({
            "id": eid.decode(),
            "subject": subject,
            "sender": sender,
            "date": date,
            "body": body[:5000],  # Limit body size
            "fetched_at": datetime.now().isoformat()
        })
    
    return emails

def save_to_knowledge_cube(email_data: Dict, intelligence: Dict) -> Dict:
    """Save email intelligence to Knowledge Cube."""
    # Build content for KC
    content_parts = [
        f"Email from {email_data['sender']}: {email_data['subject']}",
        f"Category: {intelligence.get('category', 'unknown')}",
        f"Summary: {intelligence.get('summary', '')}",
        f"Entities: {', '.join(intelligence.get('entities', []))}"
    ]
    
    if intelligence.get('offer_details'):
        offer = intelligence['offer_details']
        content_parts.append(f"CPA Offer: {offer.get('offer_name', 'unknown')} via {offer.get('network', 'unknown')}")
        content_parts.append(f"Geo: {offer.get('geo', '')}, Payout: {offer.get('payout', '')}, EPC: {offer.get('epc', '')}")
    
    if intelligence.get('financial'):
        fin = intelligence['financial']
        content_parts.append(f"Transaction: {fin.get('product', '')} - {fin.get('amount', '')} {fin.get('currency', '')}")
    
    content = "\n".join(content_parts)
    
    # Tags
    tags = intelligence.get('tags', [])
    tags.extend(["email", intelligence.get('category', 'other')])
    if intelligence.get('action_required'):
        tags.append("action_required")
    if intelligence.get('offer_details'):
        tags.extend(["cpa", "offer", "affiliate"])
    
    # Add to KC
    result = add_experience(
        text=content,
        tools=["email_intake"],
        source="email",
        dynamic_axes={
            "email_category": intelligence.get('category', 'other'),
            "email_sender": email_data['sender'][:100],
            "has_offer": bool(intelligence.get('offer_details')),
            "action_required": intelligence.get('action_required', False)
        }
    )
    
    return result

def check_llm() -> bool:
    """Check if LLM is available."""
    try:
        test = call_llm("ping")
        return "LLM_ERROR" not in test
    except:
        return False

def main():
    import os
    
    # Check if we have IMAP credentials
    has_creds = bool(os.environ.get("IMAP_USER") and os.environ.get("IMAP_PASS"))
    
    if not has_creds:
        print("[EMAIL_INTAKE] No IMAP credentials found - running in TEST MODE with mock data")
        return run_test_mode()
    
    print("[EMAIL_INTAKE] Starting email intelligence scan...")
    
    # Check LLM
    llm_ok = check_llm()
    if not llm_ok:
        print("[EMAIL_INTAKE] WARNING: LLM not available, using rule-based classification only")
    
    # IMAP config
    imap_host = os.environ.get("IMAP_HOST", "imap.gmail.com")
    imap_user = os.environ.get("IMAP_USER")
    imap_pass = os.environ.get("IMAP_PASS")
    imap_port = int(os.environ.get("IMAP_PORT", "993"))
    
    # Connect to IMAP
    try:
        mail = imaplib.IMAP4_SSL(imap_host, imap_port)
        mail.login(imap_user, imap_pass)
        mail.select("INBOX")
    except Exception as e:
        print(f"[EMAIL_INTAKE] IMAP connection failed: {e}")
        return {"success": False, "error": f"IMAP connection failed: {e}"}
    
    # Fetch last 50 emails
    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()
    recent_ids = email_ids[-50:] if len(email_ids) >= 50 else email_ids
    
    results = {
        "scanned": len(recent_ids),
        "kc_entries": 0,
        "offers_found": 0,
        "actions_created": 0,
        "by_category": {}
    }
    
    for eid in reversed(recent_ids):
        status, msg_data = mail.fetch(eid, "(RFC822)")
        if status != "OK":
            continue
        
        raw_email = msg_data[0][1]
        email_message = email.message_from_bytes(raw_email)
        
        # Extract email data
        subject = decode_header(email_message["Subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()
        
        sender = email_message["From"]
        
        # Get body
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode(errors="ignore")
                        break
        else:
            payload = email_message.get_payload(decode=True)
            if payload:
                body = payload.decode(errors="ignore")
        
        email_data = {
            "id": eid.decode(),
            "subject": subject,
            "sender": sender,
            "body": body[:5000],  # Limit size
            "date": email_message["Date"]
        }
        
        # Process email
        intelligence = extract_email_intelligence(email_data, llm_ok)
        
        # Track categories
        cat = intelligence.get('category', 'other')
        results["by_category"][cat] = results["by_category"].get(cat, 0) + 1
        
        # Save to Knowledge Cube
        kc_result = save_to_knowledge_cube(email_data, intelligence)
        if kc_result.get("status") == "added":
            results["kc_entries"] += 1
        
        # Track offers
        if intelligence.get('offer_details'):
            results["offers_found"] += 1
            print(f"  [OFFER] {intelligence['offer_details'].get('offer_name', 'unknown')} via {intelligence['offer_details'].get('network', 'unknown')}")
        
        # Track actionable
        if intelligence.get('action_required'):
            results["actions_created"] += 1
            print(f"  [ACTION] {intelligence.get('summary', '')}")
    
    mail.logout()
    
    print(f"[EMAIL_INTAKE] Complete: {results['kc_entries']} KC entries, {results['offers_found']} offers, {results['actions_created']} actions")
    
    return {"success": True, "data": results}


def run_test_mode():
    """Run with mock email data for testing."""
    print("[EMAIL_INTAKE] Generating mock email data...")
    
    # Mock emails covering different categories
    mock_emails = [
        {
            "id": "mock_001",
            "subject": "New Offer: Keto Weight Loss Trial - \$45 CPA",
            "sender": "offers@maxbounty.com",
            "body": "Hi Partner, We have a new Keto weight loss offer launching. \$45 CPA for US/CA/UK. High conversion landing page. Contact your AM for access. Network: access. Network: MaxBounty",
            "date": datetime.now().isoformat()
        },
        {
            "id": "mock_002",
            "subject": "Your CPAGrip payment of \$1,247.50 has been sent",
            "sender": "payments@cpagrip.com",
            "body": "Hello, Your payment of \$1,247.50 has been processed and sent to your Payoneer account. This covers earnings from June 1-30. CPAGrip Finance Team",
            "date": datetime.now().isoformat()
        },
        {
            "id": "mock_003",
            "subject": "Product Hunt Daily: Best new AI tools this week",
            "sender": "daily@producthunt.com",
            "body": "This week's top launches: 1) Cursor AI - AI code editor 2) V0 by Vercel - Generate UI from text 3) Perplexity Pages - Research to articles 4) HeyGen 5.0 - AI avatars. Check them out!",
            "date": datetime.now().isoformat()
        },
        {
            "id": "mock_004",
            "subject": "Invoice #INV-2024-001234 from DigitalOcean",
            "sender": "billing@digitalocean.com",
            "body": "Your invoice for \$24.00 is ready. Droplet: s-1vcpu-1gb-sfo3-01. Payment method: Credit Card ending in 4242. Due: July 15, 2024.",
            "date": datetime.now().isoformat()
        },
        {
            "id": "mock_005",
            "subject": "AffiliateFix Weekly: TikTok Organic Case Study \$3k/day",
            "sender": "newsletter@affiliatefix.com",
            "body": "This week's case study: TikTok organic + Gaming offers = \$3k/day. 15 accounts, 3 posts/day. Hook: 'STOP buying V-Bucks!' V-Bucks generator offer on CPAGrip. Full breakdown inside.",
            "date": datetime.now().isoformat()
        },
        {
            "id": "mock_006",
            "subject": "Your Netflix subscription renewal",
            "sender": "info@netflix.com",
            "body": "Your Netflix Premium plan (\$19.99/month) will renew on July 20. Manage your plan at netflix.com/account.",
            "date": datetime.now().isoformat()
        },
        {
            "id": "mock_007",
            "subject": "New high-payout offer: Personal Loan \$5000 - \$25 CPA",
            "sender": "partners@cityads.com",
            "body": "Exclusive offer for top partners: Personal Loan up to \$5000. \$25 CPA for qualified lead. GEO: US. Pre-lander with calculator included. Contact support for access. Network: CityAds",
            "date": datetime.now().isoformat()
        },
        {
            "id": "mock_008",
            "subject": "GitHub Security Alert: Dependabot detected vulnerability",
            "sender": "security@github.com",
            "body": "Dependabot detected a vulnerability in your repository hermes-agent. Package: urllib3 < 1.26.15. Severity: Medium. Update to latest version.",
            "date": datetime.now().isoformat()
        },
        {
            "id": "mock_009",
            "subject": "Weekly earnings report - Admitad",
            "sender": "reports@admitad.com",
            "body": "Your weekly earnings: \$342.10. Top offers: 1) SEMrush Pro - \$120 (recurring) 2) Hostinger - \$85 3) Fiverr - \$67. Conversions: 23. CTR: 2.4%.",
            "date": datetime.now().isoformat()
        },
        {
            "id": "mock_010",
            "subject": "Indie Hackers: How I built \$10k MRR SaaS in 6 months",
            "sender": "newsletter@indiehackers.com",
            "body": "This week's interview: Solo founder built B2B SaaS to \$10k MRR. Stack: Next.js, Supabase, Stripe. Marketing: SEO + Cold email. Churn: 3%. Full breakdown inside.",
            "date": datetime.now().isoformat()
        }
    ]
    
    results = {
        "scanned": len(mock_emails),
        "kc_entries": 0,
        "offers_found": 0,
        "actions_created": 0,
        "by_category": {}
    }
    
    for email_data in mock_emails:
        intelligence = extract_email_intelligence(email_data, False)
        
        cat = intelligence.get('category', 'other')
        results["by_category"][cat] = results["by_category"].get(cat, 0) + 1
        
        kc_result = save_to_knowledge_cube(email_data, intelligence)
        if kc_result.get("status") == "added":
            results["kc_entries"] += 1
        
        if intelligence.get('offer_details'):
            results["offers_found"] += 1
            print(f"  [OFFER] {intelligence['offer_details'].get('offer_name', 'unknown')} via {intelligence['offer_details'].get('network', 'unknown')}")
        
        if intelligence.get('action_required'):
            results["actions_created"] += 1
            print(f"  [ACTION] {intelligence.get('summary', '')}")
    
    print(f"[EMAIL_INTAKE] Test complete: {results['kc_entries']} KC entries, {results['offers_found']} offers, {results['actions_created']} actions")
    return {"success": True, "data": results}

if __name__ == "__main__":
    result = main()
    print(json.dumps(result, ensure_ascii=False, indent=2))