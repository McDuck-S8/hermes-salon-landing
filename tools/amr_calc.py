#!/usr/bin/env python3
"""
AMR Calculator — Agentic Margin Ratio
Формула: AM = Revenue - Cost; AMR = AM / Revenue * 100%

Использование:
    python amr_calc.py                    # интерактивный режим
    python amr_calc.py 0.22 5.00          # cost revenue (простой)
    python amr_calc.py --compare          # сравнение нескольких агентов
"""

import sys
import json
from datetime import datetime


def calculate_amr(cost: float, revenue: float) -> dict:
    """Calculate AMR for a single agent."""
    am = revenue - cost
    amr = (am / revenue * 100) if revenue > 0 else 0
    return {
        "cost": cost,
        "revenue": revenue,
        "absolute_margin": round(am, 4),
        "amr_percent": round(amr, 2),
        "verdict": "GREEN" if amr > 50 else ("YELLOW" if amr > 30 else "RED")
    }


def interactive_mode():
    """Interactive AMR calculator."""
    print("=" * 50)
    print("  AMR Calculator — Agentic Margin Ratio")
    print("  Formula: AM = Revenue - Cost; AMR = AM/Revenue*100")
    print("=" * 50)
    print()
    
    agents = []
    
    while True:
        print(f"\n--- Агент #{len(agents) + 1} ---")
        
        name = input("Имя агента (Enter для пропуска): ").strip()
        if not name:
            name = f"Agent #{len(agents) + 1}"
        
        try:
            cost = float(input("Стоимость за interaction ($): "))
            revenue = float(input("Доход за interaction ($): "))
        except ValueError:
            print("Ошибка: введи число")
            continue
        
        result = calculate_amr(cost, revenue)
        result["name"] = name
        agents.append(result)
        
        print(f"\n  Cost: ${result['cost']}")
        print(f"  Revenue: ${result['revenue']}")
        print(f"  Absolute Margin: ${result['absolute_margin']}")
        print(f"  AMR: {result['amr_percent']}%")
        print(f"  Verdict: {result['verdict']}")
        
        if result['verdict'] == "GREEN":
            print("  ✅ ЗЕЛЁНЫЙ СВЕТ — масштабируй!")
        elif result['verdict'] == "YELLOW":
            print("  ⚠️  ОСТОРОЖНО — дорабатывай pricing")
        else:
            print("  🛑 СТОП — меняй модель или capabilities")
        
        cont = input("\nДобавить ещё агента? (y/n): ").strip().lower()
        if cont != 'y':
            break
    
    if len(agents) > 1:
        print("\n" + "=" * 60)
        print("  СРАВНЕНИЕ АГЕНТОВ")
        print("=" * 60)
        agents_sorted = sorted(agents, key=lambda x: x['amr_percent'], reverse=True)
        print(f"\n{'Имя':<20} {'Cost':>8} {'Revenue':>8} {'AM':>8} {'AMR':>8} {'Статус':<8}")
        print("-" * 60)
        for a in agents_sorted:
            status = "GREEN" if a['verdict'] == "GREEN" else ("YELLOW" if a['verdict'] == "YELLOW" else "RED")
            print(f"{a['name']:<20} ${a['cost']:>6.2f} ${a['revenue']:>6.2f} ${a['absolute_margin']:>6.2f} {a['amr_percent']:>6.1f}% {status:<8}")
        
        best = agents_sorted[0]
        worst = agents_sorted[-1]
        print(f"\nЛучший: {best['name']} (AMR {best['amr_percent']}%)")
        print(f"Худший: {worst['name']} (AMR {worst['amr_percent']}%)")
    
    # Save results
    save = input("\nСохранить в JSON? (y/n): ").strip().lower()
    if save == 'y':
        filename = f"amr_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump({"timestamp": datetime.now().isoformat(), "agents": agents}, f, indent=2)
        print(f"Сохранено: {filename}")


def cli_mode(args):
    """CLI mode: python amr_calc.py <cost> <revenue>"""
    if args[0] == "--compare":
        print("Сравнение: запусти без аргументов для интерактивного режима")
        return
    
    cost = float(args[0])
    revenue = float(args[1])
    name = args[2] if len(args) > 2 else "Agent"
    
    result = calculate_amr(cost, revenue)
    result["name"] = name
    
    print(f"Agent: {name}")
    print(f"Cost: ${result['cost']}")
    print(f"Revenue: ${result['revenue']}")
    print(f"Absolute Margin: ${result['absolute_margin']}")
    print(f"AMR: {result['amr_percent']}%")
    print(f"Verdict: {result['verdict']}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli_mode(sys.argv[1:])
    else:
        interactive_mode()
