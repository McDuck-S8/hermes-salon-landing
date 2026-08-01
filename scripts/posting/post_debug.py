import subprocess, json, pathlib

env = pathlib.Path("D:/Portable_Soft/hermes/.env")
apikey = None
for line in env.read_text().splitlines():
    if "BOT" in line and "TOKEN" in line and "=" in line:
        apikey = line.split("=", 1)[1].strip()
        break

img_dir = pathlib.Path("D:/Portable_Soft/hermes-usb-portable-main/data/post_images")

# Debug: try one post with verbose curl
chat = "@ai_frontier_you"
img = str(img_dir / "frontier.jpg")
caption = "рџ§  РўРµСЃС‚ СЃ РєР°СЂС‚РёРЅРєРѕР№"

r = subprocess.run(
    ["curl", "-v", "-X", "POST",
     f --proxy http://127.0.0.1:10809 "https://api.telegram.org/bot{apikey}/sendPhoto",
     "-F", f"chat_id={chat}",
     "-F", f"photo=@{img}",
     "-F", f"caption={caption}"],
    capture_output=True, text=True, timeout=30
)
print("STDOUT:", r.stdout[:500])
print("STDERR:", r.stderr[-500:])
print("EXIT:", r.returncode)

