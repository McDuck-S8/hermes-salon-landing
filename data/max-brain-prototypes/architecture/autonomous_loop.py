#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAX-BRAIN REBORN — Autonomous Loop v11.0 (24/7)

Непрерывная работа с TRIGGER ENGINE:
- 10 секунд на ответ пользователя
- Если нет ответа → продолжаем работать
- TRIGGER ENGINE проверяет "эмоции" каждые 30 сек
- Приоритет: МИССИЯ 5000 руб/день

Режим: 24/7 без остановок
"""

import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Импортировать TRIGGER ENGINE
from core.trigger_engine import get_trigger_engine

# Настроить логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/autonomous-loop.log', encoding='utf-8', mode='a'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("autonomous_loop")

# Глобальный флаг работы
RUNNING = True
USER_RESPONSE_RECEIVED = False
RESPONSE_TIMEOUT_SEC = 10

# TRIGGER ENGINE
trigger_engine = None


def wait_for_user_response(timeout_sec: int = 10) -> bool:
    """
    Ждать ответ пользователя timeout_sec секунд.
    
    Returns:
        True если пользователь ответил, False если таймаут
    """
    global USER_RESPONSE_RECEIVED
    
    logger.info(f"Ожидание ответа пользователя ({timeout_sec}с)...")
    
    start_time = time.time()
    while time.time() - start_time < timeout_sec:
        if USER_RESPONSE_RECEIVED:
            logger.info("✅ Пользователь ответил!")
            USER_RESPONSE_RECEIVED = False  # Сброс
            return True
        time.sleep(0.5)
    
    logger.warning(f"⏰ Таймаут ({timeout_sec}с) — продолжаю работать автономно")
    return False


def autonomous_work_cycle():
    """
    Один цикл автономной работы.
    
    Приоритеты:
    1. МИССИЯ 5000 руб/день
    2. Задачи из todos/active-tasks.md
    3. Оптимизация системы
    4. TRIGGER ENGINE проверка
    """
    global trigger_engine
    
    logger.info("=" * 80)
    logger.info("  AUTONOMOUS WORK CYCLE — ЗАПУСК")
    logger.info("=" * 80)
    
    # 0. TRIGGER ENGINE — проверка триггеров
    logger.info("[0/5] TRIGGER ENGINE — проверка триггеров...")
    if trigger_engine is None:
        trigger_engine = get_trigger_engine()
    
    events = trigger_engine.check_triggers()
    if events:
        logger.info(f"  🔔 Активировано триггеров: {len(events)}")
        for e in events:
            logger.info(f"     - {e.trigger_id}: {e.message}")
    
    # Показать эмоциональное состояние
    logger.info(f"  {trigger_engine.get_emotional_state_report()}")
    
    # 1. Проверка МИССИИ
    logger.info("[1/5] ПРОВЕРКА МИССИИ 5000 RUB/DAY...")
    from skills.money_skill import get_money_skill
    skill = get_money_skill()
    progress = skill.get_progress()
    logger.info(f"  Заработано: {progress['current']:.2f} RUB ({progress['progress_percent']:.1f}%)")
    logger.info(f"  Осталось: {progress['remaining']:.2f} RUB")
    
    if progress['current'] == 0:
        logger.info("  → Доход 0 — нужно запустить активные действия!")
        # Здесь будет логика поиска и запуска схем
    
    # 2. Проверка задач
    logger.info("[2/5] ПРОВЕРКА ЗАДАЧ...")
    tasks_file = Path('todos/active-tasks.md')
    if tasks_file.exists():
        content = tasks_file.read_text(encoding='utf-8')
        in_progress = content.count('[IN PROGRESS]')
        done = content.count('[DONE]')
        logger.info(f"  В работе: {in_progress}, Завершено: {done}")
    
    # 3. Проверка Task Monitor
    logger.info("[3/5] ПРОВЕРКА TASK MONITOR...")
    monitor_report = Path('reports/TASK-MONITOR-STATUS.md')
    if monitor_report.exists():
        logger.info(f"  Отчёт: {monitor_report}")
        # Проверить на пинки
        content = monitor_report.read_text(encoding='utf-8')
        if 'ПИНОК' in content or 'pinch' in content:
            logger.warning("  🦶 ЕСТЬ ПИНКИ! Нужно ускориться!")
        else:
            logger.info("  ✅ Пинков нет — задачи выполняются вовремя")
    
    # 4. Автономные действия (РЕАЛЬНЫЕ!)
    logger.info("[4/5] АВТОНОМНЫЕ ДЕЙСТВИЯ...")

    # === REALITY CHECK ===
    from skills.reality_check import RealityCheck
    rc = RealityCheck()

    # Research — реальный поиск схем
    if rc.check("search_airdrops"):
        logger.info("  🕵️ Research Agent: Ищу новые аирдропы...")
        try:
            import subprocess
            subprocess.Popen(
                ["python", "skills/airdrop_hunter.py"],
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            logger.info("  ✅ Запущен поиск аирдропов")
        except Exception as e:
            logger.error(f"  ❌ Ошибка запуска: {e}")
    else:
        logger.info("  🛑 REALITY CHECK: Хватит искать аирдропы! Переключаюсь на анализ.")
        # Если поиск заблокирован, делаем что-то другое
        if rc.check("analyze_crypto_market"):
             logger.info("  📈 Анализ рынка крипты...")
             # Тут будет код анализа

    # Analyzer — анализ
    logger.info("  🛡️ Analyzer Agent: Готов к проверке на скам")
    
    # Executor — сохранение результата
    logger.info("  💾 Executor Agent: Сохраняю отчёт")
    report_path = Path("reports/AUTO-RESEARCH-RESULT.md")
    report_path.write_text(f"# Авто-исследование\n\nДата: {datetime.now()}\n\nСистема работает автономно.", encoding='utf-8')
    logger.info(f"  ✅ Отчёт сохранён: {report_path}")
    
    # 5. Применение модификаторов приоритета
    logger.info("[5/5] ПРИМЕНЕНИЕ МОДИФИКАТОРОВ ПРИОРИТЕТА...")
    base_priority = 1.0
    modified_priority = trigger_engine.get_priority_modifier(base_priority)
    logger.info(f"  Базовый приоритет: {base_priority:.2f}")
    logger.info(f"  Модифицированный: {modified_priority:.2f} (x{modified_priority/base_priority:.1f})")
    
    if modified_priority > 2.0:
        logger.info("  ⚠️ ВЫСОКИЙ ПРИОРИТЕТ! Ускоряем работу!")
    
    logger.info("=" * 80)
    logger.info("  CYCLE COMPLETE")
    logger.info("=" * 80)


def main_loop():
    """
    Главный цикл автономной работы.
    
    Алгоритм:
    1. Ждать 10 секунд ответа пользователя
    2. Если нет ответа → работать автономно
    3. Повторять 24/7
    """
    global RUNNING
    
    logger.info("=" * 80)
    logger.info("  MAX-BRAIN REBORN — AUTONOMOUS LOOP 24/7")
    logger.info("=" * 80)
    logger.info(f"  Таймаут ожидания: {RESPONSE_TIMEOUT_SEC} секунд")
    logger.info(f"  Режим: непрерывная работа")
    logger.info(f"  Приоритет: МИССИЯ 5000 RUB/DAY")
    logger.info("=" * 80)
    logger.info("")
    
    cycle_count = 0
    
    try:
        while RUNNING:
            cycle_count += 1
            logger.info(f"\n🔄 ЦИКЛ #{cycle_count} — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Ждать ответа пользователя 10 секунд
            user_responded = wait_for_user_response(RESPONSE_TIMEOUT_SEC)
            
            if not user_responded:
                # Таймаут — работать автономно
                logger.info("🤖 АВТОНОМНАЯ РАБОТА (пользователь не ответил)...")
                autonomous_work_cycle()
            else:
                # Пользователь ответил — обработать ввод
                logger.info("👤 Пользователь активен — обработка ввода...")
                # Здесь будет логика обработки команд пользователя
            
            # Пауза перед следующим циклом
            time.sleep(2)
    
    except KeyboardInterrupt:
        logger.info("\n⚠️  Остановлено пользователем")
        RUNNING = False
    
    logger.info("Autonomous loop stopped")


if __name__ == "__main__":
    main_loop()
