"""Core search module for Crimea Job Search."""
import asyncio
import aiohttp
import json
import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from urllib.parse import urlencode
import yaml


@dataclass
class Vacancy:
    id: str
    name: str
    company: str
    city: str
    salary_from: Optional[int]
    salary_to: Optional[int]
    currency: str
    experience: str
    schedule: str
    employment: str
    description: str
    skills: List[str]
    published_at: datetime
    url: str
    is_new: bool = False
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['published_at'] = self.published_at.isoformat() if self.published_at else None
        return d
    
    def salary_str(self) -> str:
        if self.salary_from and self.salary_to:
            return f"{self.salary_from:,} - {self.salary_to:,} {self.currency}"
        elif self.salary_from:
            return f"от {self.salary_from:,} {self.currency}"
        elif self.salary_to:
            return f"до {self.salary_to:,} {self.currency}"
        return "Не указана"


class HHApiClient:
    """Async hh.ru API client with rate limiting."""
    
    BASE_URL = "https://api.hh.ru"
    
    def __init__(self, user_agent: str = "Hermes-Agent-Crimea-Job-Search/1.0", 
                 rate_limit: int = 200, timeout: int = 30):
        self.user_agent = user_agent
        self.rate_limit = rate_limit  # requests per minute
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self._semaphore = asyncio.Semaphore(rate_limit // 60 + 1)
        self._last_request = 0
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "User-Agent": self.user_agent,
                    "Accept": "application/json",
                    "Accept-Language": "ru_RU",
                },
                timeout=self.timeout
            )
        return self._session
    
    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _rate_limit(self):
        """Enforce rate limit."""
        async with self._semaphore:
            now = asyncio.get_event_loop().time()
            elapsed = now - self._last_request
            min_interval = 60.0 / self.rate_limit
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            self._last_request = asyncio.get_event_loop().time()
    
    async def get_vacancies(self, params: Dict[str, Any]) -> Dict:
        """Fetch vacancies from hh.ru API."""
        await self._rate_limit()
        
        session = await self._get_session()
        url = f"{self.BASE_URL}/vacancies"
        
        async with session.get(url, params=params) as resp:
            if resp.status == 429:
                retry_after = int(resp.headers.get("Retry-After", 60))
                await asyncio.sleep(retry_after)
                return await self.get_vacancies(params)
            
            resp.raise_for_status()
            return await resp.json()
    
    async def get_vacancy_details(self, vacancy_id: str) -> Dict:
        """Fetch full vacancy details."""
        await self._rate_limit()
        
        session = await self._get_session()
        url = f"{self.BASE_URL}/vacancies/{vacancy_id}"
        
        async with session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()
    
    async def get_areas(self) -> List[Dict]:
        """Get all areas (regions/cities)."""
        await self._rate_limit()
        
        session = await self._get_session()
        url = f"{self.BASE_URL}/areas"
        
        async with session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()


class VacancyCache:
    """SQLite cache for vacancy deduplication."""
    
    def __init__(self, db_path: str, ttl_hours: int = 24, max_entries: int = 10000):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.ttl_hours = ttl_hours
        self.max_entries = max_entries
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vacancies (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    seen_count INTEGER DEFAULT 1
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fetched_at ON vacancies(fetched_at)
            """)
            conn.commit()
    
    def is_new(self, vacancy_id: str) -> bool:
        """Check if vacancy is new (not in cache)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM vacancies WHERE id = ?", (vacancy_id,)
            )
            return cursor.fetchone() is None
    
    def save(self, vacancy: Vacancy):
        """Save vacancy to cache."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT OR REPLACE INTO vacancies (id, data, fetched_at, seen_count)
                   VALUES (?, ?, ?, 
                       COALESCE((SELECT seen_count FROM vacancies WHERE id = ?), 0) + 1)""",
                (vacancy.id, json.dumps(vacancy.to_dict()), datetime.now().isoformat(), vacancy.id)
            )
            conn.commit()
    
    def cleanup_old(self):
        """Remove entries older than TTL."""
        cutoff = datetime.now() - timedelta(hours=self.ttl_hours)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM vacancies WHERE fetched_at < ?", (cutoff.isoformat(),)
            )
            # Also enforce max_entries
            conn.execute("""
                DELETE FROM vacancies 
                WHERE id IN (
                    SELECT id FROM vacancies 
                    ORDER BY fetched_at DESC 
                    LIMIT -1 OFFSET ?
                )
            """, (self.max_entries,))
            conn.commit()
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM vacancies")
            total = cursor.fetchone()[0]
            
            cursor = conn.execute(
                "SELECT COUNT(*) FROM vacancies WHERE fetched_at > ?",
                ((datetime.now() - timedelta(hours=24)).isoformat(),)
            )
            recent = cursor.fetchone()[0]
            
            return {"total": total, "recent_24h": recent}


class VacancyFilter:
    """Filter vacancies by criteria."""
    
    def __init__(self, config: Dict):
        self.keywords = [k.strip().lower() for k in config.get("keywords", "").split(",") if k.strip()]
        self.salary_min = config.get("salary_min")
        self.salary_max = config.get("salary_max")
        self.experience = set(config.get("experience", "").split(",")) if config.get("experience") else set()
        self.schedule = set(config.get("schedule", "").split(",")) if config.get("schedule") else set()
        self.employment = set(config.get("employment", "").split(",")) if config.get("employment") else set()
        self.city = config.get("city", "").lower()
    
    def matches(self, vacancy: Vacancy) -> bool:
        # Keywords in name or description
        if self.keywords:
            text = f"{vacancy.name} {vacancy.description}".lower()
            if not any(kw in text for kw in self.keywords):
                return False
        
        # Salary filter
        if self.salary_min and vacancy.salary_from:
            if vacancy.salary_from < self.salary_min:
                return False
        if self.salary_max and vacancy.salary_to:
            if vacancy.salary_to > self.salary_max:
                return False
        
        # Experience
        if self.experience and vacancy.experience not in self.experience:
            return False
        
        # Schedule
        if self.schedule and vacancy.schedule not in self.schedule:
            return False
        
        # Employment
        if self.employment and vacancy.employment not in self.employment:
            return False
        
        # City
        if self.city and self.city not in vacancy.city.lower():
            return False
        
        return True


def parse_vacancy(data: Dict, cache: Optional[VacancyCache] = None) -> Vacancy:
    """Parse hh.ru vacancy JSON to Vacancy object."""
    salary = data.get("salary") or {}
    snippet = data.get("snippet") or {}
    experience = data.get("experience") or {}
    schedule = data.get("schedule") or {}
    employment = data.get("employment") or {}
    area = data.get("area") or {}
    employer = data.get("employer") or {}
    professional_roles = data.get("professional_roles") or []
    key_skills = data.get("key_skills") or []
    
    # Parse published date
    published_at = None
    if data.get("published_at"):
        try:
            published_at = datetime.fromisoformat(data["published_at"].replace("Z", "+00:00"))
        except:
            pass
    
    is_new = False
    if cache:
        is_new = cache.is_new(data["id"])
    
    return Vacancy(
        id=str(data["id"]),
        name=data.get("name", ""),
        company=employer.get("name", ""),
        city=area.get("name", ""),
        salary_from=salary.get("from"),
        salary_to=salary.get("to"),
        currency=salary.get("currency", "RUR"),
        experience=experience.get("id", ""),
        schedule=schedule.get("id", ""),
        employment=employment.get("id", ""),
        description=snippet.get("requirement", "") + " " + snippet.get("responsibility", ""),
        skills=[s.get("name", "") for s in key_skills],
        published_at=published_at,
        url=data.get("alternate_url", ""),
        is_new=is_new
    )


class JobSearchCLI:
    """Main CLI for job search."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.client = HHApiClient(
            user_agent=self.config.get("hh_api", {}).get("user_agent", "Hermes-Agent/1.0"),
            rate_limit=self.config.get("hh_api", {}).get("rate_limit", 200),
            timeout=self.config.get("hh_api", {}).get("timeout", 30)
        )
        cache_config = self.config.get("cache", {})
        self.cache = VacancyCache(
            db_path=cache_config.get("db_path", "cache/vacancies.db"),
            ttl_hours=cache_config.get("ttl_hours", 24),
            max_entries=cache_config.get("max_entries", 10000)
        )
        self.filter = VacancyFilter(self.config.get("search", {}))
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        default_config = {
            "hh_api": {
                "base_url": "https://api.hh.ru",
                "user_agent": "Hermes-Agent-Crimea-Job-Search/1.0",
                "rate_limit": 200,
                "timeout": 30
            },
            "search": {
                "default_area": 1002,
                "cities": ["Симферополь", "Севастополь", "Керчь", "Евпатория", "Феодосия"],
                "default_keywords": "python,django,fastapi,backend,api",
                "salary_min": 80000,
                "experience": "between1And3,between3And6",
                "schedule": "remote,flexible",
                "employment": "full,part"
            },
            "cache": {
                "db_path": "cache/vacancies.db",
                "ttl_hours": 24,
                "max_entries": 10000
            },
            "notify": {
                "telegram_enabled": True,
                "telegram_chat_id": "737433175"
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f)
                # Deep merge
                for key, value in user_config.items():
                    if key in default_config and isinstance(value, dict):
                        default_config[key].update(value)
                    else:
                        default_config[key] = value
        
        return default_config
    
    async def test_connection(self) -> bool:
        """Test API connectivity."""
        try:
            result = await self.client.get_vacancies({
                "area": 1002,
                "per_page": 1,
                "page": 0
            })
            print(f"✅ API connection OK. Found {result.get('found', 0)} vacancies in Crimea")
            return True
        except Exception as e:
            print(f"❌ API connection failed: {e}")
            return False
    
    async def search_once(self, args) -> List[Vacancy]:
        """Execute single search."""
        keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
        
        params = {
            "area": args.area,
            "text": " OR ".join(keywords),
            "page": args.page,
            "per_page": min(args.per_page, 100),
            "order_by": "publication_time",
            "search_field": ["name", "description"]
        }
        
        if args.salary_min:
            params["salary"] = args.salary_min
            params["only_with_salary"] = True
        
        if args.experience:
            params["experience"] = args.experience
        
        if args.schedule:
            params["schedule"] = args.schedule
        
        if args.employment:
            params["employment"] = args.employment
        
        print(f"🔍 Searching: {args.keywords} in {args.city} (salary ≥ {args.salary_min})...")
        
        result = await self.client.get_vacancies(params)
        vacancies_data = result.get("items", [])
        total_found = result.get("found", 0)
        
        print(f"📊 Total found: {total_found}, fetched: {len(vacancies_data)}")
        
        # Parse and filter
        vacancies = []
        new_count = 0
        
        for v_data in vacancies_data:
            vacancy = parse_vacancy(v_data, self.cache if args.new_only else None)
            
            if args.new_only and not vacancy.is_new:
                continue
            
            if vacancy.is_new:
                new_count += 1
            
            if self.filter.matches(vacancy):
                vacancies.append(vacancy)
                if args.new_only or not hasattr(args, 'skip_cache_save'):
                    self.cache.save(vacancy)
        
        print(f"✅ Matched: {len(vacancies)} (new: {new_count})")
        
        # Output
        await self._output(vacancies, args)
        
        return vacancies
    
    async def _output(self, vacancies: List[Vacancy], args):
        """Output vacancies in specified format."""
        if args.output == "json":
            data = [v.to_dict() for v in vacancies]
            output = json.dumps(data, ensure_ascii=False, indent=2)
        elif args.output == "csv":
            import csv
            import io
            output_io = io.StringIO()
            if vacancies:
                writer = csv.DictWriter(output_io, fieldnames=vacancies[0].to_dict().keys())
                writer.writeheader()
                for v in vacancies:
                    writer.writerow(v.to_dict())
            output = output_io.getvalue()
        else:  # table
            if not vacancies:
                output = "No vacancies found matching criteria."
            else:
                lines = []
                for i, v in enumerate(vacancies, 1):
                    new_flag = " 🆕" if v.is_new else ""
                    lines.append(
                        f"{i:2d}. {v.name[:50]:50s} | {v.company[:30]:30s} | "
                        f"{v.city:15s} | {v.salary_str():>20s} | {v.experience:12s}{new_flag}"
                    )
                output = "\n".join(lines)
        
        if args.file:
            Path(args.file).write_text(output, encoding="utf-8")
            print(f"💾 Saved to {args.file}")
        else:
            print(output)
    
    async def run_daemon(self, args):
        """Run continuous polling."""
        print(f"🔄 Daemon mode: polling every {args.interval}s")
        print("Press Ctrl+C to stop")
        
        while True:
            try:
                await self.search_once(args)
                self.cache.cleanup_old()
            except KeyboardInterrupt:
                print("\n👋 Stopping daemon...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
            
            await asyncio.sleep(args.interval)
    
    async def close(self):
        await self.client.close()