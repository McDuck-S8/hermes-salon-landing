import subprocess, json, pathlib

env = pathlib.Path("D:/Portable_Soft/hermes/.env")
token = None
for line in env.read_text().splitlines():
    if line.startswith("TELEGRAM_BOT_TOKEN="):
        token = line.split("=", 1)[1].strip()
        break

if not token:
    print("NO TOKEN FOUND")
    exit(1)

print(f"Token length: {len(token)}")

channels = [
    "max_brain_chef_official",
    "ai_frontier_you",
    "max_brain_chef_ai",
    "neuro_kitchen_ai",
]

for ch in channels:
    r = subprocess.run(
        ["curl", "-s", "-X", "POST",
         f --proxy http://127.0.0.1:10809 "https://api.telegram.org/bot{token}/sendMessage",
         "-H", "Content-Type: application/json",
         "-d", json.dumps({"chat_id": f"@{ch}", "text": "\u2705 Hermes \u043f\u043e\u0434\u043a\u043b\u044e\u0447\u0451\u043d \u043a \u043a\u0430\u043d\u0430\u043b\u0443"})],
        capture_output=True, text=True
    )
    try:
        data = json.loads(r.stdout)
        if data.get("ok"):
            print(f"  OK @ {ch}")
        else:
            print(f"  FAIL @ {ch}: {data.get('description', 'unknown')}")
    except:
        print(f"  ERROR @ {ch}: {r.stdout[:200]}")

