import json
with open('cache/self_model.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Keep only last 5 studied
data['sovest']['studied'] = data['sovest']['studied'][-5:]
print('Kept studied:', data['sovest']['studied'])

with open('cache/self_model.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print('Done')