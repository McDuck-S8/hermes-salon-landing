"""outreach.py — Generate Instagram DM outreach messages for potential clients

Usage:
  python scripts/outreach.py --name "Salon Name" --instagram @salon_ig [--site current-site.com]

Output: personalized DM message ready to send
"""

import argparse, json, sys, re

TEMPLATES = {
    "no_site": """Привіт! 👋

Я переглядав ваш Instagram — у вас класні роботи! Помітив, що у вас немає сайту, а це втрачає клієнтів. Багато хто шукає салони через Google, а не Instagram.

Я зробив демо-версію сайту для вашого салону — подивіться:

{preview_url}

Там уже є прайс, галерея, форма запису онлайн. Якщо сподобається — домовимося про співпрацю.

Не хотів нав'язуватись, просто показав, як це може виглядати 😊""",

    "bad_site": """Привіт! 👋

Я переглядав ваш Instagram — класний контент! Але зайшов на ваш сайт і помітив, що він застарів і незручний на телефоні. Це відлякує клієнтів.

Я зробив демо того, як це могло б виглядати сучасно:

{preview_url}

Адаптивний дизайн, швидке завантаження, зручна навігація. Якщо цікаво — розкажу деталі :)""",
}

def slugify(name):
    tr = {
        'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e',
        'ж':'zh','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m',
        'н':'n','о':'o','п':'p','р':'r','с':'s','т':'t','у':'u',
        'ф':'f','х':'kh','ц':'ts','ч':'ch','ш':'sh','щ':'shch',
        'ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya',
        'і':'i','ї':'yi','є':'ye','ґ':'g',
    }
    s = name.lower()
    for cyr, lat in tr.items():
        s = s.replace(cyr, lat)
    s = re.sub(r"[^a-z0-9-]", "", s.replace(" ", "-"))
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:30]

def generate(name, instagram, site=None):
    slug = slugify(name)
    preview_url = f"https://mcduck-s8.github.io/hermes-salon-landing/demos/{slug}/"

    template = TEMPLATES["bad_site"] if site else TEMPLATES["no_site"]
    msg = template.format(name=name, preview_url=preview_url)

    return {
        "to": instagram,
        "message": msg,
        "preview_url": preview_url,
        "call_to_action": "Send this as Instagram DM",
    }

def main():
    p = argparse.ArgumentParser(description="Generate outreach DM")
    p.add_argument("--name", required=True)
    p.add_argument("--instagram", required=True)
    p.add_argument("--site", default=None)
    args = p.parse_args()

    result = generate(args.name, args.instagram, args.site)

    if sys.stdout.isatty():
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("\n" + "=" * 50)
        print("DM TEXT:")
        print("=" * 50)
        print(result["message"])
    else:
        print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
