import subprocess, json, pathlib, os

env = pathlib.Path("D:/Portable_Soft/hermes/.env")
apikey = None
for line in env.read_text().splitlines():
    if "BOT" in line and "TOKEN" in line and "=" in line:
        apikey = line.split("=", 1)[1].strip()
        break

img_dir = pathlib.Path("D:/Portable_Soft/hermes-usb-portable-main/data/post_images")

# Use absolute path with forward slashes
img = str(img_dir / "frontier.jpg").replace("\\", "/")
print(f"Image path: {img}")
print(f"Exists: {pathlib.Path(img).exists()}")

# Try sending with URL method instead of file upload
# First upload, then send by file_id
# Actually, let's try with the URL directly
unsplash_url = "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1200&q=80"

r = subprocess.run(
    ["curl", "-s", "-X", "POST",
     f --proxy http://127.0.0.1:10809 "https://api.telegram.org/bot{apikey}/sendPhoto",
     "-d", f"chat_id=@ai_frontier_you",
     "-d", f"photo={unsplash_url}",
     "-d", "caption=рџ§  РўРµСЃС‚ СЃ РєР°СЂС‚РёРЅРєРѕР№"],
    capture_output=True, text=True, timeout=30
)
print(f"URL method: {r.stdout[:300]}")

