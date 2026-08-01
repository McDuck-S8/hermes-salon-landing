#!/usr/bin/env python3
"""
Email Automation — SMTP/IMAP with warmup, templating, tracking, auto-reply.
"""

import asyncio
import imaplib
import smtplib
import email
import ssl
import random
import string
import sqlite3
import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.header import decode_header
import aiosmtplib
from jinja2 import Environment, BaseLoader

try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class EmailConfig:
    """SMTP/IMAP configuration for an identity."""
    smtp_host: str
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_pass: str = ""
    smtp_tls: bool = True
    
    imap_host: str = ""
    imap_port: int = 993
    imap_user: str = ""
    imap_pass: str = ""
    imap_ssl: bool = True
    
    # OAuth2 (optional)
    oauth2_token: Optional[str] = None
    oauth2_refresh_token: Optional[str] = None
    oauth2_client_id: Optional[str] = None
    oauth2_client_secret: Optional[str] = None
    
    # Warmup state
    daily_limit: int = 50
    sent_today: int = 0
    last_sent: Optional[str] = None
    warmup_stage: int = 0  # 0=new, 1=warming, 2=warmed
    reputation_score: float = 0.5


@dataclass
class EmailTemplate:
    """Jinja2 email template with tracking."""
    name: str
    subject: str
    html_body: str
    text_body: str
    tracking_pixel: bool = True
    click_tracking: bool = True
    utm_params: Dict[str, str] = field(default_factory=dict)
    
    def render(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Render template with context."""
        env = Environment(loader=BaseLoader())
        
        subject_tpl = env.from_string(self.subject)
        html_tpl = env.from_string(self.html_body)
        text_tpl = env.from_string(self.text_body)
        
        return {
            "subject": subject_tpl.render(**context),
            "html": html_tpl.render(**context),
            "text": text_tpl.render(**context),
        }


@dataclass
class EmailMessage:
    """Outgoing email message."""
    to: str
    subject: str
    html: str
    text: str
    from_name: str = ""
    reply_to: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    attachments: List[Dict[str, Any]] = field(default_factory=list)
    tracking_id: str = field(default_factory=lambda: hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8])
    
    def to_mime(self, from_addr: str) -> MIMEMultipart:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"{self.from_name} <{from_addr}>" if self.from_name else from_addr
        msg["To"] = self.to
        msg["Subject"] = self.subject
        msg["Reply-To"] = self.reply_to or from_addr
        msg["Message-ID"] = f"<{self.tracking_id}@{from_addr.split('@')[1]}>"
        
        for k, v in self.headers.items():
            msg[k] = v
        
        msg.attach(MIMEText(self.text, "plain", "utf-8"))
        msg.attach(MIMEText(self.html, "html", "utf-8"))
        
        for att in self.attachments:
            if att["type"] == "image":
                img = MIMEImage(att["data"], name=att.get("name", "image.png"))
                img.add_header("Content-ID", f"<{att['cid']}>")
                msg.attach(img)
        
        return msg


@dataclass
class EmailResult:
    """Result of email operation."""
    success: bool
    tracking_id: str
    to: str
    error: Optional[str] = None
    sent_at: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# TRACKING PIXEL & LINK WRAPPER
# =============================================================================

class TrackingEngine:
    """Generates tracking pixels and wraps links."""
    
    def __init__(self, tracking_domain: str = "t.example.com"):
        self.tracking_domain = tracking_domain
    
    def generate_pixel(self, tracking_id: str, campaign: str = "") -> str:
        """Generate 1x1 transparent tracking pixel."""
        params = {"id": tracking_id}
        if campaign:
            params["c"] = campaign
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f'<img src="https://{self.tracking_domain}/pixel?{query}" width="1" height="1" style="display:none;">'
    
    def wrap_links(self, html: str, tracking_id: str, campaign: str = "") -> str:
        """Wrap all links with tracking."""
        import re
        
        def replace_link(match):
            url = match.group(1)
            text = match.group(2) or url
            params = {"id": tracking_id, "url": url}
            if campaign:
                params["c"] = campaign
            query = "&".join(f"{k}={v}" for k, v in params.items())
            tracked = f"https://{self.tracking_domain}/click?{query}"
            return f'<a href="{tracked}" target="_blank">{text}</a>'
        
        # Match <a href="...">...</a>
        pattern = r'<a\s+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
        return re.sub(pattern, replace_link, html, flags=re.IGNORECASE | re.DOTALL)
    
    def add_utm(self, url: str, utm: Dict[str, str]) -> str:
        """Add UTM parameters to URL."""
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        for k, v in utm.items():
            params[k] = [v]
        new_query = urlencode(params, doseq=True)
        return urlunparse(parsed._replace(query=new_query))


# =============================================================================
# SMTP SENDER WITH WARMUP
# =============================================================================

class SMTPSender:
    """SMTP sender with warmup scheduling and reputation management."""
    
    def __init__(self, config: EmailConfig, db: "EmailDB"):
        self.config = config
        self.db = db
        self.semaphore = asyncio.Semaphore(1)  # Sequential sends
    
    async def send(self, message: EmailMessage) -> EmailResult:
        """Send single email with warmup checks."""
        async with self.semaphore:
            # Check daily limit
            if self.config.sent_today >= self.config.daily_limit:
                return EmailResult(
                    success=False,
                    tracking_id=message.tracking_id,
                    to=message.to,
                    error="Daily limit reached"
                )
            
            # Build MIME
            mime_msg = message.to_mime(self.config.smtp_user)
            
            # Send
            try:
                await aiosmtplib.send(
                    mime_msg,
                    hostname=self.config.smtp_host,
                    port=self.config.smtp_port,
                    username=self.config.smtp_user,
                    password=self.config.smtp_pass,
                    start_tls=self.config.smtp_tls,
                    validate_certs=True,
                )
                
                # Update counters
                self.config.sent_today += 1
                self.config.last_sent = datetime.now().isoformat()
                self._update_warmup()
                self.db.save_config(self.config)
                
                return EmailResult(
                    success=True,
                    tracking_id=message.tracking_id,
                    to=message.to,
                )
            except Exception as e:
                return EmailResult(
                    success=False,
                    tracking_id=message.tracking_id,
                    to=message.to,
                    error=str(e)
                )
    
    def _update_warmup(self):
        """Progress warmup stage based on volume."""
        if self.config.warmup_stage == 0:
            # Stage 0: 5/day for 3 days
            if self.config.sent_today >= 5:
                self.config.warmup_stage = 1
                self.config.daily_limit = 20
        elif self.config.warmup_stage == 1:
            # Stage 1: 20/day for 7 days
            pass  # Would track days
        elif self.config.warmup_stage == 2:
            # Stage 2: Warmed, full limit
            self.config.daily_limit = 200
    
    async def send_batch(self, messages: List[EmailMessage], 
                         delay_range: tuple = (30, 120)) -> List[EmailResult]:
        """Send batch with random delays."""
        results = []
        for msg in messages:
            result = await self.send(msg)
            results.append(result)
            if result.success and msg != messages[-1]:
                delay = random.uniform(*delay_range)
                await asyncio.sleep(delay)
        return results


# =============================================================================
# IMAP RECEIVER WITH AUTO-REPLY
# =============================================================================

class IMAPReceiver:
    """IMAP receiver with auto-reply rules."""
    
    def __init__(self, config: EmailConfig, db: "EmailDB"):
        self.config = config
        self.db = db
        self.auto_reply_rules: List[Dict] = []
    
    def add_auto_reply_rule(self, condition: Callable[[Dict], bool], 
                            template: EmailTemplate, delay_range: tuple = (60, 300)):
        """Add auto-reply rule."""
        self.auto_reply_rules.append({
            "condition": condition,
            "template": template,
            "delay_range": delay_range,
        })
    
    async def check_mail(self, since: Optional[datetime] = None) -> List[Dict]:
        """Check for new emails."""
        mail = imaplib.IMAP4_SSL(self.config.imap_host, self.config.imap_port)
        mail.login(self.config.imap_user, self.config.imap_pass)
        mail.select("INBOX")
        
        criteria = "UNSEEN"
        if since:
            criteria = f'(SINCE "{since.strftime("%d-%b-%Y")}")'
        
        status, messages = mail.search(None, criteria)
        results = []
        
        for num in messages[0].split():
            status, msg_data = mail.fetch(num, "(RFC822)")
            raw = msg_data[0][1]
            parsed = self._parse_email(raw)
            parsed["uid"] = num.decode()
            results.append(parsed)
            
            # Check auto-reply rules
            await self._process_auto_reply(parsed, mail, num)
        
        mail.logout()
        return results
    
    def _parse_email(self, raw: bytes) -> Dict:
        """Parse raw email to dict."""
        msg = email.message_from_bytes(raw)
        
        def decode_mime_header(header):
            if not header:
                return ""
            parts = decode_header(header)
            return "".join(
                part[0].decode(part[1] or "utf-8") if isinstance(part[0], bytes) else part[0]
                for part in parts
            )
        
        body = ""
        html_body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                ct = part.get_content_type()
                disp = part.get("Content-Disposition", "")
                if ct == "text/plain" and "attachment" not in disp:
                    body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8")
                elif ct == "text/html" and "attachment" not in disp:
                    html_body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8")
        else:
            body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8")
        
        return {
            "from": decode_mime_header(msg.get("From", "")),
            "to": decode_mime_header(msg.get("To", "")),
            "subject": decode_mime_header(msg.get("Subject", "")),
            "date": msg.get("Date", ""),
            "message_id": msg.get("Message-ID", ""),
            "body": body,
            "html_body": html_body,
            "references": msg.get("References", ""),
            "in_reply_to": msg.get("In-Reply-To", ""),
        }
    
    async def _process_auto_reply(self, parsed: Dict, mail: imaplib.IMAP4_SSL, uid: bytes):
        """Check rules and send auto-reply."""
        for rule in self.auto_reply_rules:
            if rule["condition"](parsed):
                # Send reply
                template = rule["template"]
                rendered = template.render({"original": parsed})
                
                # Create reply
                reply = MIMEText(rendered["text"], "plain", "utf-8")
                reply["From"] = self.config.imap_user
                reply["To"] = parsed["from"]
                reply["Subject"] = f"Re: {parsed['subject']}"
                reply["In-Reply-To"] = parsed["message_id"]
                reply["References"] = parsed["references"] + " " + parsed["message_id"]
                
                # Send via SMTP (would use SMTPSender)
                # For now just log
                print(f"Auto-reply to {parsed['from']}: {rendered['subject']}")
                
                # Mark as read
                mail.store(uid, "+FLAGS", "\\Seen")
                break


# =============================================================================
# EMAIL DATABASE
# =============================================================================

class EmailDB:
    """SQLite database for email configs, templates, sent history."""
    
    def __init__(self, db_path: str = "email_automation.db", key: Optional[bytes] = None):
        self.db_path = db_path
        self.key = key or (Fernet.generate_key() if CRYPTO_AVAILABLE else None)
        self.cipher = Fernet(self.key) if CRYPTO_AVAILABLE and self.key else None
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS email_configs (
                    identity_id TEXT PRIMARY KEY,
                    config_data TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS email_templates (
                    name TEXT PRIMARY KEY,
                    subject TEXT,
                    html_body TEXT,
                    text_body TEXT,
                    tracking_pixel INTEGER DEFAULT 1,
                    click_tracking INTEGER DEFAULT 1,
                    utm_params TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sent_emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tracking_id TEXT,
                    identity_id TEXT,
                    to_addr TEXT,
                    subject TEXT,
                    template_name TEXT,
                    status TEXT,
                    error TEXT,
                    sent_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS received_emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    identity_id TEXT,
                    message_id TEXT,
                    from_addr TEXT,
                    subject TEXT,
                    body TEXT,
                    received_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tracking_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tracking_id TEXT,
                    event_type TEXT,  -- open, click, bounce, complaint
                    ip TEXT,
                    user_agent TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def save_config(self, config: EmailConfig):
        data = json.dumps(asdict(config))
        encrypted = self.cipher.encrypt(data.encode()).decode() if self.cipher else data
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO email_configs (identity_id, config_data, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (config.smtp_user, encrypted))
            conn.commit()
    
    def load_config(self, identity_id: str) -> Optional[EmailConfig]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT config_data FROM email_configs WHERE identity_id = ?", 
                (identity_id,)
            ).fetchone()
            if row:
                data = row["config_data"]
                if self.cipher:
                    data = self.cipher.decrypt(data.encode()).decode()
                return EmailConfig(**json.loads(data))
        return None
    
    def save_template(self, template: EmailTemplate):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO email_templates 
                (name, subject, html_body, text_body, tracking_pixel, click_tracking, utm_params)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (template.name, template.subject, template.html_body, template.text_body,
                  int(template.tracking_pixel), int(template.click_tracking), 
                  json.dumps(template.utm_params)))
            conn.commit()
    
    def load_template(self, name: str) -> Optional[EmailTemplate]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM email_templates WHERE name = ?", (name,)
            ).fetchone()
            if row:
                return EmailTemplate(
                    name=row["name"],
                    subject=row["subject"],
                    html_body=row["html_body"],
                    text_body=row["text_body"],
                    tracking_pixel=bool(row["tracking_pixel"]),
                    click_tracking=bool(row["click_tracking"]),
                    utm_params=json.loads(row["utm_params"] or "{}"),
                )
        return None
    
    def log_sent(self, tracking_id: str, identity_id: str, to_addr: str, 
                 subject: str, template: str, status: str, error: str = None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO sent_emails (tracking_id, identity_id, to_addr, subject, template_name, status, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tracking_id, identity_id, to_addr, subject, template, status, error))
            conn.commit()
    
    def log_received(self, identity_id: str, parsed: Dict):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO received_emails (identity_id, message_id, from_addr, subject, body)
                VALUES (?, ?, ?, ?, ?)
            """, (identity_id, parsed["message_id"], parsed["from"], parsed["subject"], parsed["body"]))
            conn.commit()
    
    def log_tracking(self, tracking_id: str, event_type: str, ip: str = "", ua: str = ""):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO tracking_events (tracking_id, event_type, ip, user_agent)
                VALUES (?, ?, ?, ?)
            """, (tracking_id, event_type, ip, ua))
            conn.commit()


# =============================================================================
# EMAIL AUTOMATION ORCHESTRATOR
# =============================================================================

class EmailAutomation:
    """High-level email automation for an identity."""
    
    def __init__(self, identity_id: str, db: EmailDB):
        self.identity_id = identity_id
        self.db = db
        self.config = db.load_config(identity_id)
        if not self.config:
            raise ValueError(f"No email config for {identity_id}")
        
        self.sender = SMTPSender(self.config, db)
        self.receiver = IMAPReceiver(self.config, db)
        self.tracking = TrackingEngine()
        self.templates: Dict[str, EmailTemplate] = {}
    
    def load_template(self, name: str) -> EmailTemplate:
        if name not in self.templates:
            tpl = self.db.load_template(name)
            if not tpl:
                raise ValueError(f"Template {name} not found")
            self.templates[name] = tpl
        return self.templates[name]
    
    async def send_templated(self, template_name: str, to: str, context: Dict[str, Any],
                              from_name: str = "", utm: Dict = None) -> EmailResult:
        """Send email from template with context."""
        template = self.load_template(template_name)
        rendered = template.render(context)
        
        # Add tracking
        tracking_id = hashlib.md5(f"{to}{datetime.now()}".encode()).hexdigest()[:8]
        
        if template.tracking_pixel:
            pixel = self.tracking.generate_pixel(tracking_id, context.get("campaign", ""))
            rendered["html"] = rendered["html"].replace("</body>", f"{pixel}</body>")
        
        if template.click_tracking:
            rendered["html"] = self.tracking.wrap_links(rendered["html"], tracking_id, 
                                                         context.get("campaign", ""))
        
        # Add UTM
        if utm or template.utm_params:
            all_utm = {**template.utm_params, **(utm or {})}
            # Would need to parse HTML and add to links - simplified
        
        message = EmailMessage(
            to=to,
            subject=rendered["subject"],
            html=rendered["html"],
            text=rendered["text"],
            from_name=from_name,
            tracking_id=tracking_id,
        )
        
        result = await self.sender.send(message)
        self.db.log_sent(tracking_id, self.identity_id, to, rendered["subject"], 
                         template_name, "sent" if result.success else "failed", result.error)
        return result
    
    async def warmup_sequence(self, contacts: List[str], template_name: str = "warmup"):
        """Send warmup emails to contacts."""
        template = self.load_template(template_name)
        
        for contact in contacts:
            context = {"name": contact.split("@")[0], "campaign": "warmup"}
            await self.send_templated(template_name, contact, context, from_name="Warmup")
            await asyncio.sleep(random.uniform(300, 900))  # 5-15 min between
    
    async def check_replies(self):
        """Check for new emails and process."""
        emails = await self.receiver.check_mail()
        for email in emails:
            self.db.log_received(self.identity_id, email)
        return emails


# =============================================================================
# BUILT-IN TEMPLATES
# =============================================================================

DEFAULT_TEMPLATES = {
    "warmup": EmailTemplate(
        name="warmup",
        subject="Hey {{ name }}, quick question",
        html_body="""
        <html><body>
        <p>Hey {{ name }},</p>
        <p>Just wanted to reach out and see how things are going. 
        Been following your work and thought I'd say hi.</p>
        <p>No pitch, no ask - just genuine curiosity.</p>
        <p>Best,<br>{{ sender_name }}</p>
        </body></html>
        """,
        text_body="""
        Hey {{ name }},
        
        Just wanted to reach out and see how things are going. 
        Been following your work and thought I'd say hi.
        
        No pitch, no ask - just genuine curiosity.
        
        Best,
        {{ sender_name }}
        """,
    ),
    "outreach_cpa": EmailTemplate(
        name="outreach_cpa",
        subject="Partnership opportunity: {{ offer_name }} for {{ geo }} traffic",
        html_body="""
        <html><body>
        <p>Hi {{ name }},</p>
        <p>I'm reaching out because I have a {{ offer_name }} offer that's converting really well in {{ geo }}.</p>
        <p>Quick specs:</p>
        <ul>
        <li>Payout: ${{ payout }}</li>
        <li>Conversion: {{ cr }}%</li>
        <li>Cap: {{ cap }}/day</li>
        <li>Payments: {{ payment_terms }}</li>
        </ul>
        <p>If you have {{ geo }} traffic (TikTok/Shorts/Native), this could be a solid fit.</p>
        <p>Open to test with a small budget first?</p>
        <p>Best,<br>{{ sender_name }}</p>
        </body></html>
        """,
        text_body="""
        Hi {{ name }},
        
        I'm reaching out because I have a {{ offer_name }} offer that's converting really well in {{ geo }}.
        
        Quick specs:
        - Payout: ${{ payout }}
        - Conversion: {{ cr }}%
        - Cap: {{ cap }}/day
        - Payments: {{ payment_terms }}
        
        If you have {{ geo }} traffic (TikTok/Shorts/Native), this could be a solid fit.
        
        Open to test with a small budget first?
        
        Best,
        {{ sender_name }}
        """,
        utm_params={"source": "email", "medium": "outreach", "campaign": "cpa_partnership"},
    ),
    "followup_1": EmailTemplate(
        name="followup_1",
        subject="Re: {{ original_subject }}",
        html_body="""
        <html><body>
        <p>Hey {{ name }},</p>
        <p>Just floating this to the top of your inbox - didn't want you to miss it.</p>
        <p>The {{ offer_name }} offer in {{ geo }} is still open for a test run.</p>
        <p>Let me know if you want the link.</p>
        <p>Best,<br>{{ sender_name }}</p>
        </body></html>
        """,
        text_body="""
        Hey {{ name }},
        
        Just floating this to the top of your inbox - didn't want you to miss it.
        The {{ offer_name }} offer in {{ geo }} is still open for a test run.
        
        Let me know if you want the link.
        
        Best,
        {{ sender_name }}
        """,
    ),
}


# =============================================================================
# TEST
# =============================================================================

def test_templates():
    print("=== EMAIL TEMPLATE TEST ===")
    
    for name, tpl in DEFAULT_TEMPLATES.items():
        context = {
            "name": "Alex",
            "sender_name": "Mike",
            "offer_name": "1xBet India",
            "geo": "India",
            "payout": "45",
            "cr": "12",
            "cap": "500",
            "payment_terms": "Net-7, USDT",
            "original_subject": "Partnership opportunity",
            "campaign": "cpa_partnership",
        }
        rendered = tpl.render(context)
        print(f"\nTemplate: {name}")
        print(f"Subject: {rendered['subject']}")
        print(f"Text preview: {rendered['text'][:100]}...")


if __name__ == "__main__":
    test_templates()