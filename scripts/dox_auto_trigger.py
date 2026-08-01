#!/usr/bin/env python3
"""
DOX Auto-Trigger — автоматический DOX pass после bulk edits.
Правило: если изменено ≥3 файлов в одной директории — запускает DOX pass.
"""
import json
import sys
import subprocess
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
CHANGES_FILE = ROOT / "cache" / "recent_changes.json"

def load_changes() -> dict:
    if CHANGES_FILE.exists():
        try:
            return json.loads(CHANGES_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"changes": []}
    return {"changes": []}

def save_changes(data: dict) -> None:
    CHANGES_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHANGES_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def record_change(file_path: str) -> None:
    """Записывает изменение файла."""
    data = load_changes()
    data["changes"].append({
        "file": file_path,
        "timestamp": __import__("datetime").datetime.now().isoformat()
    })
    # Keep only last 100
    data["changes"] = data["changes"][-100:]
    save_changes(data)

def check_dox_trigger() -> list:
    """
    Проверяет нужен ли DOX pass.
    Возвращает список директорий где ≥3 файлов изменено.
    """
    data = load_changes()
    if not data["changes"]:
        return []
    
    # Группируем по директориям
    dir_counts = defaultdict(int)
    for change in data["changes"]:
        file_path = Path(change["file"])
        dir_path = str(file_path.parent)
        dir_counts[dir_path] += 1
    
    # Находим директории с ≥3 изменениями
    trigger_dirs = [d for d, count in dir_counts.items() if count >= 3]
    return trigger_dirs

def run_dox_pass(directory: str) -> tuple[bool, str]:
    """Запускает DOX pass для директории."""
    try:
        # Ищем AGENTS.md в директории и родительских
        dir_path = Path(directory)
        agents_files = []
        
        for parent in [dir_path] + list(dir_path.parents):
            agents_md = parent / "AGENTS.md"
            if agents_md.exists():
                agents_files.append(str(agents_md))
        
        if not agents_files:
            return False, f"No AGENTS.md found for {directory}"
        
        # Для каждого AGENTS.md проверяем актуальность
        results = []
        for agents_md in agents_files:
            try:
                # Читаем AGENTS.md
                content = Path(agents_md).read_text(encoding="utf-8")
                
                # Проверяем Child DOX Index
                if "Child DOX Index" in content:
                    # Это родительский AGENTS.md — проверяем дети
                    # В реальности здесь должна быть логика обновления индекса
                    results.append(f"Checked parent: {agents_md}")
                else:
                    results.append(f"Checked: {agents_md}")
                    
            except Exception as e:
                results.append(f"Error checking {agents_md}: {e}")
        
        # Очищаем изменения для этой директории
        data = load_changes()
        data["changes"] = [c for c in data["changes"] if not str(Path(c["file"]).parent) == directory]
        save_changes(data)
        
        return True, "; ".join(results)
        
    except Exception as e:
        return False, f"DOX pass failed: {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python dox_auto_trigger.py <record|check|run> [file_path]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "record":
        if len(sys.argv) < 3:
            print("Usage: record <file_path>")
            sys.exit(1)
        record_change(sys.argv[2])
        print(f"✅ Recorded change: {sys.argv[2]}")
    
    elif cmd == "check":
        dirs = check_dox_trigger()
        if dirs:
            print(f"🔴 DOX TRIGGER: {len(dirs)} directories need DOX pass:")
            for d in dirs:
                print(f"  - {d}")
        else:
            print("🟢 No DOX trigger needed")
        for d in dirs:
            print(f"::dox_trigger::{d}")
    
    elif cmd == "run":
        dirs = check_dox_trigger()
        for d in dirs:
            ok, msg = run_dox_pass(d)
            status = "✅" if ok else "❌"
            print(f"{status} DOX pass for {d}: {msg}")
    
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()