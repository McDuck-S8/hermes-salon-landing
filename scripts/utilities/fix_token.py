import pathlib

a = "8645168670"
b = "AAG_wrpmbyKcqE5PCe192k5WWWV-swl6dug"
token = a + ":" + b

p = pathlib.Path(".env")
lines = p.read_text().splitlines()

found = False
for i, line in enumerate(lines):
    if line.startswith("TELEGRAM_BOT_TOKEN="***        found = True
        break

if not found:
    for i, line in enumerate(lines):
        if line.startswith("TELEGRAM_API_HASH="***            lines.insert(i + 1, "TELEGRAM_BOT_TOKEN="***            break

p.write_text("\n".join(lines) + "\n")
print("OK:", token[:15] + "...")
