#!/usr/bin/env python3
"""
Audience Analyzer — Main CLI
Two modes: audience2offer (audience → offer ideas) and offer2audience (offer → target audience)
"""

import argparse
import sys
import yaml
import json
import asyncio
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
import re

# Add skills to path
SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR))

# Import human-source modules for values map and ripple engine
from skills.human_source.scripts.analyze import (
    HumanAnalyzer, HumanProfile, HumanDimension, Key, RippleCircle, ValueConflict
)


@dataclass
class ParsedContent:
    """Content parsed from a source."""
    source_type: str
    source_url: str
    title: str
    items: List[Dict]  # posts, videos, comments, etc.
    metadata: Dict = field(default_factory=dict)
    raw_text: str = ""


@dataclass
class AudienceSegment:
    """A segment/cluster within the audience."""
    name: str
    size: int
    percentage: float
    keywords: List[str]
    representative_texts: List[str]
    pain_points: List[str]
    desires: List[str]
    values: List[str]
    language_patterns: Dict[str, int]  # word -> frequency


@dataclass
class AudiencePortrait:
    """Complete portrait of an audience."""
    source_url: str
    source_type: str
    total_analyzed: int
    segments: List[AudienceSegment]
    overall_values_map: Dict
    top_pain_points: List[str]
    top_desires: List[str]
    language_patterns: Dict[str, int]
    tone: str
    activity_level: str
    platform_specific: Dict = field(default_factory=dict)


@dataclass
class OfferDecomposition:
    """Decomposed offer into components."""
    description: str
    core_problem: str
    target_pain_points: List[str]
    target_desires: List[str]
    avg_check: Optional[float]
    price_model: str  # CPA, CPS, CPL, subscription, one-time
    objections: List[str]
    required_commitment: str  # low, medium, high
    risk_level: str  # low, medium, high
    kyc_required: bool
    geo_restrictions: List[str]


@dataclass
class AudienceMatch:
    """Where the audience lives and how to reach them."""
    platform: str
    channels: List[Dict]  # {name, url, size, engagement, relevance}
    keywords: List[str]
    hashtags: List[str]
    content_angles: List[str]
    tone_recommendations: List[str]


class Config:
    """Load and hold configuration."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config = {
            'parsers': {
                'telegram': {'max_posts': 100, 'include_comments': True, 'max_comments_per_post': 50},
                'youtube': {'max_videos': 30, 'max_comments_per_video': 100, 'use_yt_dlp': True},
                'vk': {'max_posts': 100, 'max_comments': 50},
            },
            'analysis': {
                'dimensions': {'frustrations': 0.3, 'sins': 0.2, 'norms': 0.2, 'strengths': 0.15, 'context': 0.15},
                'min_cluster_size': 5,
                'max_clusters': 8,
            },
            'ripple_engine': {'max_depth': 3, 'conflict_threshold': 0.7, 'stop_on_conflict': True},
            'output': {'format': 'markdown', 'include_raw_data': False, 'include_clusters': True}
        }
        if config_path and config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config.update(yaml.safe_load(f))
    
    def __getattr__(self, name):
        return self.config.get(name, {})


class TelegramParser:
    """Parse public Telegram channels (no API key needed for public channels)."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.max_posts = config.get('max_posts', 100)
        self.include_comments = config.get('include_comments', True)
        self.max_comments = config.get('max_comments_per_post', 50)
    
    async def parse(self, url: str) -> ParsedContent:
        """Parse a public Telegram channel."""
        # Extract channel username from URL
        match = re.search(r't\.me/([^/?#]+)', url) or re.search(r'telegram\.me/([^/?#]+)', url)
        if not match:
            raise ValueError(f"Invalid Telegram URL: {url}")
        channel = match.group(1)
        
        # For public channels, we can use t.me/s/channel for preview
        # This is a simplified parser - in production you'd use Telegram Bot API or TDLib
        import aiohttp
        
        posts = []
        async with aiohttp.ClientSession() as session:
            # Try to get channel preview page
            preview_url = f"https://t.me/s/{channel}"
            try:
                async with session.get(preview_url, timeout=30) as resp:
                    html = await resp.text()
                    posts = self._extract_posts_from_html(html, channel)
            except Exception as e:
                print(f"Warning: Could not fetch {preview_url}: {e}")
                posts = []
        
        return ParsedContent(
            source_type="telegram",
            source_url=url,
            title=f"@{channel}",
            items=posts,
            metadata={"channel": channel, "posts_count": len(posts)}
        )
    
    def _extract_posts_from_html(self, html: str, channel: str) -> List[Dict]:
        """Extract posts from t.me/s/channel HTML."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        posts = []
        
        # t.me/s/channel uses .tgme_widget_message class
        for msg in soup.find_all('div', class_='tgme_widget_message'):
            try:
                text_elem = msg.find('div', class_='tgme_widget_message_text')
                text = text_elem.get_text(strip=True) if text_elem else ""
                
                # Get date
                date_elem = msg.find('time', class_='tgme_widget_message_date')
                date = date_elem.get('datetime', '') if date_elem else ""
                
                # Get views
                views_elem = msg.find('span', class_='tgme_widget_message_views')
                views = views_elem.get_text(strip=True) if views_elem else "0"
                
                if text and len(text) > 20:  # Filter out very short/empty
                    posts.append({
                        'text': text,
                        'date': date,
                        'views': views,
                        'channel': channel
                    })
            except Exception:
                continue
        
        return posts[:self.max_posts]


class YouTubeParser:
    """Parse YouTube channel and comments."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.max_videos = config.get('max_videos', 30)
        self.max_comments = config.get('max_comments_per_video', 100)
    
    async def parse(self, url: str) -> ParsedContent:
        """Parse YouTube channel."""
        import aiohttp
        import subprocess
        
        # Extract channel handle
        handle_match = re.search(r'youtube\.com/@([^/?#]+)', url) or \
                       re.search(r'youtube\.com/c/([^/?#]+)', url) or \
                       re.search(r'youtube\.com/channel/([^/?#]+)', url)
        
        if not handle_match:
            raise ValueError(f"Invalid YouTube URL: {url}")
        
        handle = handle_match.group(1)
        
        videos = []
        
        # Use yt-dlp for reliable extraction
        try:
            cmd = [
                'yt-dlp', '--flat-playlist', '--dump-json',
                f'https://youtube.com/@{handle}',
                '--playlist-end', str(self.max_videos)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    video = json.loads(line)
                    videos.append({
                        'title': video.get('title', ''),
                        'url': video.get('url', ''),
                        'duration': video.get('duration', 0),
                        'view_count': video.get('view_count', 0)
                    })
        except Exception as e:
            print(f"Warning: yt-dlp failed: {e}")
        
        return ParsedContent(
            source_type="youtube",
            source_url=url,
            title=f"@{handle}",
            items=videos,
            metadata={"handle": handle, "videos_count": len(videos)}
        )


class VKParser:
    """Parse VK public groups."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.max_posts = config.get('max_posts', 100)
    
    async def parse(self, url: str) -> ParsedContent:
        """Parse VK group (public pages only, no auth)."""
        import aiohttp
        
        # Extract group ID/screen_name
        match = re.search(r'vk\.com/([^/?#]+)', url)
        if not match:
            raise ValueError(f"Invalid VK URL: {url}")
        
        group = match.group(1)
        posts = []
        
        # VK public API (no auth needed for public pages)
        api_url = f"https://api.vk.com/method/wall.get"
        params = {
            'domain': group,
            'count': min(self.max_posts, 100),
            'filter': 'owner',
            'v': '5.199'
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(api_url, params=params, timeout=30) as resp:
                    data = await resp.json()
                    if 'response' in data:
                        for item in data['response']['items']:
                            text = item.get('text', '')
                            if text and len(text) > 20:
                                posts.append({
                                    'text': text,
                                    'date': item.get('date', 0),
                                    'likes': item.get('likes', {}).get('count', 0),
                                    'reposts': item.get('reposts', {}).get('count', 0),
                                    'comments': item.get('comments', {}).get('count', 0),
                                    'group': group
                                })
            except Exception as e:
                print(f"Warning: VK API failed: {e}")
        
        return ParsedContent(
            source_type="vk",
            source_url=url,
            title=group,
            items=posts,
            metadata={"group": group, "posts_count": len(posts)}
        )


class GenericParser:
    """Parse generic web pages, forums, etc."""
    
    async def parse(self, url: str) -> ParsedContent:
        """Parse any web page for text content."""
        import aiohttp
        from bs4 import BeautifulSoup
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=30) as resp:
                    html = await resp.text()
            except Exception as e:
                raise ValueError(f"Failed to fetch {url}: {e}")
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script/style
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract text
        text = soup.get_text(separator='\n', strip=True)
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n') if len(p.strip()) > 50]
        
        return ParsedContent(
            source_type="web",
            source_url=url,
            title=soup.title.string if soup.title else url,
            items=[{'text': p} for p in paragraphs[:100]],
            metadata={"paragraphs_count": len(paragraphs)}
        )


class TextAnalyzer:
    """Analyze text for pain points, desires, values, language patterns."""
    
    # Keyword patterns for different dimensions
    FRUSTRATION_PATTERNS = [
        r'(бесит|раздражает|ненавиж|проблем|сложн|не получает|не работает|ошибк|баг|лагает|тормоз)',
        r'(hate|annoy|frustrat|problem|difficult|broken|error|slow|lag)',
        r'(заебал|достал|устал|надоел|показалось|разочарован)',
    ]
    
    DESIRE_PATTERNS = [
        r'(хочу|желаю|мечта|нужен|нужн|потреб|ищу|найти|купить|заказать|подобрать)',
        r'(want|need|dream|wish|looking for|search|buy|order|find)',
        r'(круто бы|идеально|супер было|мечтаю)',
    ]
    
    VALUE_PATTERNS = [
        r'(ценю|важно|принцип|этик|морал|честн|справедлив|качеств|надежн|профессионал)',
        r'(value|important|principle|ethic|honest|fair|quality|reliable|professional)',
        r'(нормально|правильно|как надо|по уму|по совести)',
    ]
    
    STRENGTH_PATTERNS = [
        r'(умею|может|опы|навык|знан|эксперт|профи|специалист|мастер|гuru)',
        r'(can|able|skill|expert|know|experience|master|pro)',
        r'(делаю|сделал|решил|настроил|создал|построил)',
    ]
    
    CONTEXT_PATTERNS = [
        r'(в москве|в спб|в крыму|в казани|россия|russia|moscow|spb|crimea)',
        r'(windows|linux|mac|android|ios|iphone|pc|ноутбук|телефон)',
        r'(python|javascript|php|java|go|rust|sql|docker|k8s|kubernetes)',
    ]
    
    def __init__(self):
        self.frustration_re = [re.compile(p, re.IGNORECASE) for p in self.FRUSTRATION_PATTERNS]
        self.desire_re = [re.compile(p, re.IGNORECASE) for p in self.DESIRE_PATTERNS]
        self.value_re = [re.compile(p, re.IGNORECASE) for p in self.VALUE_PATTERNS]
        self.strength_re = [re.compile(p, re.IGNORECASE) for p in self.STRENGTH_PATTERNS]
        self.context_re = [re.compile(p, re.IGNORECASE) for p in self.CONTEXT_PATTERNS]
    
    def analyze_texts(self, texts: List[str]) -> Dict:
        """Analyze a list of texts and return dimension evidence."""
        evidence = {
            'frustrations': [],
            'desires': [],
            'values': [],
            'strengths': [],
            'context': [],
            'language_patterns': {}
        }
        
        # Word frequency for language patterns
        word_freq = {}
        
        for text in texts:
            # Extract words (cyrillic + latin, 3+ chars)
            words = re.findall(r'[а-яёa-z]{3,}', text.lower())
            for w in words:
                word_freq[w] = word_freq.get(w, 0) + 1
            
            # Check patterns
            for pattern in self.frustration_re:
                if pattern.search(text):
                    evidence['frustrations'].append(text[:200])
                    break
            
            for pattern in self.desire_re:
                if pattern.search(text):
                    evidence['desires'].append(text[:200])
                    break
            
            for pattern in self.value_re:
                if pattern.search(text):
                    evidence['values'].append(text[:200])
                    break
            
            for pattern in self.strength_re:
                if pattern.search(text):
                    evidence['strengths'].append(text[:200])
                    break
            
            for pattern in self.context_re:
                if pattern.search(text):
                    evidence['context'].append(text[:200])
                    break
        
        # Top language patterns
        evidence['language_patterns'] = dict(
            sorted(word_freq.items(), key=lambda x: -x[1])[:50]
        )
        
        return evidence


class Clusterer:
    """Cluster audience into segments based on text similarity."""
    
    def __init__(self, config: Dict):
        self.min_cluster_size = config.get('min_cluster_size', 5)
        self.max_clusters = config.get('max_clusters', 8)
    
    def cluster(self, items: List[Dict], text_key: str = 'text') -> List[AudienceSegment]:
        """Simple keyword-based clustering."""
        if len(items) < self.min_cluster_size:
            return [self._make_single_segment(items, text_key)]
        
        # Extract keywords from each item
        item_keywords = []
        for item in items:
            text = item.get(text_key, '')
            keywords = self._extract_keywords(text)
            item_keywords.append((item, keywords))
        
        # Simple clustering by shared keywords
        clusters = []
        used = set()
        
        for i, (item, keywords) in enumerate(item_keywords):
            if i in used:
                continue
            
            cluster_items = [item]
            cluster_keywords = set(keywords)
            used.add(i)
            
            # Find similar items
            for j, (other_item, other_keywords) in enumerate(item_keywords):
                if j in used:
                    continue
                overlap = len(cluster_keywords & set(other_keywords))
                if overlap >= 2:  # At least 2 shared keywords
                    cluster_items.append(other_item)
                    cluster_keywords.update(other_keywords)
                    used.add(j)
            
            if len(cluster_items) >= self.min_cluster_size:
                clusters.append(self._make_segment(cluster_items, cluster_keywords, text_key))
        
        # Remaining items as "Other"
        remaining = [item for i, (item, _) in enumerate(item_keywords) if i not in used]
        if remaining:
            clusters.append(self._make_single_segment(remaining, text_key, name="Other"))
        
        # Sort by size, limit
        clusters.sort(key=lambda c: -c.size)
        return clusters[:self.max_clusters]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Remove common words
        stopwords = {'это', 'что', 'как', 'для', 'и', 'в', 'на', 'с', 'по', 'от', 'до', 'из', 'о', 'об', 'за', 'под', 'над',
                     'the', 'and', 'for', 'with', 'to', 'in', 'on', 'of', 'a', 'an', 'is', 'are', 'was', 'were',
                     'этот', 'такой', 'так', 'или', 'но', 'да', 'нет', 'не', 'ни', 'же', 'бы', 'был', 'была', 'были'}
        
        words = re.findall(r'[а-яёa-z]{4,}', text.lower())
        keywords = [w for w in words if w not in stopwords]
        # Return top 10 unique
        return list(dict.fromkeys(keywords))[:10]
    
    def _make_segment(self, items: List[Dict], keywords: set, text_key: str, name: str = None) -> AudienceSegment:
        """Create segment from clustered items."""
        all_texts = [item.get(text_key, '') for item in items]
        combined = ' '.join(all_texts)
        
        # Extract pain points, desires from texts
        analyzer = TextAnalyzer()
        evidence = analyzer.analyze_texts(all_texts)
        
        return AudienceSegment(
            name=name or f"Segment_{keywords.pop() if keywords else 'Unknown'}",
            size=len(items),
            percentage=0,  # Will be calculated later
            keywords=list(keywords)[:10],
            representative_texts=all_texts[:3],
            pain_points=evidence['frustrations'][:5],
            desires=evidence['desires'][:5],
            values=evidence['values'][:5],
            language_patterns=evidence['language_patterns']
        )
    
    def _make_single_segment(self, items: List[Dict], text_key: str, name: str = "General") -> AudienceSegment:
        """Create a single segment from all items."""
        all_texts = [item.get(text_key, '') for item in items]
        combined = ' '.join(all_texts)
        keywords = self._extract_keywords(combined)
        
        analyzer = TextAnalyzer()
        evidence = analyzer.analyze_texts(all_texts)
        
        return AudienceSegment(
            name=name,
            size=len(items),
            percentage=100.0,
            keywords=keywords[:15],
            representative_texts=all_texts[:3],
            pain_points=evidence['frustrations'][:5],
            desires=evidence['desires'][:5],
            values=evidence['values'][:5],
            language_patterns=evidence['language_patterns']
        )


class AudienceAnalyzer:
    """Main analyzer orchestrating the pipeline."""
    
    def __init__(self, config: Config):
        self.config = config
        self.human_analyzer = HumanAnalyzer(config.config)
        self.parsers = {
            'telegram': TelegramParser(config.config['parsers']['telegram']),
            'youtube': YouTubeParser(config.config['parsers']['youtube']),
            'vk': VKParser(config.config['parsers']['vk']),
            'web': GenericParser(),
        }
        self.text_analyzer = TextAnalyzer()
        self.clusterer = Clusterer(config.config['analysis'])
    
    async def analyze_audience(self, source: str, url: str) -> AudiencePortrait:
        """Mode 1: Audience → Offer."""
        parser = self.parsers.get(source)
        if not parser:
            raise ValueError(f"Unknown source: {source}")
        
        print(f"🔍 Parsing {source}: {url}")
        content = await parser.parse(url)
        
        print(f"📄 Parsed {len(content.items)} items")
        
        # Extract texts
        texts = [item.get('text', '') for item in content.items if item.get('text')]
        
        if not texts:
            raise ValueError("No text content extracted")
        
        # Analyze overall
        evidence = self.text_analyzer.analyze_texts(texts)
        
        # Cluster
        segments = self.clusterer.cluster(content.items)
        total = sum(s.size for s in segments)
        for s in segments:
            s.percentage = round(s.size / total * 100, 1)
        
        # Build values map using human-source methodology
        # Create mock human profile for the audience
        values_map = self._build_values_map(evidence, segments)
        
        # Generate keys (offer ideas) from values map
        keys = self.human_analyzer._generate_keys(values_map, evidence)
        
        # Run ripple engine on each key
        profile = HumanProfile(
            dimensions=[],
            values_map=values_map,
            keys=keys,
            conflicts_summary={}
        )
        
        for key in keys:
            self.human_analyzer._run_ripple_engine(key, values_map)
        
        # Determine tone
        tone = self._detect_tone(texts)
        activity = self._detect_activity(content)
        
        return AudiencePortrait(
            source_url=url,
            source_type=source,
            total_analyzed=len(texts),
            segments=segments,
            overall_values_map=values_map,
            top_pain_points=evidence['frustrations'][:10],
            top_desires=evidence['desires'][:10],
            language_patterns=evidence['language_patterns'],
            tone=tone,
            activity_level=activity,
            platform_specific=content.metadata
        )
    
    def _build_values_map(self, evidence: Dict, segments: List[AudienceSegment]) -> Dict:
        """Build values map (landscape) from evidence."""
        return {
            'deep_zones': [
                {'name': 'Strength: ' + s.name, 'evidence': s.values[:3], 'depth': 'deep'}
                for s in segments if s.values
            ][:3],
            'shallow_zones': [
                {'name': 'Pain: ' + s.name, 'evidence': s.pain_points[:3], 'depth': 'shallow'}
                for s in segments if s.pain_points
            ][:3],
            'underwater_rocks': [
                {'name': 'Hard Constraint: ' + v, 'evidence': [v], 'type': 'value'}
                for v in set(evidence['values']) if v
            ][:5]
        }
    
    def _detect_tone(self, texts: List[str]) -> str:
        """Detect overall tone of communication."""
        formal = sum(1 for t in texts if re.search(r'\b(вы|ваш|уважаемый|прошу|благодарю)\b', t, re.I))
        casual = sum(1 for t in texts if re.search(r'\b(ты|твой|привет|хех|лол|круто|топ|норм)\b', t, re.I))
        technical = sum(1 for t in texts if re.search(r'\b(api|sql|docker|k8s|python|js|json|http|ssl)\b', t, re.I))
        
        if technical > max(formal, casual):
            return "technical"
        elif casual > formal:
            return "casual"
        else:
            return "neutral/formal"
    
    def _detect_activity(self, content: ParsedContent) -> str:
        """Detect activity level."""
        count = len(content.items)
        if count > 50:
            return "high"
        elif count > 15:
            return "medium"
        else:
            return "low"
    
    def analyze_offer(self, offer_text: str) -> OfferDecomposition:
        """Mode 2: Offer → Audience. Decompose offer into components."""
        # Use human-source to analyze the offer
        evidence = self.text_analyzer.analyze_texts([offer_text])
        
        return OfferDecomposition(
            description=offer_text,
            core_problem=self._extract_core_problem(offer_text),
            target_pain_points=evidence['frustrations'],
            target_desires=evidence['desires'],
            avg_check=self._extract_price(offer_text),
            price_model=self._detect_price_model(offer_text),
            objections=self._extract_objections(offer_text),
            required_commitment=self._detect_commitment(offer_text),
            risk_level=self._detect_risk(offer_text),
            kyc_required=self._detect_kyc(offer_text),
            geo_restrictions=self._detect_geo(offer_text)
        )
    
    def _extract_core_problem(self, text: str) -> str:
        """Extract core problem the offer solves."""
        # Simplified - first sentence or clause with problem words
        sentences = re.split(r'[.!?]', text)
        for s in sentences:
            if any(w in s.lower() for w in ['проблем', 'боли', 'решает', 'помогает', 'устраняет', 'упрощает']):
                return s.strip()
        return sentences[0].strip() if sentences else text[:100]
    
    def _extract_price(self, text: str) -> Optional[float]:
        """Extract price/check from text."""
        # Look for $, руб, р., cpa, cps, etc.
        patterns = [
            r'\$(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*(?:руб|р\.|rub)',
            r'cpa\s*[=:]\s*\$?(\d+(?:\.\d+)?)',
            r'cps\s*[=:]\s*(\d+(?:\.\d+)?)%',
        ]
        for p in patterns:
            m = re.search(p, text, re.I)
            if m:
                return float(m.group(1))
        return None
    
    def _detect_price_model(self, text: str) -> str:
        text_lower = text.lower()
        if 'cpa' in text_lower:
            return 'CPA'
        elif 'cps' in text_lower:
            return 'CPS'
        elif 'cpl' in text_lower:
            return 'CPL'
        elif 'подписк' in text_lower or 'subscription' in text_lower:
            return 'subscription'
        else:
            return 'one-time'
    
    def _extract_objections(self, text: str) -> List[str]:
        """Extract likely objections."""
        objections = []
        objection_patterns = [
            'дорог', 'expensive', 'не довер', 'don\'t trust', 'склад', 'warehouse',
            'долго', 'long', 'сложн', 'complex', 'риск', 'risk', 'обман', 'scam'
        ]
        for pat in objection_patterns:
            if pat in text.lower():
                objections.append(pat)
        return objections[:5]
    
    def _detect_commitment(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ['разов', 'один раз', 'one-time', 'single']):
            return 'low'
        elif any(w in text_lower for w in ['подписк', 'subscription', 'ежемесяч', 'monthly', 'регулярн']):
            return 'high'
        else:
            return 'medium'
    
    def _detect_risk(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ['беттинг', 'gambling', 'casino', 'crypto', 'инвестиц', 'investment', 'риск']):
            return 'high'
        elif any(w in text_lower for w in ['обучен', 'course', 'education', 'софт', 'software', 'сервис', 'service']):
            return 'medium'
        else:
            return 'low'
    
    def _detect_kyc(self, text: str) -> bool:
        text_lower = text.lower()
        return any(w in text_lower for w in ['kyc', 'паспорт', 'passport', 'документ', 'document', 'верификац', 'verif'])
    
    def _detect_geo(self, text: str) -> List[str]:
        geo = []
        geo_patterns = ['россия', 'russia', 'край', 'край', 'москва', 'moscow', 'спб', 'спб', 'индия', 'india', 'индия', 'край']
        for g in ['россия', 'russia', 'индия', 'india', 'снг', 'cis', 'европа', 'europe', 'сша', 'usa', 'край', 'край']:
            if g in text.lower():
                geo.append(g.title())
        return geo[:5]
    
    def find_audience_for_offer(self, offer: OfferDecomposition) -> List[AudienceMatch]:
        """Find where the target audience lives based on offer decomposition."""
        # This would search for relevant channels/groups
        # For now, return template recommendations based on offer type
        matches = []
        
        # Build search keywords from offer
        keywords = offer.target_pain_points + offer.target_desires
        
        matches.append(AudienceMatch(
            platform="telegram",
            channels=[
                {"name": f"Channels about {kw}", "url": f"https://t.me/search?q={kw}", "size": "?", "engagement": "?", "relevance": "high"}
                for kw in keywords[:5]
            ],
            keywords=keywords[:10],
            hashtags=[f"#{kw.replace(' ', '_')}" for kw in keywords[:5]],
            content_angles=self._generate_content_angles(offer),
            tone_recommendations=self._recommend_tone(offer)
        ))
        
        matches.append(AudienceMatch(
            platform="youtube",
            channels=[
                {"name": f"Creators in {kw}", "url": f"https://youtube.com/results?search_query={kw}", "size": "?", "engagement": "?", "relevance": "high"}
                for kw in keywords[:5]
            ],
            keywords=keywords[:10],
            hashtags=[],
            content_angles=self._generate_content_angles(offer),
            tone_recommendations=self._recommend_tone(offer)
        ))
        
        return matches
    
    def _generate_content_angles(self, offer: OfferDecomposition) -> List[str]:
        """Generate content angles for creatives."""
        angles = []
        if offer.target_pain_points:
            angles.append(f"Problem-Solution: {offer.target_pain_points[0]} → {offer.description[:50]}")
        if offer.target_desires:
            angles.append(f"Desire Fulfillment: {offer.target_desires[0]}")
        angles.append(f"Case Study: How [persona] achieved [result] with {offer.description[:30]}")
        angles.append(f"Comparison: Why {offer.description[:30]} beats alternatives")
        angles.append(f"Objection Handling: '{offer.objections[0] if offer.objections else 'Too expensive'}' — here's why it's worth it")
        return angles
    
    def _recommend_tone(self, offer: OfferDecomposition) -> List[str]:
        """Recommend tone based on offer risk/commitment."""
        if offer.risk_level == 'high':
            return ["Educational/Expert — build trust first", "Transparent about risks", "Social proof heavy"]
        elif offer.required_commitment == 'high':
            return ["Value-first — show ROI before asking", "Demo/Trial focused", "Case studies"]
        else:
            return ["Direct benefit-driven", "Urgency/Scarcity", "Simple & clear"]


class ReportGenerator:
    """Generate markdown reports."""
    
    @staticmethod
    def generate_audience_report(portrait: AudiencePortrait, keys: List[Key]) -> str:
        """Generate Mode 1 report."""
        lines = [
            f"# Audience Analysis Report",
            f"**Source:** {portrait.source_type} — {portrait.source_url}",
            f"**Analyzed:** {portrait.total_analyzed} items | **Tone:** {portrait.tone} | **Activity:** {portrait.activity_level}",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "## Executive Summary",
            f"Audience of {portrait.total_analyzed} items across {len(portrait.segments)} segments. ",
            f"Primary language: {portrait.tone}. Top pain: {portrait.top_pain_points[0] if portrait.top_pain_points else 'N/A'}. ",
            f"Top desire: {portrait.top_desires[0] if portrait.top_desires else 'N/A'}.",
            "",
            "## Values Map (Landscape)",
            ""
        ]
        
        for zone_type, zones in portrait.overall_values_map.items():
            lines.append(f"### {zone_type.replace('_', ' ').title()}")
            for z in zones:
                lines.append(f"- **{z['name']}** ({z.get('depth', z.get('type', ''))})")
                for e in z.get('evidence', [])[:2]:
                    lines.append(f"  - {e[:100]}...")
            lines.append("")
        
        lines.extend([
            "## Segments",
            ""
        ])
        
        for seg in portrait.segments:
            lines.extend([
                f"### {seg.name} ({seg.size} items, {seg.percentage}%)",
                f"**Keywords:** {', '.join(seg.keywords[:10])}",
                f"**Pain Points:** {'; '.join(seg.pain_points[:3]) if seg.pain_points else '—'}",
                f"**Desires:** {'; '.join(seg.desires[:3]) if seg.desires else '—'}",
                f"**Values:** {'; '.join(seg.values[:3]) if seg.values else '—'}",
                f"**Sample:** {seg.representative_texts[0][:150]}..." if seg.representative_texts else "",
                ""
            ])
        
        lines.extend([
            "## Language Patterns (Top 30)",
            ""
        ])
        for word, count in list(portrait.language_patterns.items())[:30]:
            lines.append(f"- **{word}**: {count}")
        
        lines.extend([
            "",
            "## Validated Offer Ideas (Ripple Engine)",
            ""
        ])
        
        for i, key in enumerate(keys, 1):
            status = "✅ VALIDATED" if key.status == 'validated' else "❌ REJECTED"
            lines.extend([
                f"### {i}. {key.text} [{status}]",
                f"**Rationale:** {key.rationale}",
                f"**Circles:** {len(key.circles)} | **Conflicts:** {len(key.conflicts)}",
                ""
            ])
            
            for circle in key.circles:
                lines.append(f"  **Circle {circle.depth}: {circle.name}**")
                for aspect in circle.aspects:
                    lines.append(f"  - {aspect}")
                if circle.conflicts:
                    lines.append(f"  ⚠️ **Conflicts:**")
                    for c in circle.conflicts:
                        sev = "🔴" if c.severity == 'critical' else "🟡"
                        lines.append(f"  {sev} {c.violated_value}: {c.aspect} — {c.description}")
            
            if key.replacement:
                lines.append(f"  🔄 **Replacement:** {key.replacement}")
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_offer_report(offer: OfferDecomposition, matches: List[AudienceMatch], validation: List[Key]) -> str:
        """Generate Mode 2 report."""
        lines = [
            f"# Offer → Audience Analysis",
            f"**Offer:** {offer.description[:100]}...",
            f"**Price Model:** {offer.price_model} | **Avg Check:** ${offer.avg_check or 'N/A'} | **Risk:** {offer.risk_level} | **KYC:** {'Yes' if offer.kyc_required else 'No'}",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "## Offer Decomposition",
            f"**Core Problem:** {offer.core_problem}",
            f"**Target Pain Points:** {', '.join(offer.target_pain_points) if offer.target_pain_points else '—'}",
            f"**Target Desires:** {', '.join(offer.target_desires) if offer.target_desires else '—'}",
            f"**Objections:** {', '.join(offer.objections) if offer.objections else '—'}",
            f"**Commitment Required:** {offer.required_commitment}",
            "",
            "## Target Audience Portrait",
            f"People experiencing: {', '.join(offer.target_pain_points[:3])}",
            f"Wanting: {', '.join(offer.target_desires[:3])}",
            f"Price sensitivity: {'High' if offer.avg_check and offer.avg_check > 100 else 'Medium' if offer.avg_check and offer.avg_check > 20 else 'Low'}",
            f"Risk tolerance: {offer.risk_level.title()}",
            f"KYC tolerance: {'Required' if offer.kyc_required else 'Not required'}",
            f"Geo: {', '.join(offer.geo_restrictions) if offer.geo_restrictions else 'Global'}",
            "",
            "## Where They Live",
            ""
        ]
        
        for match in matches:
            lines.extend([
                f"### {match.platform.title()}",
                f"**Keywords:** {', '.join(match.keywords[:10])}",
                f"**Hashtags:** {', '.join(match.hashtags[:10])}" if match.hashtags else "",
                "**Channels to research:**"
            ])
            for ch in match.channels[:5]:
                lines.append(f"- {ch['name']}: {ch['url']} (relevance: {ch['relevance']})")
            lines.append("")
        
        lines.extend([
            "## Content Angles for Creatives",
            ""
        ])
        for angle in matches[0].content_angles if matches else []:
            lines.append(f"- {angle}")
        
        lines.extend([
            "",
            "## Tone Recommendations",
            ""
        ])
        for tone in matches[0].tone_recommendations if matches else []:
            lines.append(f"- {tone}")
        
        lines.extend([
            "",
            "## Ripple Validation (Offer vs Audience Values)",
            ""
        ])
        
        for key in validation:
            status = "✅ VALIDATED" if key.status == 'validated' else "❌ CONFLICT"
            lines.append(f"### {key.text} [{status}]")
            if key.conflicts:
                for c in key.conflicts:
                    sev = "🔴" if c.severity == 'critical' else "🟡"
                    lines.append(f"{sev} {c.violated_value}: {c.description}")
            if key.replacement:
                lines.append(f"🔄 **Suggested Pivot:** {key.replacement}")
            lines.append("")
        
        return "\n".join(lines)


async def main():
    parser = argparse.ArgumentParser(description="Audience Analyzer — Audience→Offer or Offer→Audience")
    parser.add_argument("--mode", choices=['audience2offer', 'offer2audience'], required=True,
                        help="Analysis mode")
    parser.add_argument("--source", choices=['telegram', 'youtube', 'vk', 'web'],
                        help="Source type (for audience2offer)")
    parser.add_argument("--url", help="Source URL (for audience2offer)")
    parser.add_argument("--offer", help="Offer description (for offer2audience)")
    parser.add_argument("--offer-file", help="YAML file with offer details")
    parser.add_argument("--config", default="skills/audience-analyzer/config.yaml", help="Config file")
    parser.add_argument("--output", help="Output report file")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Load config
    config = Config(Path(args.config) if args.config else None)
    
    analyzer = AudienceAnalyzer(config)
    
    if args.mode == 'audience2offer':
        if not args.source or not args.url:
            parser.error("audience2offer requires --source and --url")
        
        portrait = await analyzer.analyze_audience(args.source, args.url)
        
        # Generate keys from profile
        keys = analyzer.human_analyzer._generate_keys(portrait.overall_values_map, {})
        profile = HumanProfile(
            dimensions=[],
            values_map=portrait.overall_values_map,
            keys=keys,
            conflicts_summary={}
        )
        for key in keys:
            analyzer.human_analyzer._run_ripple_engine(key, portrait.overall_values_map)
        
        report = ReportGenerator.generate_audience_report(portrait, keys)
        
    else:  # offer2audience
        if args.offer_file:
            with open(args.offer_file, 'r', encoding='utf-8') as f:
                offer_data = yaml.safe_load(f)
            offer_text = offer_data.get('description', '')
        elif args.offer:
            offer_text = args.offer
        else:
            parser.error("offer2audience requires --offer or --offer-file")
        
        offer = analyzer.analyze_offer(offer_text)
        matches = analyzer.find_audience_for_offer(offer)
        
        # Validate offer against typical audience values
        # Create a generic audience values map for validation
        generic_values = {
            'deep_zones': [{'name': 'Cost Savings', 'evidence': ['save money'], 'depth': 'deep'}],
            'shallow_zones': [{'name': 'Complexity Fear', 'evidence': ['too complex'], 'depth': 'shallow'}],
            'underwater_rocks': [
                {'name': 'No Scams', 'evidence': ['trust'], 'type': 'value'},
                {'name': 'Privacy', 'evidence': ['no kyc', 'anonymous'], 'type': 'hard_constraint'}
            ]
        }
        
        test_key = Key(
            text=offer_text[:80],
            source_dimension="offer_test",
            rationale="Offer validation against generic audience"
        )
        analyzer.human_analyzer._run_ripple_engine(test_key, generic_values)
        
        report = ReportGenerator.generate_offer_report(offer, matches, [test_key])
    
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(report, encoding='utf-8')
        print(f"💾 Report saved to {args.output}")
    
    if args.verbose or not args.output:
        print("\n" + "="*70)
        print(report)


if __name__ == "__main__":
    asyncio.run(main())