#!/usr/bin/env python3
"""
Account Registration Module — Auto-register accounts on any platform.
Form filling, email/SMS verification, CAPTCHA solving, credential storage.
"""

import asyncio
import json
import random
import re
import sqlite3
import string
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from cryptography.fernet import Fernet

# Playwright
try:
    from playwright.async_api import Page, Locator
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class AccountProfile:
    """Generated profile for account registration."""
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    phone: Optional[str] = None
    birth_date: Optional[str] = None  # YYYY-MM-DD
    gender: Optional[str] = None      # male/female/other
    address: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RegistrationResult:
    """Result of registration attempt."""
    success: bool
    platform: str
    profile: Optional[AccountProfile] = None
    identity_id: Optional[str] = None
    error: Optional[str] = None
    captcha_solved: bool = False
    email_verified: bool = False
    phone_verified: bool = False
    credentials_saved: bool = False
    raw_response: Optional[str] = None


# =============================================================================
# PROFILE GENERATOR
# =============================================================================

class ProfileGenerator:
    """Generates realistic account profiles."""
    
    FIRST_NAMES_MALE = [
        "Alexander", "Dmitry", "Maxim", "Ivan", "Artem", "Nikita", "Mikhail", "Danil",
        "Alex", "Chris", "Mike", "John", "David", "James", "Robert", "William",
        "Александр", "Дмитрий", "Максим", "Иван", "Артём", "Никита", "Михаил", "Данил",
    ]
    
    FIRST_NAMES_FEMALE = [
        "Anna", "Maria", "Elena", "Olga", "Natalia", "Svetlana", "Yulia", "Ekaterina",
        "Emily", "Sarah", "Jessica", "Jennifer", "Lisa", "Amanda", "Stephanie", "Melissa",
        "Анна", "Мария", "Елена", "Ольга", "Наталья", "Светлана", "Юлия", "Екатерина",
    ]
    
    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Иванов", "Смирнов", "Кузнецов", "Попов", "Васильев", "Петров", "Соколов", "Михайлов",
        "Novak", "Kowalski", "Schmidt", "Müller", "Rossi", "Garcia", "Martinez",
    ]
    
    DOMAINS = [
        "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "proton.me",
        "mail.ru", "yandex.ru", "rambler.ru", "icloud.com", "pm.me",
    ]
    
    def __init__(self, seed: Optional[int] = None):
        self.rng = random.Random(seed)
    
    def generate(self, locale: str = "mixed", gender: Optional[str] = None) -> AccountProfile:
        """Generate a complete account profile."""
        
        if gender is None:
            gender = self.rng.choice(["male", "female"])
        
        if gender == "male":
            first_name = self.rng.choice(self.FIRST_NAMES_MALE)
        else:
            first_name = self.rng.choice(self.FIRST_NAMES_FEMALE)
        
        last_name = self.rng.choice(self.LAST_NAMES)
        
        # Username: firstname + lastname + numbers
        username_base = f"{first_name.lower()}{last_name.lower()}"
        username_base = re.sub(r'[^a-z0-9]', '', username_base)
        username = f"{username_base}{self.rng.randint(10, 9999)}"
        
        # Email
        domain = self.rng.choice(self.DOMAINS)
        email = f"{username}@{domain}"
        
        # Password: strong but memorable pattern
        password = self._generate_password()
        
        # Phone (Russian format for now)
        phone = f"+7{self.rng.randint(900, 999)}{self.rng.randint(1000000, 9999999)}"
        
        # Birth date (18-60 years old)
        from datetime import date, timedelta
        today = date.today()
        years_ago = self.rng.randint(18, 60)
        birth_year = today.year - years_ago
        birth_month = self.rng.randint(1, 12)
        birth_day = self.rng.randint(1, 28)
        birth_date = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"
        
        return AccountProfile(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password,
            phone=phone,
            birth_date=birth_date,
            gender=gender,
        )
    
    def _generate_password(self) -> str:
        """Generate strong password."""
        length = self.rng.randint(12, 16)
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        # Ensure at least one of each type
        pwd = [
            self.rng.choice(string.ascii_uppercase),
            self.rng.choice(string.ascii_lowercase),
            self.rng.choice(string.digits),
            self.rng.choice("!@#$%^&*"),
        ]
        pwd += [self.rng.choice(chars) for _ in range(length - 4)]
        self.rng.shuffle(pwd)
        return "".join(pwd)


# =============================================================================
# FORM DETECTOR
# =============================================================================

class FormDetector:
    """ML-assisted form field detection."""
    
    FIELD_PATTERNS = {
        "email": [
            r"(email|e-mail|mail)", r"username.*email", r"login.*email",
            r"type=['\"]email['\"]", r"inputmode=['\"]email['\"]",
        ],
        "password": [
            r"password|passwd|pass", r"type=['\"]password['\"]",
            r"confirm.*password", r"repeat.*password",
        ],
        "username": [
            r"username|login|nickname|handle", r"user.*name",
            r"type=['\"]text['\"].*name=['\"]user",
        ],
        "first_name": [
            r"first.?name|fname|given.?name", r"name.*first",
        ],
        "last_name": [
            r"last.?name|lname|surname|family.?name", r"name.*last",
        ],
        "phone": [
            r"phone|mobile|tel|telephone", r"type=['\"]tel['\"]",
        ],
        "birth_date": [
            r"birth|dob|date.?of.?birth", r"birthday",
        ],
        "gender": [
            r"gender|sex", r"(male|female).*radio",
        ],
        "submit": [
            r"submit|register|sign.?up|create|join|continue|next",
            r"type=['\"]submit['\"]", r"button.*register",
        ],
    }
    
    def __init__(self):
        self.compiled = {k: [re.compile(p, re.I) for p in v] 
                         for k, v in self.FIELD_PATTERNS.items()}
    
    async def detect_fields(self, page) -> Dict[str, List[Locator]]:
        """Detect form fields on page."""
        fields = {k: [] for k in self.FIELD_PATTERNS.keys()}
        
        inputs = await page.locator("input, select, textarea").all()
        
        for input_el in inputs:
            # Get attributes
            attrs = {}
            for attr in ["type", "name", "id", "placeholder", "aria-label", "autocomplete"]:
                val = await input_el.get_attribute(attr)
                if val:
                    attrs[attr] = val.lower()
            
            # Also check label
            label_text = ""
            input_id = attrs.get("id", "")
            if input_id:
                label = await page.locator(f"label[for='{input_id}']").first.inner_text()
                label_text = label.lower() if label else ""
            
            # Combine all text for matching
            haystack = " ".join(list(attrs.values()) + [label_text])
            
            # Match against patterns
            for field_type, patterns in self.compiled.items():
                for pattern in patterns:
                    if pattern.search(haystack):
                        fields[field_type].append(input_el)
                        break
        
        return fields


# =============================================================================
# EMAIL VERIFICATION
# =============================================================================

class EmailVerifier:
    """Email verification via IMAP and temp-mail services."""
    
    TEMP_MAIL_APIS = {
        "1secmail": "https://www.1secmail.com/api/v1/",
        "tempmail": "https://api.temp-mail.io/api/v3/",
        "guerrillamail": "https://api.guerrillamail.com/ajax.php",
    }
    
    def __init__(self, imap_config: Optional[Dict] = None):
        self.imap_config = imap_config or {}
    
    async def verify_via_imap(self, email: str, password: str, 
                              sender_filter: Optional[str] = None,
                              timeout: int = 60) -> Optional[str]:
        """Check IMAP for verification link."""
        import imaplib
        import email
        import re
        
        # Parse email domain for IMAP server
        domain = email.split("@")[1]
        imap_server = self._get_imap_server(domain)
        
        if not imap_server:
            return None
        
        start = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start < timeout:
            try:
                mail = imaplib.IMAP4_SSL(imap_server)
                mail.login(email, password)
                mail.select("INBOX")
                
                # Search for unread emails from sender
                criteria = "UNSEEN"
                if sender_filter:
                    criteria += f' FROM "{sender_filter}"'
                
                status, messages = mail.search(None, criteria)
                
                if status == "OK" and messages[0]:
                    for num in messages[0].split()[-5:]:  # Last 5
                        status, data = mail.fetch(num, "(RFC822)")
                        if status == "OK":
                            msg = email.message_from_bytes(data[0][1])
                            
                            # Extract links
                            body = self._get_email_body(msg)
                            links = re.findall(r'https?://[^\s<>"]+', body)
                            
                            # Find verification link
                            for link in links:
                                if any(kw in link.lower() for kw in 
                                       ["verify", "confirm", "activate", "validate", "auth"]):
                                    mail.logout()
                                    return link
                
                mail.logout()
            except Exception as e:
                print(f"IMAP error: {e}")
            
            await asyncio.sleep(5)
        
        return None
    
    def _get_imap_server(self, domain: str) -> Optional[str]:
        servers = {
            "gmail.com": "imap.gmail.com",
            "yahoo.com": "imap.mail.yahoo.com",
            "outlook.com": "outlook.office365.com",
            "hotmail.com": "outlook.office365.com",
            "mail.ru": "imap.mail.ru",
            "yandex.ru": "imap.yandex.ru",
            "proton.me": "imap.proton.me",
            "icloud.com": "imap.mail.me.com",
        }
        return servers.get(domain)
    
    def _get_email_body(self, msg) -> str:
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() in ["text/plain", "text/html"]:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode(errors="ignore")
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(errors="ignore")
        return body
    
    async def verify_via_temp_mail(self, email: str, api: str = "1secmail") -> Optional[str]:
        """Verify using temp-mail API (for disposable emails)."""
        import aiohttp
        
        # Extract login from email
        login = email.split("@")[0]
        domain = email.split("@")[1]
        
        api_base = self.TEMP_MAIL_APIS.get(api)
        if not api_base:
            return None
        
        async with aiohttp.ClientSession() as session:
            # Check messages
            url = f"{api_base}?action=getMessages&login={login}&domain={domain}"
            async with session.get(url) as resp:
                if resp.status == 200:
                    messages = await resp.json()
                    for msg in messages:
                        if any(kw in msg.get("subject", "").lower() for kw in 
                               ["verify", "confirm", "activate"]):
                            # Get full message
                            msg_id = msg["id"]
                            url2 = f"{api_base}?action=readMessage&login={login}&domain={domain}&id={msg_id}"
                            async with session.get(url2) as resp2:
                                if resp2.status == 200:
                                    full = await resp2.json()
                                    body = full.get("body", "") or full.get("textBody", "")
                                    import re
                                    links = re.findall(r'https?://[^\s<>"]+', body)
                                    for link in links:
                                        if any(kw in link.lower() for kw in 
                                               ["verify", "confirm", "activate", "validate"]):
                                            return link
        return None


# =============================================================================
# SMS VERIFICATION
# =============================================================================

class SMSVerifier:
    """Phone verification via SMS APIs."""
    
    PROVIDERS = {
        "5sim": {
            "base": "https://5sim.net/v1",
            "buy": "/user/buy/activation/{country}/{operator}/{product}",
            "check": "/user/check/{id}",
            "cancel": "/user/cancel/{id}",
        },
        "sms_activate": {
            "base": "https://api.sms-activate.org/stubs/handler_api.php",
            "buy": "?api_key={key}&action=getNumber&service={service}&country={country}",
            "check": "?api_key={key}&action=getStatus&id={id}",
            "cancel": "?api_key={key}&action=setStatus&id={id}&status=8",
        },
    }
    
    def __init__(self, provider: str = "5sim", api_key: str = ""):
        self.provider = provider
        self.api_key = api_key
        self.config = self.PROVIDERS.get(provider, {})
    
    async def get_number(self, country: str = "russia", service: str = "any") -> Optional[Dict]:
        """Buy a phone number for verification."""
        import aiohttp
        
        if self.provider == "5sim":
            url = f"{self.config['base']}{self.config['buy'].format(country=country, operator='any', product=service)}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
        elif self.provider == "sms_activate":
            url = f"{self.config['base']}{self.config['buy'].format(key=self.api_key, service=service, country=0)}"
            headers = {}
        else:
            return None
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
        return None
    
    async def wait_for_code(self, order_id: str, timeout: int = 120) -> Optional[str]:
        """Wait for SMS code."""
        import aiohttp
        
        start = asyncio.get_event_loop().time()
        
        while asyncio.get_event_loop().time() - start < timeout:
            if self.provider == "5sim":
                url = f"{self.config['base']}{self.config['check'].format(id=order_id)}"
                headers = {"Authorization": f"Bearer {self.api_key}"}
            elif self.provider == "sms_activate":
                url = f"{self.config['base']}{self.config['check'].format(key=self.api_key, id=order_id)}"
                headers = {}
            else:
                return None
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if self.provider == "5sim":
                            if data.get("sms"):
                                return data["sms"][0]["code"]
                        elif self.provider == "sms_activate":
                            if "STATUS_OK" in str(data):
                                return data.split(":")[-1]
            
            await asyncio.sleep(5)
        
        return None
    
    async def cancel_order(self, order_id: str):
        """Cancel/return the number."""
        import aiohttp
        
        if self.provider == "5sim":
            url = f"{self.config['base']}{self.config['cancel'].format(id=order_id)}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
        elif self.provider == "sms_activate":
            url = f"{self.config['base']}{self.config['cancel'].format(key=self.api_key, id=order_id)}"
            headers = {}
        else:
            return
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                return resp.status == 200


# =============================================================================
# CAPTCHA SOLVER
# =============================================================================

class CaptchaSolver:
    """CAPTCHA solving via 2captcha, Anti-Captcha, CapMonster."""
    
    PROVIDERS = {
        "2captcha": {
            "base": "https://2captcha.com",
            "in": "/in.php",
            "res": "/res.php",
        },
        "anti_captcha": {
            "base": "https://api.anti-captcha.com",
            "create": "/createTask",
            "result": "/getTaskResult",
        },
        "capmonster": {
            "base": "https://api.capmonster.cloud",
            "create": "/createTask",
            "result": "/getTaskResult",
        },
    }
    
    def __init__(self, provider: str = "2captcha", api_key: str = ""):
        self.provider = provider
        self.api_key = api_key
        self.config = self.PROVIDERS.get(provider, {})
    
    async def solve_recaptcha_v2(self, sitekey: str, page_url: str, 
                                  invisible: bool = False) -> Optional[str]:
        """Solve reCAPTCHA v2."""
        import aiohttp
        
        if self.provider == "2captcha":
            return await self._solve_2captcha(sitekey, page_url, invisible)
        elif self.provider in ["anti_captcha", "capmonster"]:
            return await self._solve_anticaptcha(sitekey, page_url)
        return None
    
    async def _solve_2captcha(self, sitekey: str, page_url: str, invisible: bool) -> Optional[str]:
        import aiohttp
        
        params = {
            "key": self.api_key,
            "method": "userrecaptcha",
            "googlekey": sitekey,
            "pageurl": page_url,
            "invisible": 1 if invisible else 0,
            "json": 1,
        }
        
        async with aiohttp.ClientSession() as session:
            # Submit
            async with session.get(f"{self.config['base']}{self.config['in']}", params=params) as resp:
                data = await resp.json()
                if data.get("status") != 1:
                    return None
                captcha_id = data["request"]
            
            # Poll for result
            for _ in range(30):
                await asyncio.sleep(5)
                params = {"key": self.api_key, "action": "get", "id": captcha_id, "json": 1}
                async with session.get(f"{self.config['base']}{self.config['res']}", params=params) as resp:
                    data = await resp.json()
                    if data.get("status") == 1:
                        return data["request"]
                    if data.get("request") == "CAPCHA_NOT_READY":
                        continue
                    return None
        return None
    
    async def _solve_anticaptcha(self, sitekey: str, page_url: str) -> Optional[str]:
        import aiohttp
        
        task = {
            "clientKey": self.api_key,
            "task": {
                "type": "NoCaptchaTaskProxyless",
                "websiteURL": page_url,
                "websiteKey": sitekey,
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.config['base']}{self.config['create']}", json=task) as resp:
                data = await resp.json()
                if data.get("errorId") != 0:
                    return None
                task_id = data["taskId"]
            
            for _ in range(30):
                await asyncio.sleep(5)
                async with session.post(f"{self.config['base']}{self.config['result']}", 
                                        json={"clientKey": self.api_key, "taskId": task_id}) as resp:
                    data = await resp.json()
                    if data.get("status") == "ready":
                        return data["solution"]["gRecaptchaResponse"]
                    if data.get("status") == "processing":
                        continue
                    return None
        return None


# =============================================================================
# REGISTRATION ORCHESTRATOR
# =============================================================================

class AccountRegistrar:
    """Orchestrates full account registration flow."""
    
    def __init__(self, identity_db, ghost_browser, behavior_engine):
        self.identity_db = identity_db
        self.ghost_browser = ghost_browser
        self.behavior = behavior_engine
        self.profile_gen = ProfileGenerator()
        self.form_detector = FormDetector()
        self.email_verifier = EmailVerifier()
        self.sms_verifier = SMSVerifier()
        self.captcha_solver = CaptchaSolver()
    
    async def register(self, platform: str, registration_config: Dict) -> RegistrationResult:
        """Register account on platform using config."""
        
        # Generate profile
        profile = self.profile_gen.generate(
            locale=registration_config.get("locale", "mixed"),
            gender=registration_config.get("gender")
        )
        
        # Launch browser with identity
        async with self.ghost_browser as browser:
            page = browser.page
            
            # Navigate to registration page
            await page.goto(registration_config["url"], wait_until="networkidle")
            await asyncio.sleep(random.uniform(1, 3))
            
            # Detect form fields
            fields = await self.form_detector.detect_fields(page)
            
            # Fill form
            await self._fill_registration_form(page, fields, profile, registration_config)
            
            # Handle CAPTCHA if present
            captcha_solved = await self._handle_captcha(page, registration_config)
            
            # Submit
            await self._submit_form(page, fields)
            
            # Wait for result
            await asyncio.sleep(3)
            
            # Check for email verification
            email_verified = False
            if registration_config.get("verify_email"):
                email_verified = await self._verify_email(page, profile, registration_config)
            
            # Check for phone verification
            phone_verified = False
            if registration_config.get("verify_phone"):
                phone_verified = await self._verify_phone(page, profile, registration_config)
            
            # Save credentials
            credentials_saved = False
            if email_verified or phone_verified or not registration_config.get("require_verification"):
                credentials_saved = await self._save_credentials(browser.identity, platform, profile)
            
            return RegistrationResult(
                success=True,
                platform=platform,
                profile=profile,
                identity_id=browser.identity.id,
                captcha_solved=captcha_solved,
                email_verified=email_verified,
                phone_verified=phone_verified,
                credentials_saved=credentials_saved,
            )
    
    async def _fill_registration_form(self, page: Page, fields: Dict, 
                                       profile: AccountProfile, config: Dict):
        """Fill detected form fields."""
        field_mapping = {
            "email": profile.email,
            "password": profile.password,
            "username": profile.username,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "phone": profile.phone,
            "birth_date": profile.birth_date,
        }
        
        for field_type, value in field_mapping.items():
            if not value:
                continue
            if field_type in fields and fields[field_type]:
                await self.behavior.typing.type(page, fields[field_type][0], value)
                await asyncio.sleep(random.uniform(0.2, 0.5))
        
        # Handle gender radio
        if "gender" in fields and fields["gender"] and profile.gender:
            for radio in fields["gender"]:
                val = await radio.get_attribute("value")
                if val and profile.gender.lower() in val.lower():
                    await radio.click()
                    break
    
    async def _handle_captcha(self, page: Page, config: Dict) -> bool:
        """Detect and solve CAPTCHA."""
        # Check for reCAPTCHA
        recaptcha = await page.locator(".g-recaptcha, [data-sitekey]").first
        if await recaptcha.count() > 0:
            sitekey = await recaptcha.get_attribute("data-sitekey")
            if sitekey:
                solution = await self.captcha_solver.solve_recaptcha_v2(
                    sitekey, page.url
                )
                if solution:
                    # Inject solution
                    await page.evaluate(f"""
                        document.getElementById('g-recaptcha-response').innerHTML = '{solution}';
                        if (typeof ___grecaptcha_cfg !== 'undefined') {{
                            Object.entries(___grecaptcha_cfg.clients).forEach(([k, v]) => {{
                                if (v.callback) v.callback('{solution}');
                            }});
                        }}
                    """)
                    return True
        return False
    
    async def _submit_form(self, page: Page, fields: Dict):
        """Submit registration form."""
        if "submit" in fields and fields["submit"]:
            await self.behavior.mouse.click(page)
            await fields["submit"][0].click()
        else:
            # Try pressing Enter on last field
            await page.keyboard.press("Enter")
    
    async def _verify_email(self, page: Page, profile: AccountProfile, config: Dict) -> bool:
        """Verify email via IMAP or temp-mail."""
        # Try IMAP first
        link = await self.email_verifier.verify_via_imap(
            profile.email, profile.password,
            sender_filter=config.get("email_sender"),
            timeout=config.get("email_timeout", 120)
        )
        
        if link:
            await page.goto(link)
            await asyncio.sleep(2)
            return True
        
        # Try temp-mail
        link = await self.email_verifier.verify_via_temp_mail(profile.email)
        if link:
            await page.goto(link)
            await asyncio.sleep(2)
            return True
        
        return False
    
    async def _verify_phone(self, page: Page, profile: AccountProfile, config: Dict) -> bool:
        """Verify phone via SMS API."""
        # This would require the platform to show the code input
        # and us to have bought a number beforehand
        # Simplified implementation
        return False
    
    async def _save_credentials(self, identity, platform: str, profile: AccountProfile) -> bool:
        """Save credentials to identity."""
        identity.credentials[platform] = {
            "email": profile.email,
            "password": profile.password,
            "username": profile.username,
            "phone": profile.phone or "",
        }
        self.identity_db.save(identity)
        return True


# =============================================================================
# PLATFORM CONFIGS (Examples)
# =============================================================================

PLATFORM_CONFIGS = {
    "tiktok": {
        "url": "https://www.tiktok.com/signup",
        "verify_email": True,
        "verify_phone": True,
        "email_sender": "noreply@tiktok.com",
        "email_timeout": 120,
        "require_verification": True,
    },
    "youtube": {
        "url": "https://accounts.google.com/signup",
        "verify_email": True,
        "verify_phone": True,
        "email_sender": "noreply@google.com",
        "email_timeout": 180,
        "require_verification": True,
    },
    "instagram": {
        "url": "https://www.instagram.com/accounts/emailsignup/",
        "verify_email": True,
        "verify_phone": True,
        "email_sender": "security@mail.instagram.com",
        "email_timeout": 120,
        "require_verification": True,
    },
    "telegram": {
        "url": "https://my.telegram.org/auth",
        "verify_phone": True,
        "require_verification": True,
    },
    "protonmail": {
        "url": "https://account.proton.me/signup",
        "verify_email": False,
        "require_verification": False,
    },
    "cpagrip": {
        "url": "https://www.cpagrip.com/register",
        "verify_email": True,
        "email_sender": "noreply@cpagrip.com",
        "require_verification": True,
    },
}


# =============================================================================
# TEST
# =============================================================================

def test_profile_generator():
    print("=== PROFILE GENERATOR TEST ===")
    pg = ProfileGenerator(seed=42)
    for i in range(3):
        profile = pg.generate()
        print(f"\nProfile {i+1}:")
        print(f"  Name: {profile.first_name} {profile.last_name}")
        print(f"  Username: {profile.username}")
        print(f"  Email: {profile.email}")
        print(f"  Phone: {profile.phone}")
        print(f"  Birth: {profile.birth_date}")
        print(f"  Gender: {profile.gender}")


if __name__ == "__main__":
    test_profile_generator()