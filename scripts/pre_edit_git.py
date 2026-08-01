#!/usr/bin/env python3
"""
Pre-edit Git Versioning Hook.
ВАЖНО: перед ЛЮБЫМ редактированием файла — версия (git stash или git add + commit).
Это предотвращает потерю работы и позволяет откат.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def git_version_before_edit(file_path: str) -> bool:
    """Создаёт версию файла перед редактированием."""
    try:
        # Проверяем, что файл существует
        f = ROOT / file_path
        if not f.exists():
            print(f"⚠️  File not found: {file_path} — создаём новый, версия не нужна")
            return True
        
        # Проверяем git статус
        result = subprocess.run(
            ["git", "status", "--porcelain", file_path],
            cwd=str(ROOT), capture_output=True, text=True, timeout=10
        )
        
        if result.stdout.strip():
            # Файл уже изменен — делаем коммит текущих изменений
            print(f"📦 File {file_path} has uncommitted changes — committing first")
            subprocess.run(["git", "add", file_path], cwd=str(ROOT), check=True, timeout=10)
            subprocess.run(["git", "commit", "-m", f"pre-edit snapshot: {file_path}"], cwd=str(ROOT), check=True, timeout=15)
        else:
            # Чистый файл — делаем stash для возможности отката
            print(f"📦 Clean file {file_path} — stashing for rollback")
            subprocess.run(["git", "stash", "push", "-m", f"pre-edit stash: {file_path}", "--", file_path], 
                         cwd=str(ROOT), check=True, timeout=10)
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git versioning failed for {file_path}: {e}")
        return False
    except Exception as e:
        print(f"❌ Git versioning error: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python pre_edit_git.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    success = git_version_before_edit(file_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()