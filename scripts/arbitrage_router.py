#!/usr/bin/env python3
"""
Arbitrage Route Calculator v2 — Spider Web Router
Просчитывает маршруты в 3D-паутине: трафик → прокладки → CPA → рефералки → P2P → вывод.

Логика: бюджет тратится на трафик, трафик даёт конверсии, конверсии приносят выплаты.

Запуск:
  python scripts/arbitrage-router.py --all                 # все источники, топ-маршруты
  python scripts/arbitrage-router.py --budget 200          # бюджет $200
  python scripts/arbitrage-router.py --from tiktok          # детально по источнику
  python scripts/arbitrage-router.py --route tiktok carrd cpagrip tbank profit  # конкретный путь
"""

import sys, math
from dataclasses import dataclass, field

# ============== МОДЕЛЬ ==============

@dataclass
class Edge:
    target: str
    label: str
    conv_rate: float = 1.0      # конверсия на этом шаге (0-1)
    fee_pct: float = 0.0        # комиссия в % от суммы
    fee_fixed: float = 0.0      # фикс комиссия $
    time_min: int = 0
    note: str = ""

@dataclass
class Node:
    id: str
    label: str
    z: int                       # плоскость
    traffic_cost_per_1k: float = 0  # $ за 1000 просмотров/посетителей
    payout_per_action: float = 0    # $ за 1 конверсию (CPA)
    edge_cpa_cost: float = 0        # доп затраты на этом узле ($)
    base_conv_to_action: float = 0  # конверсия из посетителя в действие
    edges: list = field(default_factory=list)

# ============== ГРАФ ==============

def build():
    n = {}
    def add(id, label, z, traffic_cost=0, payout=0, edge_cost=0, conv=0):
        n[id] = Node(id=id, label=label, z=z, traffic_cost_per_1k=traffic_cost,
                     payout_per_action=payout, edge_cpa_cost=edge_cost,
                     base_conv_to_action=conv)
    def edge(src, dst, label, conv=1.0, fee_pct=0, fee_fixed=0, time=0, note=""):
        n[src].edges.append(Edge(dst, label, conv, fee_pct, fee_fixed, time, note))

    # ===== Z0: ВХОДЫ — ТРАФИК =====
    add("tiktok",    "TikTok Shorts",     0, traffic_cost=0)     # органика
    add("youtube",   "YouTube Shorts",    0, traffic_cost=0)     # органика
    add("telegram",  "TG каналы (Крым)",  0, traffic_cost=5)     # $5 за пост
    add("reddit",    "Reddit",            0, traffic_cost=0)     # органика
    add("pinterest", "Pinterest",         0, traffic_cost=0)
    add("seo",       "SEO-сайты",         0, traffic_cost=0)

    # ===== Z1: ПРОКЛАДКИ =====
    add("carrd",     "Carrd Landing",     1, traffic_cost=0)
    add("tgbot",     "Telegram Bot",      1, traffic_cost=0)
    add("ghpages",   "GitHub Pages",      1, traffic_cost=0)
    add("seosite",   "SEO микро-сайт",    1, traffic_cost=0)

    # ===== Z2: CPA =====
    add("cpagrip",   "CPAGrip",           2, payout=3.5, conv=0.30)
    add("mylead",    "MyLead",            2, payout=2.5, conv=0.25)
    add("fincpa",    "FinCPANetwork",     2, payout=15,  conv=0.15)
    add("travel",    "Travelpayouts",     2, payout=10,  conv=0.03)
    add("maxbounty", "MaxBounty",         2, payout=8,   conv=0.05)

    # ===== Z3: РЕФЕРАЛКИ (доход = % от оборота приведённых) =====
    add("kucoin-ref","KuCoin RevShare30%",3, payout=0)   # считается отдельно
    add("okx-ref",   "OKX RevShare 30%",  3, payout=0)

    # ===== Z4: P2P АРБИТРАЖ =====
    add("kucoin-p2p","KuCoin P2P",        4, conv=0)     # спред 1.5%
    add("okx-p2p",   "OKX P2P",           4, conv=0)
    add("p2p-cycle", "P2P цикл",          4, conv=0)

    # ===== Z5: ВЫВОД =====
    add("tbank",     "Т-Банк",            5)
    add("crypto",    "Крипта USDT",        5)
    add("profit",    "💰 ПРИБЫЛЬ",        5)

    # ==================== СВЯЗИ ====================

    # Z0 → Z1
    edge("tiktok","carrd",  "TikTok → Carrd",     conv=0.05)  # 5% CTR
    edge("tiktok","tgbot",  "TikTok → TG Bot",    conv=0.03)
    edge("youtube","carrd", "YouTube → Carrd",    conv=0.04)
    edge("telegram","tgbot","TG → TG Bot",        conv=0.08)
    edge("telegram","carrd","TG → Carrd",         conv=0.05)
    edge("reddit","ghpages","Reddit → GH Pages",   conv=0.02)
    edge("reddit","seosite","Reddit → SEO-сайт",  conv=0.03)
    edge("seo","seosite",   "SEO → микро-сайт",   conv=0.01)
    edge("pinterest","carrd","Pin → Carrd",        conv=0.02)

    # Z1 → Z2 (конверсии тут — % от посетителей лендинга в CPA действие)
    edge("carrd","cpagrip",  "Carrd → CPAGrip",    conv=0.30)
    edge("carrd","mylead",   "Carrd → MyLead",     conv=0.25)
    edge("tgbot","fincpa",   "Bot → FinCPA",       conv=0.15)
    edge("tgbot","mylead",   "Bot → MyLead",       conv=0.12)
    edge("ghpages","maxbounty","GH → MaxBounty",   conv=0.05)
    edge("seosite","travel", "SEO → Travelpayouts", conv=0.03)
    edge("seosite","cpagrip","SEO → CPAGrip",      conv=0.04)

    # Z2 → Z3
    edge("cpagrip","kucoin-ref","CPA лиды → KuCoin реф", conv=0.50)
    edge("fincpa","kucoin-ref", "лиды → KuCoin реф",     conv=0.30)
    edge("travel","okx-ref",    "туристы → OKX реф",     conv=0.20)

    # Z2 → Z4
    edge("cpagrip","kucoin-p2p","USDT → KuCoin P2P",    conv=1.0, fee_pct=1.0)
    edge("mylead","kucoin-p2p", "USDT → KuCoin P2P",    conv=1.0, fee_pct=1.5)
    edge("fincpa","kucoin-p2p", "USDT → KuCoin P2P",    conv=1.0, fee_pct=0.5)
    edge("maxbounty","kucoin-p2p","USDT → KuCoin P2P",  conv=1.0, fee_pct=2.0)

    # Z3 → Z4
    edge("kucoin-ref","kucoin-p2p","реф. комиссия → P2P", conv=1.0)
    edge("okx-ref","kucoin-p2p",   "OKX реф → KuCoin P2P",conv=1.0, fee_pct=0.5)

    # Z4 → Z4
    edge("kucoin-p2p","okx-p2p",   "KuCoin → OKX P2P",   conv=1.0, fee_pct=0.3)
    edge("kucoin-p2p","p2p-cycle", "KuCoin P2P цикл",    conv=1.0, fee_pct=0.5)
    edge("okx-p2p","p2p-cycle",    "OKX P2P цикл",       conv=1.0, fee_pct=0.5)

    # Z4 → Z5
    edge("kucoin-p2p","tbank","USDT → Т-Банк",         conv=1.0, fee_pct=0.5, time=15)
    edge("okx-p2p","tbank",    "USDT → Т-Банк",         conv=1.0, fee_pct=0.5, time=15)
    edge("p2p-cycle","tbank",  "P2P цикл → Т-Банк",     conv=1.0, fee_pct=0.5)

    # Cross-plane Z0 → Z2 (минуя лендинг)
    edge("tiktok","cpagrip","TikTok → CPA прямая",      conv=0.01)
    edge("telegram","fincpa","TG → FinCPA прямая",      conv=0.03)

    # Cross-plane Z0 → Z3 (трафик сразу на реф. ссылку)
    edge("youtube","kucoin-ref","YT → KuCoin реф",      conv=0.005)
    edge("telegram","kucoin-ref","TG → KuCoin реф",     conv=0.01)

    # Cross-plane Z2 → Z0 (реинвест)
    edge("cpagrip","tiktok","прибыль → реинвест TikTok", conv=1.0)
    edge("fincpa","telegram","прибыль → TG реклама",     conv=1.0)

    # Cross-plane Z4 → Z0 (реинвест с P2P)
    edge("p2p-cycle","tiktok","P2P → TikTok трафик",     conv=1.0)
    edge("kucoin-p2p","telegram","P2P → TG реклама",     conv=1.0)

    # Z2 → Z5 (вывод напрямую)
    edge("cpagrip","tbank","CPAGrip wire → Т-Банк",     conv=1.0, fee_pct=3.0, time=1440)
    edge("fincpa","tbank","FinCPA wire → Т-Банк",       conv=1.0, fee_pct=2.0, time=2880)

    # Z5 → profit
    edge("tbank","profit", "вывод → 💰",               conv=1.0)
    edge("crypto","profit","крипта → 💰",               conv=1.0)

    return n


# ============== КАЛЬКУЛЯТОР ==============

@dataclass
class RouteResult:
    path: list
    node_labels: list
    edges_labels: list
    visitors_total: int          # всего посетителей с трафика
    cpa_actions: int             # CPA конверсий
    cpa_revenue: float           # $
    fees_total: float            # все комиссии $
    referral_revenue: float      # реферальный доход $
    p2p_profit: float            # P2P арбитраж $
    total_revenue: float
    total_cost: float            # затраты на трафик
    net_profit: float
    roi_pct: float
    time_total: int              # минут до вывода
    details: list = field(default_factory=list)  # пошагово

def calc_route(graph, path_ids, budget=100):
    """
    Симуляция маршрута: на входе budget $ тратится на трафик,
    проходит через все шаги, на выходе — сколько денег.
    """
    if not path_ids or path_ids[0] not in graph:
        return None

    src = graph[path_ids[0]]
    # Сколько посетителей даёт бюджет
    cost_per_visitor = src.traffic_cost_per_1k / 1000 if src.traffic_cost_per_1k > 0 else 0
    if cost_per_visitor > 0:
        visitors = int(budget / cost_per_visitor)
        traffic_cost = budget
    else:
        # Органический трафик — 1 визит ≈ $0, берём 10000 просмотров за "условный бюджет"
        visitors = int(budget * 100)  # $100 = 10,000 просмотров
        traffic_cost = 0

    details = []
    details.append(f"📺 Трафик: {path_ids[0]} → {visitors} посетителей, затраты ${traffic_cost:.2f}")

    amount = visitors
    cpa_revenue = 0
    referal_revenue = 0
    p2p_revenue = 0
    fees = 0
    total_time = 0
    source_name = graph[path_ids[0]].label

    # Проходим по маршруту
    for i in range(len(path_ids) - 1):
        curr = graph[path_ids[i]]
        nxt = graph[path_ids[i+1]]
        edg = None
        for e in curr.edges:
            if e.target == path_ids[i+1]:
                edg = e
                break
        if not edg:
            details.append(f"❌ Нет ребра {path_ids[i]} → {path_ids[i+1]}")
            return None

        conv = edg.conv_rate
        fee_pct = edg.fee_pct
        total_time += edg.time_min

        if nxt.z == 2 and nxt.payout_per_action > 0 and nxt.base_conv_to_action > 0:
            # CPA узел: visitors × baseline_conv → actions × payout
            actions = int(amount * nxt.base_conv_to_action * conv)
            payout_total = actions * nxt.payout_per_action
            cpa_revenue += payout_total
            details.append(f"  CPA {nxt.label}: {amount:.0f} посетителей × {nxt.base_conv_to_action:.0%} × {edg.label.split('→')[-1].strip()} conv={conv:.0%} → {actions} действий × ${nxt.payout_per_action} = ${payout_total:.2f}")
            amount = payout_total  # дальше идут USDT
        elif nxt.z >= 4:
            # P2P / вывод: работаем с USDT суммой
            fee_amount = amount * (fee_pct / 100)
            fees += fee_amount
            amount_after = amount * conv - fee_amount
            p2p_revenue += max(0, amount_after - amount) if nxt.z == 4 else 0
            details.append(f"  {nxt.label}: ${amount:.2f} → conv={conv:.0%} fee={fee_pct:.1f}% = ${amount_after:.2f}")
            amount = max(0, amount_after)
        elif nxt.z == 3:
            # Рефералка: рассчитываем дополнительный доход
            # Предполагаем что 1 реферал даёт $50 оборота × 30% = $15
            ref_actions = int(amount * 0.01 * conv)  # 1% приведённых становятся активными
            ref_income = ref_actions * 15  # $15 с реферала
            referal_revenue += ref_income
            details.append(f"  {nxt.label}: из {amount:.0f} → {ref_actions} рефералов × ${15} = ${ref_income:.2f}")
            amount += ref_income
        else:
            # Прокладка: просто конверсия посетителей
            visitors_after = int(amount * conv)
            details.append(f"  {path_ids[i]} → {path_ids[i+1]}: {amount:.0f} × {conv:.0%} = {visitors_after}")
            amount = visitors_after

    total_revenue = cpa_revenue + referal_revenue + p2p_revenue
    net = total_revenue - traffic_cost - fees
    roi = (net / max(budget, 1)) * 100

    return RouteResult(
        path=path_ids,
        node_labels=[graph[p].label for p in path_ids],
        edges_labels=[],
        visitors_total=visitors,
        cpa_actions=int(cpa_revenue / max(max(graph[p].payout_per_action for p in path_ids), 0.01)) 
                     if any(graph[p].payout_per_action > 0 for p in path_ids) else 0,
        cpa_revenue=cpa_revenue,
        fees_total=fees,
        referral_revenue=referal_revenue,
        p2p_profit=p2p_revenue,
        total_revenue=total_revenue,
        total_cost=traffic_cost + fees,
        net_profit=net,
        roi_pct=roi,
        time_total=total_time,
        details=details
    )


def enumerate_routes(graph, start_id, end_id="profit", budget=100, max_depth=6):
    """Все маршруты от start до end (через DFS с ограничением глубины)."""
    if start_id not in graph or end_id not in graph:
        return []

    results = []

    def dfs(node_id, visited, path, depth):
        if depth > max_depth:
            return
        if node_id == end_id:
            res = calc_route(graph, list(path), budget)
            if res:
                results.append(res)
            return
        node = graph[node_id]
        for e in node.edges:
            if e.target in visited:
                continue
            visited.add(e.target)
            path.append(e.target)
            dfs(e.target, visited, path, depth + 1)
            path.pop()
            visited.remove(e.target)

    dfs(start_id, {start_id}, [start_id], 0)

    # убираем маршруты с нулевой прибылью
    results = [r for r in results if r.net_profit != 0]
    results.sort(key=lambda r: r.net_profit, reverse=True)
    return results


def dedup(routes):
    seen = set()
    uniq = []
    for r in routes:
        key = tuple(r.path)
        if key not in seen:
            seen.add(key)
            uniq.append(r)
    return uniq


# ============== ВЫВОД ==============

def print_all(graph, budget=100):
    sources = {"tiktok":"TikTok","youtube":"YouTube","telegram":"TGканалы",
               "reddit":"Reddit","pinterest":"Pinterest","seo":"SEO"}
    print(f"\n{'='*90}")
    print(f"🕸  ARBITRAGE SPIDER WEB — BEST ROUTES (бюджет ${budget})")
    print(f"{'='*90}")
    print(f"{'Источник':<12} {'ROI':>8} {'Конв.акц':>8} {'Доход':>9} {'Комис':>7} {'Чист':>9} {'Время':>7} {'Маршрут'}")
    print(f"{'-'*12} {'-'*8} {'-'*8} {'-'*9} {'-'*7} {'-'*9} {'-'*7} {'-'*30}")

    for sid, sl in sources.items():
        routes = enumerate_routes(graph, sid, budget=budget)
        routes = dedup(routes)
        if routes:
            best = routes[0]
            cpa_cnt = best.cpa_actions if best.cpa_actions else 0
            route_str = '→'.join(best.path)
            print(f"{sl:<12} {best.roi_pct:>+7.1f}% {cpa_cnt:>8} ${best.total_revenue:>6.1f} ${best.fees_total:>5.1f} ${best.net_profit:>7.2f} {best.time_total:>5}мин {route_str}")
        else:
            print(f"{sl:<12} ❌ нет маршрута")

    print(f"\n💡 Детально: python scripts/arbitrage-router.py --from <source>")
    print(f"💡 Путь:     python scripts/arbitrage-router.py --route <node> <node> ...")


def print_detail(graph, start_id, budget=100):
    routes = enumerate_routes(graph, start_id, budget=budget)
    routes = dedup(routes)
    src = graph[start_id].label
    print(f"\n{'='*90}")
    print(f"🕸  ВСЕ МАРШРУТЫ: {src} (бюджет ${budget})")
    print(f"{'='*90}")

    if not routes:
        print("  ❌ Нет маршрутов")
        return

    for i, r in enumerate(routes[:8]):
        print(f"\n  #{i+1} ROI {r.roi_pct:+.1f}% | Доход ${r.total_revenue:.2f} | Комис ${r.fees_total:.2f} | "
              f"Чист ${r.net_profit:.2f} | Время {r.time_total}мин")
        print(f"      {' → '.join(r.node_labels)}")
        for d in r.details:
            print(f"      {d}")
        print()


def simulate_path(graph, path_ids, budget=100):
    for p in path_ids:
        if p not in graph:
            print(f"❌ Неизвестный узел: {p}")
            print(f"  Доступные: {list(graph.keys())}")
            return
    r = calc_route(graph, path_ids, budget)
    if not r:
        print("❌ Не удалось рассчитать")
        return
    print(f"\n{'='*90}")
    print(f"📋  СИМУЛЯЦИЯ: {' → '.join(r.node_labels)}")
    print(f"{'='*90}")
    print(f"  Бюджет на трафик: ${budget}")
    for d in r.details:
        print(f"  {d}")
    print(f"\n  {'─'*50}")
    print(f"  📊 ИТОГО:")
    print(f"     Посетителей:      {r.visitors_total}")
    if r.cpa_actions:
        print(f"     CPA действий:      {r.cpa_actions}")
    print(f"     Доход CPA:       ${r.cpa_revenue:.2f}")
    if r.referral_revenue:
        print(f"     Реферальный доход: ${r.referral_revenue:.2f}")
    if r.p2p_profit:
        print(f"     P2P арбитраж:     ${r.p2p_profit:.2f}")
    print(f"     Комиссии:        ${r.fees_total:.2f}")
    print(f"     Полный доход:    ${r.total_revenue:.2f}")
    print(f"     Затраты:         ${r.total_cost:.2f}")
    print(f"     ЧИСТАЯ ПРИБЫЛЬ:  ${r.net_profit:.2f}")
    print(f"     ROI:             {r.roi_pct:+.1f}%")
    print(f"     Время до вывода: {r.time_total}мин")
    print(f"  {'─'*50}")


# ============== CLI ==============

def main():
    graph = build()

    budget = 100
    if "--budget" in sys.argv:
        idx = sys.argv.index("--budget")
        budget = float(sys.argv[idx+1])

    if "--all" in sys.argv:
        print_all(graph, budget)
        return

    if "--from" in sys.argv:
        idx = sys.argv.index("--from")
        src = sys.argv[idx+1]
        if src not in graph:
            print(f"❌ Неизвестный источник: {src}")
            return
        print_detail(graph, src, budget)
        return

    if "--route" in sys.argv:
        idx = sys.argv.index("--route")
        path = sys.argv[idx+1:]
        simulate_path(graph, path, budget)
        return

    # По умолчанию: все
    print_all(graph, budget)


if __name__ == "__main__":
    main()
