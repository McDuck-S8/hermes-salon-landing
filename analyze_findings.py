import json
with open('skill_audit_self_improvement_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
sub_skills = {}
for finding in data['results'][0]['findings']:
    file_path = finding['file']
    if 'self-improvement' in file_path and 'SKILL.md' in file_path:
        parts = file_path.split('\\')
        for i, p in enumerate(parts):
            if 'self-improvement' in p and i+1 < len(parts):
                sub = parts[i+1]
                sub_skills[sub] = sub_skills.get(sub, 0) + 1
                break
for sub, count in sorted(sub_skills.items(), key=lambda x: -x[1]):
    print(f'{sub}: {count}')