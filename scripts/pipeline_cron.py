"""pipeline_cron.py — Weekly automated pipeline for hot leads
Called by cron job "hot-leads-pipeline" every Monday at 9:00.
Generates demos for top 2 leads and prints report.
"""

import json, subprocess, sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
LEADS_FILE = SCRIPTS.parent / "kyiv_potential_clients.json"
HERMES_ROOT = str(SCRIPTS.parent)

def run_script(script, *args):
    cmd = [sys.executable, str(SCRIPTS / script)] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=HERMES_ROOT)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def main():
    print("=" * 60)
    print("HERMES STUDIO — Weekly Hot Leads Pipeline")
    print("=" * 60)

    # Load leads
    with open(LEADS_FILE, encoding="utf-8") as f:
        leads = json.load(f)

    # Sort by urgency
    def urgency(l):
        score = 0
        if not l.get("current_site"): score += 3
        elif "сломан" in (l.get("issues") or "").lower(): score += 4
        elif "только" in (l.get("current_site") or ""): score += 2
        return -score

    leads.sort(key=urgency)
    hot = leads[:2]  # Top 2 hottest

    print(f"\nTotal leads: {len(leads)}")
    print(f"Processing top {len(hot)}: {', '.join(l['name'] for l in hot)}\n")

    results = []
    for l in hot:
        print(f"\n--- {l['name']} ---")

        cat = l.get("category", "salon")
        # Normalize category names
        if cat in ("medical_center",):
            cat = "medical"
        elif cat in ("beauty_salon",):
            cat = "salon"
        elif cat in ("cafe",):
            cat = "cafe"
        elif cat in ("auto_service",):
            cat = "salon"

        ig = l.get("instagram") or ""
        site = l.get("current_site") or ""
        tagline = ""
        if l["category"] == "medical_center":
            tagline = "Турбота про ваше здоров'я"
        elif l["category"] == "cafe":
            tagline = "Смачно, затишно, по-домашньому"
        else:
            tagline = "Ваш ідеальний образ починається тут"

        out, err, code = run_script(
            "pipeline.py",
            "--name", l["name"],
            "--category", cat,
            "--instagram", ig,
            "--tagline", tagline,
            "--site", site,
        )

        if code == 0:
            # Extract demo URL from output
            for line in out.split("\n"):
                if "Демо створено:" in line or "📎" in line:
                    url = line.split("https://")[-1].strip() if "https://" in line else ""
                    results.append({"name": l["name"], "status": "ok", "url": f"https://{url}" if url else ""})
                    break
        else:
            results.append({"name": l["name"], "status": "error", "error": err[:200]})

    print("\n" + "=" * 60)
    print("RESULTS:")
    for r in results:
        status = "✅" if r["status"] == "ok" else "❌"
        print(f"  {status} {r['name']}: {r.get('url', r.get('error', 'unknown'))}")
    print("=" * 60)

if __name__ == "__main__":
    main()
