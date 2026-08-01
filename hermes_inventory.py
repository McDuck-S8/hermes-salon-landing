import os
import sys
import json
import pkg_resources
import ast
import datetime
import webbrowser
from pathlib import Path

HERMES_HOME = Path(r"D:\Portable_Soft\hermes")
VENV_PYTHON = HERMES_HOME / "hermes-agent" / "venv" / "Scripts" / "python.exe"

HTML_REPORT = HERMES_HOME / "hermes_inventory.html"

def get_pip_list():
    """Получить список установленных пакетов из venv."""
    try:
        import subprocess
        result = subprocess.run(
            [str(VENV_PYTHON), "-m", "pip", "list", "--format=json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return [{"name": "ERROR", "version": result.stderr}]
    except Exception as e:
        return [{"name": "ERROR", "version": str(e)}]

def extract_docstring(filepath):
    """Извлечь docstring из .py файла."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        tree = ast.parse(content)
        return ast.get_docstring(tree) or "Нет описания"
    except:
        return "Не удалось извлечь docstring"

def list_scripts():
    """Список всех .py и .bat файлов в scripts/."""
    scripts_dir = HERMES_HOME / "scripts"
    if not scripts_dir.exists():
        return []
    items = []
    for f in sorted(scripts_dir.rglob("*")):
        if f.is_file() and f.suffix in (".py", ".bat", ".sh", ".ps1"):
            doc = ""
            if f.suffix == ".py":
                doc = extract_docstring(f)
            items.append({
                "name": str(f.relative_to(scripts_dir)),
                "path": str(f),
                "description": doc
            })
    return items

def list_skills():
    """Найти все скиллы (SKILL.md) в папке skills/."""
    skills_dir = HERMES_HOME / "skills"
    if not skills_dir.exists():
        skills_dir = HERMES_HOME / "tools"
    if not skills_dir.exists():
        return []
    skills = []
    for md_file in skills_dir.rglob("SKILL.md"):
        skill_name = md_file.parent.name if md_file.parent.name != "skills" else md_file.stem
        with open(md_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        # Попытка извлечь заголовок
        title = skill_name
        for line in content.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        skills.append({
            "name": skill_name,
            "path": str(md_file),
            "title": title,
            "size": len(content)
        })
    return skills

def list_configs():
    """Собрать содержимое config.yaml и .env (без паролей)."""
    configs = {}
    config_file = HERMES_HOME / "config.yaml"
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8", errors="ignore") as f:
            configs["config.yaml"] = f.read()
    env_file = HERMES_HOME / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8", errors="ignore") as f:
            # Маскируем значения ключей
            lines = []
            for line in f:
                if "=" in line:
                    key, val = line.split("=", 1)
                    lines.append(f"{key}=***скрыто***")
                else:
                    lines.append(line)
            configs[".env"] = "\n".join(lines)
    return configs

def list_policies():
    """Содержимое agent_policies.md, если есть."""
    policy_file = HERMES_HOME / "agent_policies.md"
    if policy_file.exists():
        with open(policy_file, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return "Файл не найден."

def list_identity():
    """SELF_IDENTITY.md."""
    id_file = HERMES_HOME / "SELF_IDENTITY.md"
    if id_file.exists():
        with open(id_file, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return "Файл не найден."

def generate_html(packages, scripts, skills, configs, policies, identity):
    """Сгенерировать HTML-отчёт."""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Hermes Inventory Report</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 40px; background: #0d1117; color: #c9d1d9; }}
        h1, h2 {{ color: #58a6ff; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 30px; }}
        th, td {{ border: 1px solid #30363d; padding: 8px 12px; text-align: left; }}
        th {{ background: #161b22; }}
        pre {{ background: #161b22; padding: 15px; border-radius: 6px; overflow-x: auto; }}
        .section {{ margin-bottom: 40px; }}
        code {{ color: #f0883e; }}
    </style>
</head>
<body>
<h1>🧠 Hermes Inventory Report</h1>
<p>Сгенерирован: {now} | HERMES_HOME: {HERMES_HOME}</p>

<div class="section">
    <h2>1. Установленные пакеты (Python venv)</h2>
    <table>
        <tr><th>Пакет</th><th>Версия</th></tr>
        {''.join(f"<tr><td>{p.get('name', p.get('Name', 'unknown'))}</td><td>{p.get('version', p.get('Version', 'unknown'))}</td></tr>" for p in packages)}
    </table>
</div>

<div class="section">
    <h2>2. Скрипты в scripts/</h2>
    <table>
        <tr><th>Файл</th><th>Описание (docstring)</th></tr>
        {''.join(f"<tr><td><code>{s['name']}</code></td><td>{s['description'][:200]}</td></tr>" for s in scripts)}
    </table>
</div>

<div class="section">
    <h2>3. Скиллы (SKILL.md)</h2>
    <table>
        <tr><th>Название</th><th>Путь</th><th>Заголовок</th><th>Размер (символов)</th></tr>
        {''.join(f"<tr><td>{sk['name']}</td><td><code>{sk['path']}</code></td><td>{sk['title']}</td><td>{sk['size']}</td></tr>" for sk in skills)}
    </table>
</div>

<div class="section">
    <h2>4. Конфигурация</h2>
    <h3>config.yaml</h3>
    <pre>{configs.get('config.yaml', 'Нет')}</pre>
    <h3>.env (ключи скрыты)</h3>
    <pre>{configs.get('.env', 'Нет')}</pre>
</div>

<div class="section">
    <h2>5. Agent Policies</h2>
    <pre>{policies}</pre>
</div>

<div class="section">
    <h2>6. Самоидентификация (SELF_IDENTITY.md)</h2>
    <pre>{identity[:5000]}</pre>
    <p>... (обрезано для краткости)</p>
</div>

</body>
</html>"""
    with open(HTML_REPORT, "w", encoding="utf-8") as f:
        f.write(html)
    return HTML_REPORT

if __name__ == "__main__":
    print("🔍 Сбор данных...")
    packages = get_pip_list()
    scripts = list_scripts()
    skills = list_skills()
    configs = list_configs()
    policies = list_policies()
    identity = list_identity()
    
    print(f"   Найдено пакетов: {len(packages)}")
    print(f"   Найдено скриптов: {len(scripts)}")
    print(f"   Найдено скиллов: {len(skills)}")
    print(f"   Размер конфигураций: {len(configs)}")
    
    report_path = generate_html(packages, scripts, skills, configs, policies, identity)
    print(f"\n✅ Отчёт сохранён в: {report_path}")
    webbrowser.open(f"file:///{report_path.resolve().as_posix()}")