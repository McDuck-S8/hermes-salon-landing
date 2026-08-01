import subprocess, json, pathlib

env = pathlib.Path(".env")
token = None
prefix = "TELEGRAM_BOT_TOKEN="
for line in env.read_text().splitlines():
    if line.startswith(prefix):
        token = line[len(prefix):]
        break

for ch in ["max_brain_chef_ai", "neuro_kitchen_ai"]:
    body = json.dumps({"chat_id": "@" + ch, "text": "test"})
    r = subprocess.run(
        ["curl", "-s", "-X", "POST",
         f --proxy http://127.0.0.1:10809 "https://api.telegram.org/bot{token}/sendMessage",
         "-H", "Content-Type: application/json",
         "-d", body],
        capture_output=True, text=True, timeout=15
    )
    try:
        data = json.loads(r.stdout)
        print(f"@{ch}: ok={data.get('ok')} desc={data.get('description','')}")
    except:
        print(f"@{ch}: raw={r.stdout[:200]}")
