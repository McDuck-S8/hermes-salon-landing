#!/usr/bin/env python3
"""
General Worker — General purpose worker for testing and basic tasks.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from worker_base import WorkerBase, log_team_event

HERMES_HOME = Path(__file__).resolve().parent.parent.parent


class GeneralWorker(WorkerBase):
    """General purpose worker for testing."""
    
    def __init__(self, worker_id: str):
        super().__init__(worker_id, "general_worker")
    
    def execute(self, task_data: Dict) -> Dict:
        """Execute general task."""
        description = task_data.get("description", "")
        context = task_data.get("context", {})
        
        log_team_event("worker_executing", self.worker_id, f"Executing: {description[:80]}")
        
        # Simple task execution based on description
        if "landing" in description.lower() and "create" in description.lower():
            return self._create_landing(context)
        elif "review" in description.lower():
            return {"message": "Review task - would delegate to review_worker", "delegated": True}
        elif "research" in description.lower():
            return self._do_research(context)
        elif "content" in description.lower() and "create" in description.lower():
            return self._create_content(context)
        else:
            return {"message": f"General worker completed: {description}", "status": "done", "worker": self.worker_id}
    
    def _create_landing(self, context: Dict) -> Dict:
        """Create a simple landing page."""
        # This would normally call Forge or generate HTML
        landing_html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Салон Красоты - Премиальный Уход</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .hero {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 80px 20px; text-align: center; }}
        .hero h1 {{ font-size: 3rem; margin-bottom: 1rem; }}
        .hero p {{ font-size: 1.3rem; margin-bottom: 2rem; max-width: 600px; margin-left: auto; margin-right: auto; }}
        .cta-btn {{ background: #ff6b6b; color: white; padding: 18px 40px; border: none; border-radius: 50px; font-size: 1.1rem; cursor: pointer; text-decoration: none; display: inline-block; }}
        .cta-btn:hover {{ background: #ff5252; }}
        .benefits {{ padding: 60px 20px; max-width: 1000px; margin: 0 auto; }}
        .benefits h2 {{ text-align: center; margin-bottom: 3rem; font-size: 2.5rem; }}
        .benefit-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; }}
        .benefit-card {{ padding: 2rem; background: #f8f9fa; border-radius: 15px; text-align: center; }}
        .benefit-card h3 {{ margin-bottom: 1rem; color: #667eea; }}
        .social-proof {{ background: #f8f9fa; padding: 60px 20px; text-align: center; }}
        .testimonials {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; max-width: 1000px; margin: 2rem auto 0; }}
        .testimonial {{ background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .footer {{ background: #333; color: white; padding: 40px 20px; text-align: center; }}
    </style>
</head>
<body>
    <section class="hero">
        <h1>STOP переплачивать за уход за собой!</h1>
        <p>Откройте секрет премиального сервиса по цене обычного салона. Первая процедура — скидка 50%.</p>
        <a href="#booking" class="cta-btn">Забронировать со скидкой 50%</a>
    </section>
    
    <section class="benefits">
        <h2>Почему 2000+ клиентов выбирают нас</h2>
        <div class="benefit-grid">
            <div class="benefit-card">
                <h3>🎯 Мастера-топы</h3>
                <p>Только профи с опытом 5+ лет. Постоянно проходят обучение за рубежом.</p>
            </div>
            <div class="benefit-card">
                <h3>💎 Премиум косметика</h3>
                <p>Работаем только с профессиональными линиями: Kerastase, Olaplex, Moroccanoil, OPI.</p>
            </div>
            <div class="benefit-card">
                <h3>⏰ Удобное время</h3>
                <p>Открыты с 9:00 до 22:00 без выходных. Запись онлайн за 30 секунд.</p>
            </div>
            <div class="benefit-card">
                <h3>🛡 Гарантия результата</h3>
                <p>Если не понравилось — переделаем бесплатно или вернем деньги.</p>
            </div>
        </div>
    </section>
    
    <section class="social-proof">
        <h2>Что говорят клиенты</h2>
        <div class="testimonials">
            <div class="testimonial">
                <p>"Лучший салон в городе! Сделала маникюр и окрашивание — держится 3 недели идеально. Мастера настоящие профи!"</p>
                <strong>— Марина К., 28 отзывов</strong>
            </div>
            <div class="testimonial">
                <p>"Пришла на рекомендацию подруги. Ожидания превзошли — уютная атмосфера, вкусный кофе, результат супер."</p>
                <strong>— Елена С., 15 отзывов</strong>
            </div>
            <div class="testimonial">
                <p>"Муж подарил сертификат — был в шоке от качества. Теперь клиент навсегда. Спасибо команде!"</p>
                <strong>— Анна В., 8 отзывов</strong>
            </div>
        </div>
    </section>
    
    <section id="booking" style="padding: 60px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center;">
        <h2>Забронируйте сейчас и получите скидку 50% на первую процедуру</h2>
        <p>Предложение действует только до конца недели. Осталось мест: <strong id="spots">7</strong></p>
        <a href="https://t.me/your_bot" class="cta-btn" style="background: #ff6b6b; margin-top: 1rem;">Записаться в Telegram</a>
    </section>
    
    <footer class="footer">
        <p>Салон Красоты "Премиум" | г. Симферополь, ул. Пушкина 15 | +7 (978) XXX-XX-XX</p>
        <p>Instagram • Telegram • WhatsApp</p>
    </footer>
    
    <script>
        // Simple urgency counter
        let spots = 7;
        setInterval(() => {{ if (spots > 2) {{ spots--; document.getElementById('spots').textContent = spots; }}, 30000);
        
        // Track clicks
        document.querySelectorAll('a[href^="https://t.me"]').forEach(el => {{
            el.addEventListener('click', () => {{ console.log('CTA clicked'); }});
        }});
    </script>
</body>
</html>"""
        
        # Save landing
        landing_dir = HERMES_HOME / "cache" / "landings"
        landing_dir.mkdir(parents=True, exist_ok=True)
        landing_file = landing_dir / f"landing_{self.task_id}.html"
        landing_file.write_text(landing_html, encoding="utf-8")
        
        return {
            "message": "Landing page created",
            "file": str(landing_file),
            "preview_url": f"file://{landing_file}",
            "status": "done"
        }
    
    def _do_research(self, context: Dict) -> Dict:
        """Perform research task."""
        return {"message": "Research completed", "findings": ["Finding 1", "Finding 2"], "status": "done"}
    
    def _create_content(self, context: Dict) -> Dict:
        """Create content."""
        return {"message": "Content created", "scripts": ["Script 1", "Script 2"], "status": "done"}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No task data"}, ensure_ascii=False))
        sys.exit(1)
    
    try:
        task_data = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print(json.dumps({"success": False, "error": "Invalid JSON"}, ensure_ascii=False))
        sys.exit(1)
    
    worker_id = task_data.get("worker_id", f"general_{os.getpid()}")
    worker = GeneralWorker(worker_id)
    result = worker.run(task_data)
    
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()