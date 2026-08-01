import json
import sys
sys.path.insert(0, 'D:/Portable_Soft/hermes/skills/automation/knowledge-filter/scripts')
from filter import KnowledgeFilter

filter = KnowledgeFilter()

# Load YouTube cache
with open('D:/Portable_Soft/hermes/cache/youtube_watch/latest.json') as f:
    data = json.load(f)

articles = []
for ch_id, ch_data in data.get('channels', {}).items():
    for v in ch_data.get('videos', []):
        articles.append({
            "title": v.get("title", ""),
            "url": v.get("url", ""),
            "source": f"youtube_{ch_id}",
            "content": f"Title: {v.get('title', '')}\nDuration: {v.get('duration', '')}\nChannel: {ch_id}",
            "extra": {"channel": ch_id, "topic": ch_data.get("topic", "")}
        })

print(f"Filtering {len(articles)} YouTube videos...")
results = filter.filter_batch(articles)

passed = sum(1 for r in results if r.passed)
print(f"\n=== SUMMARY ===")
print(f"Total: {len(results)} | Passed: {passed} | Rejected: {len(results)-passed}")