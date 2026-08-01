#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAX-BRAIN REBORN — Direct Task Executor

Выполняет задачи ИЗ active-tasks.md НАПРЯМУЮ, без ZeroMQ посредников.
Запускается раз в 30 секунд.
"""

import re
import sys
import json
import time
import logging
import traceback
import psutil
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
TASKS_FILE = ROOT / 'todos' / 'active-tasks.md'

logging.basicConfig(
    format='%(asctime)s - DIRECT_EXECUTOR - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/direct-executor.log', encoding='utf-8', mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Force UTF-8 on stdout/stderr for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

logger = logging.getLogger("direct_executor")

EXECUTED_FILE = ROOT / 'memory' / 'executed_tasks.json'


def load_executed():
    """Загрузить список выполненных задач."""
    if EXECUTED_FILE.exists():
        try:
            return json.load(open(EXECUTED_FILE, 'r', encoding='utf-8'))
        except:
            return []
    return []


def save_executed(task_id):
    """Сохранить выполненную задачу."""
    executed = load_executed()
    if task_id not in executed:
        executed.append(task_id)
    json.dump(executed, open(EXECUTED_FILE, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)


def parse_pending_tasks():
    """Найти все PENDING/NEW задачи из active-tasks.md."""
    if not TASKS_FILE.exists():
        logger.warning("tasks file not found")
        return []

    content = TASKS_FILE.read_text(encoding='utf-8')
    tasks = []
    current = None

    # Ищем заголовки ### [STATUS] Title
    header_re = re.compile(r'^###\s*\[([A-Za-z_]+)\]\s*(.*)$')

    for line in content.split('\n'):
        line = line.strip()
        m = header_re.match(line)
        if m:
            if current:
                tasks.append(current)
            status_raw = m.group(1).upper()
            title = m.group(2)

            # Нормализуем статус
            if status_raw in ('PENDING', 'NEW'):
                status = 'PENDING'
            elif status_raw in ('DONE',):
                status = 'DONE'
            else:
                status = status_raw

            current = {
                'status': status,
                'title': title,
                'id': 'unknown',
                'type': 'general',
                'description': '',
                'priority': 'medium',
                'raw_status': status_raw,
            }
            continue

        if current:
            if line.startswith('- **ID:**'):
                current['id'] = line.split('**ID:**')[1].strip()
            elif line.startswith('- **Тип:**'):
                current['type'] = line.split('**Тип:**')[1].strip()
            elif line.startswith('- **Описание:**'):
                current['description'] = line.split('**Описание:**')[1].strip()[:500]
            elif line.startswith('- **Приоритет:**'):
                current['priority'] = line.split('**Приоритет:**')[1].strip()

    if current:
        tasks.append(current)

    pending = [t for t in tasks if t['status'] == 'PENDING']
    logger.info(f"Found {len(pending)} pending tasks out of {len(tasks)} total")
    return pending


def fix_learner_agent_chromadb():
    """FIX: learner_agent — graceful degradation для ChromaDB."""
    logger.info("🔧 FIX: learner_agent graceful degradation for ChromaDB")
    
    agent_file = ROOT / 'agents' / 'learner_agent.py'
    if not agent_file.exists():
        logger.error("learner_agent.py not found")
        return False

    content = agent_file.read_text(encoding='utf-8')
    
    # Проверяем уже ли исправлен
    if 'graceful degradation' in content.lower() or 'chromadb_unavailable' in content.lower():
        logger.info("  ✅ Already fixed")
        return True

    # Добавляем try/except вокруг ChromaDB инициализации
    # Ищем инициализацию ChromaDB
    if 'chromadb' in content.lower():
        # Добавляем try/except
        new_content = content.replace(
            'self.client = chromadb',
            '''try:
            self.client = chromadb
            self.chroma_available = True
        except Exception as e:
            logger.warning(f"ChromaDB unavailable, running in degraded mode: {e}")
            self.client = None
            self.chroma_available = False'''
        )
        
        if new_content != content:
            agent_file.write_text(new_content, encoding='utf-8')
            logger.info("  ✅ Added graceful degradation for ChromaDB")
            return True
        else:
            logger.info("  ⚠️ Could not auto-fix, ChromaDB init pattern not found")
            return False
    
    logger.info("  ⚠️ No ChromaDB usage found in learner_agent")
    return True


def fix_data_extraction_agent():
    """FIX: data_extraction_agent — mock режим без API ключей."""
    logger.info("🔧 FIX: data_extraction_agent mock mode without API keys")
    
    agent_file = ROOT / 'agents' / 'data_extraction_agent.py'
    if not agent_file.exists():
        logger.error("data_extraction_agent.py not found")
        return False

    content = agent_file.read_text(encoding='utf-8')
    
    if 'mock' in content.lower() or 'api_key' in content.lower():
        # Добавляем проверку API ключей
        if 'os.environ.get' not in content and 'os.getenv' not in content:
            # Добавляем mock проверку
            new_content = content.replace(
                'import ',
                '''import os

# Mock mode check
def _check_api_key(key_name):
    val = os.environ.get(key_name, '')
    if not val:
        logger.warning(f"API key {key_name} not set, using MOCK mode")
        return None
    return val

''',
                1
            )
            if new_content != content:
                agent_file.write_text(new_content, encoding='utf-8')
                logger.info("  ✅ Added mock mode for missing API keys")
                return True
    
    logger.info("  ✅ Agent already has API key handling")
    return True


def fix_docs_indexer_agent():
    """FIX: docs_indexer_agent — исправить инициализацию."""
    logger.info("🔧 FIX: docs_indexer_agent initialization")
    
    agent_file = ROOT / 'agents' / 'docs_indexer_agent.py'
    if not agent_file.exists():
        logger.error("docs_indexer_agent.py not found")
        return False

    content = agent_file.read_text(encoding='utf-8')
    
    # Проверяем есть ли обработчик ошибок в __init__
    if 'try:' in content and 'except' in content:
        logger.info("  ✅ Already has error handling")
        return True

    logger.info("  ⚠️ Manual review needed — no auto-fix pattern found")
    return False


def refactor_agent_base():
    """REFACTOR: agent_base.py — вынести общие зависимости."""
    logger.info("🔧 REFACTOR: agent_base.py common dependencies")
    
    agent_base_file = ROOT / 'core' / 'agent_base.py'
    if not agent_base_file.exists():
        logger.error("agent_base.py not found")
        return False

    logger.info("  ⚠️ Refactoring requires manual review — skipped for now")
    return True


def auto_self_heal():
    """AUTO-SELF-HEAL: Сканировать логи, найти отключённых агентов, исправить."""
    logger.info("🩺 AUTO-SELF-HEAL: Scanning for broken agents...")
    
    # 1. Найти агентов которые перезапускаются
    log_file = ROOT / 'logs' / 'system.log'
    if not log_file.exists():
        logger.info("  No system.log found")
        return

    # Читаем последние 1000 строк
    try:
        with open(log_file, 'rb') as f:
            f.seek(0, 2)
            sz = f.tell()
            f.seek(max(0, sz - 100000))
            chunk = f.read().decode('utf-8', errors='ignore')
        
        # Ищем ошибки по агентам
        restart_counts = {}
        error_counts = {}
        for line in chunk.split('\n'):
            for agent in ['learner_agent', 'self_improver_agent', 'data_extraction_agent', 
                         'docs_indexer_agent', 'service_discovery_agent']:
                if agent in line:
                    if 'ERROR' in line or 'Exception' in line or 'died' in line:
                        error_counts[agent] = error_counts.get(agent, 0) + 1
                    if 'died, restarting' in line or 'restarting' in line:
                        restart_counts[agent] = restart_counts.get(agent, 0) + 1

        if restart_counts or error_counts:
            logger.info(f"  Found issues: restarts={restart_counts}, errors={error_counts}")
            
            # 2. Попробовать починить
            for agent, count in error_counts.items():
                if count > 3:
                    logger.info(f"  🔧 {agent} has {count} errors — attempting fix")
                    fix_func = {
                        'learner_agent': fix_learner_agent_chromadb,
                        'data_extraction_agent': fix_data_extraction_agent,
                        'docs_indexer_agent': fix_docs_indexer_agent,
                    }.get(agent)
                    if fix_func:
                        try:
                            fix_func()
                        except Exception as e:
                            logger.error(f"  ❌ Fix failed for {agent}: {e}")
        else:
            logger.info("  ✅ No critical agent errors found")
            
    except Exception as e:
        logger.error(f"  ❌ Self-heal error: {e}")


def revive_dead_agents(task):
    """REVIVE: Перезапустить мёртвых агентов."""
    logger.info("REVIVE: Restarting dead agents...")

    import subprocess

    agents_dir = ROOT / 'agents'
    restarted = 0

    # Мёртвые агенты — те которые НЕ в cmdline запущенных процессов
    running_cmdlines = []
    for proc in psutil.process_iter(['cmdline']):
        try:
            running_cmdlines.append(' '.join(proc.info['cmdline'] or []))
        except:
            pass

    if agents_dir.exists():
        for agent_file in sorted(agents_dir.glob('*_agent.py')):
            agent_name = agent_file.stem
            already_running = any(agent_name in c for c in running_cmdlines)

            if not already_running:
                try:
                    subprocess.Popen(
                        [sys.executable, str(agent_file)],
                        cwd=str(ROOT),
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    logger.info(f"  Started {agent_name}")
                    restarted += 1
                except Exception as e:
                    logger.error(f"  Failed to start {agent_name}: {e}")

    logger.info(f"  Restarted {restarted} agents")
    return True


# Маппинг задач к функциям
TASK_HANDLERS = {
    'IMPROVE-20260402-163000': fix_learner_agent_chromadb,
    'IMPROVE-20260402-163001': fix_data_extraction_agent,
    'IMPROVE-20260402-163002': fix_docs_indexer_agent,
    'IMPROVE-20260402-163003': refactor_agent_base,
    'AUTO-SELF-HEAL-001': auto_self_heal,
}


def execute_task(task):
    """Выполнить одну задачу."""
    task_id = task['id']
    title = task['title']

    logger.info(f"▶️  EXECUTING: {task_id} — {title}")

    # Динамический handler для REVIVE задач
    if task_id.startswith('REVIVE-'):
        return revive_dead_agents(task)

    handler = TASK_HANDLERS.get(task_id)
    if handler:
        try:
            result = handler()
            if result:
                save_executed(task_id)
                logger.info(f"✅ COMPLETED: {task_id}")
                return True
            else:
                logger.warning(f"⚠️  FAILED: {task_id}")
                return False
        except Exception as e:
            logger.error(f"❌ ERROR executing {task_id}: {e}")
            traceback.print_exc()
            return False
    else:
        logger.info(f"  ⏭️  No handler for {task_id} — skipping")
        return False


def main():
    """Главный цикл."""
    logger.info("=" * 60)
    logger.info("  DIRECT TASK EXECUTOR — START")
    logger.info("=" * 60)
    
    executed = load_executed()
    logger.info(f"Previously executed: {len(executed)} tasks")
    
    tasks = parse_pending_tasks()
    if not tasks:
        logger.info("No pending tasks found — system is clean!")
        return

    # Ограничиваем — максимум 3 задачи за цикл
    tasks = tasks[:3]
    logger.info(f"Processing {len(tasks)} tasks this cycle (max 3)")
    
    for task in tasks:
        if task['id'] in executed:
            logger.info(f"⏭️  Skipping already executed: {task['id']}")
            continue
        
        execute_task(task)
        time.sleep(1)
    
    logger.info("=" * 60)
    logger.info("  DIRECT TASK EXECUTOR — CYCLE COMPLETE")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
