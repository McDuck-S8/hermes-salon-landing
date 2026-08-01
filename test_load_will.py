import sqlite3
import re
KC = 'cache/knowledge_cube.db'
kc = sqlite3.connect(KC)
k = kc.cursor()
k.execute("SELECT raw_text FROM experiences WHERE source='crystal_will' ORDER BY id DESC LIMIT 50")
history = {}
for (text,) in k.fetchall():
    for m in re.finditer(r'\[will:([^\]]+)\]', text):
        action_id = m.group(1).strip()
        if action_id not in history:
            ent_m = re.search(r'извлечено (\d+)', text)
            entities = int(ent_m.group(1)) if ent_m else 0
            history[action_id] = {'result': text, 'entities': entities}
kc.close()
print('History keys:', list(history.keys()))
print('History count:', len(history))
for k, v in list(history.items())[-5:]:
    print(f'  {k}: {v}')