import json

with open('/d/Portable_Soft/hermes/cache/self_model.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data['sovest']['studied'] = ['coding', 'research', 'debugging', 'creative', 'latent-domain-detector']

with open('/d/Portable_Soft/hermes/cache/self_model.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("self_model.json updated - studied cleared to last 5")