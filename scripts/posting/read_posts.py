import subprocess, json, pathlib

env = pathlib.Path("D:/Portable_Soft/hermes/.env")
apikey = None
for line in env.read_text().splitlines():
    if "BOT" in line and "TOKEN" in line and "=" in line:
        apikey = line.split("=", 1)[1].strip()
        break

r = subprocess.run(
    ["curl", "-s", "--proxy", "http://127.0.0.1:10809",
     f"https://api.telegram.org/bot{apikey}/getUpdates?limit=50"],
    capture_output=True, text=True, timeout=15
)
data = json.loads(r.stdout)
posts = [u["channel_post"] for u in data.get("result", []) if "channel_post" in u]
print(f"Posts: {len(posts)}")
for p in posts[-10:]:
    chat_name = p.get("chat",{}).get("username","?")
    text = p.get("text", p.get("caption", "(media)"))[:300]
    print(f"\n--- @{chat_name} ---")
    print(text)

