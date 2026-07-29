"""pipeline.py — Full client acquisition pipeline for Hermes Studio

Usage:
  python scripts/pipeline.py --name "Salon Name" --instagram @salon_ig
  python scripts/pipeline.py --find (find new leads from scout)
  
Pipeline:
  1. Find lead (manual or from scout)
  2. Generate demo page 
  3. Generate outreach DM
  4. Print ready-to-send message
"""

import argparse, json, sys, os, subprocess

def run_demo(name, category, instagram, tagline=""):
    """Generate demo page"""
    cmd = [
        sys.executable, "scripts/demo_generator.py",
        name, "--category", category, "--instagram", instagram
    ]
    if tagline:
        cmd += ["--tagline", tagline]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="D:/Portable_Soft/hermes")
    if result.returncode != 0:
        return {"error": result.stderr}
    return json.loads(result.stdout)

def run_outreach(name, instagram, site=None):
    """Generate outreach DM"""
    cmd = [
        sys.executable, "scripts/outreach.py",
        "--name", name, "--instagram", instagram
    ]
    if site:
        cmd += ["--site", site]
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd="D:/Portable_Soft/hermes")
    if result.returncode != 0:
        return {"error": result.stderr}
    return json.loads(result.stdout)

def pipeline(name, category="salon", instagram="", site=None, tagline=""):
    """Full pipeline: demo + outreach"""
    print(f"\n{'='*60}")
    print(f"🚀 PIPELINE: {name}")
    print(f"{'='*60}")
    
    # Step 1: Generate demo
    print(f"\n[1/3] Генерація демо-сайту...")
    demo = run_demo(name, category, instagram, tagline)
    if "error" in demo:
        print(f"❌ Помилка демо: {demo['error']}")
        return
    print(f"✅ Демо створено: {demo['url']}")
    
    # Step 2: Generate outreach
    print(f"\n[2/3] Генерація повідомлення...")
    outreach = run_outreach(name, instagram, site)
    if "error" in outreach:
        print(f"❌ Помилка аутрич: {outreach['error']}")
        return
    print(f"✅ Повідомлення готове")
    
    # Step 3: Print results
    print(f"\n[3/3] РЕЗУЛЬТАТ:")
    print(f"{'='*60}")
    print(f"📎 Демо: {demo['url']}")
    print(f"📱 Instagram: {instagram}")
    print(f"\n📝 ТЕКСТ ПОВІДОМЛЕННЯ:")
    print(f"{'='*60}")
    print(outreach["message"])
    print(f"{'='*60}")
    print(f"\n👉 Відкрий Instagram, знайди {instagram} і надішли це повідомлення!")
    
    return {"demo": demo, "outreach": outreach}

def main():
    parser = argparse.ArgumentParser(description="Full client acquisition pipeline")
    parser.add_argument("--name", help="Business name")
    parser.add_argument("--category", default="salon", help="Business category")
    parser.add_argument("--instagram", help="Instagram handle")
    parser.add_argument("--site", default=None, help="Current site URL")
    parser.add_argument("--tagline", default="", help="Hero tagline")
    parser.add_argument("--find", action="store_true", help="Find new leads from scout")
    
    args = parser.parse_args()
    
    if args.find:
        print("🔍 Запуск пошуку клієнтів...")
        result = subprocess.run(
            [sys.executable, "scripts/client_scout.py"],
            capture_output=True, text=True,
            cwd="D:/Portable_Soft/hermes"
        )
        print(result.stdout)
        return
    
    if not args.name or not args.instagram:
        parser.print_help()
        return
    
    pipeline(args.name, args.category, args.instagram, args.site, args.tagline)

if __name__ == "__main__":
    main()
