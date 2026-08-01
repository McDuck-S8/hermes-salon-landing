import json
with open('cache/self_model.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print('last_cycle:', data.get('last_cycle'))
print('cycle_count:', data.get('cycle_count'))
print('studied len:', len(data.get('sovest', {}).get('studied', [])))
print('studied:', data.get('sovest', {}).get('studied', []))
print('znu keys:', list(data.get('znu', {}).keys()))
print('assessments len:', len(data.get('sovest', {}).get('assessments', [])))