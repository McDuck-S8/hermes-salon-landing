import feedparser
import json
from datetime import datetime

# CPA feeds
feeds = [
    'https://www.cparadar.com/feed/',
    'https://offervault.com/feed/',
    'https://www.affpaying.com/feed/',
    'https://offerslook.com/rss.xml',
    'https://www.mobidea.com/feed/',
    'https://www.mobidea.com/rss.xml',
    'https://www.yeahmobi.com/rss.xml',
    'https://www.zeropark.com/feed/',
]

# AI feeds
ai_feeds = [
    'https://www.artificialintelligence-news.com/feed/',
    'https://venturebeat.com/category/ai/feed/',
    'https://www.technologyreview.com/feed/',
    'https://www.theverge.com/ai-artificial-intelligence/rss/index.xml',
    'https://openai.com/blog/rss.xml',
    'https://blog.google/technology/ai/rss/',
    'https://deepmind.google/blog/rss/',
    'https://huggingface.co/blog/rss.xml',
    'https://huggingface.co/papers/rss.xml',
]

all_feeds = feeds + ai_feeds

all_entries = []
for url in all_feeds:
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            all_entries.append({
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'published': entry.get('published', ''),
                'summary': entry.get('summary', '')[:300],
                'source': feed.feed.get('title', url),
            })
    except Exception as e:
        print(f'Error fetching {url}: {e}')

# Save to file
output = {
    'timestamp': datetime.now().isoformat(),
    'entries': all_entries,
    'count': len(all_entries)
}

with open('rss_digest_latest.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f'Fetched {len(all_entries)} entries from {len(all_feeds)} feeds')
print('Saved to rss_digest_latest.json')