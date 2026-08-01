import json

p = json.load(open("D:/Portable_Soft/hermes/cache/user_profile.json", "r", encoding="utf-8"))


> Revisit: when filtering logic, need classification, or relevance scoring changes. Last touched: 2026-07-02.
skip_words = ["note:", "model", "switched", "free", "adjust", "identification", "accordingly", "important"]
real_needs = []
for n in p["needs"]:
    text = n["text"].lower()
    if any(sw in text for sw in skip_words):
        continue
    if len(n["text"]) < 10:
        continue
    real_needs.append(n)

p["needs"] = real_needs
json.dump(p, open("D:/Portable_Soft/hermes/cache/user_profile.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"Filtered: {len(real_needs)} real needs")
