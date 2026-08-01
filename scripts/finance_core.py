#!/usr/bin/env python3
"""
Finance Core — Бухгалтер автономного арбитража.
Единый модуль: P&L, Cash Flow, Unit Economics, Tax Ledger, Withdrawal Tracker.
Интегрируется с Knowledge Cube, autonomous_agent, arbitrage-execution.
"""

import sqlite3
import json
from datetime import datetime, date, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from enum import Enum

HERMES_HOME = Path("D:/Portable_Soft/hermes")
DB_PATH = HERMES_HOME / "cache" / "finance_core.db"
EXCEL_EXPORT_DIR = HERMES_HOME / "outputs" / "finance"

class EventType(Enum):
    SPEND = "spend"                    # трафик, инструменты, инфраструктура
    REVENUE = "revenue"                # CPA, affiliate, own products
    WITHDRAWAL = "withdrawal"          # запрос вывода из сети
    WITHDRAWAL_RECEIVED = "withdrawal_received"  # деньги на карте
    TAX_ACCRUAL = "tax_accrual"        # начисление налога
    TAX_PAID = "tax_paid"              # уплата налога
    REFUND = "refund"                  # возврат/чарджбэк
    FEE = "fee"                        # комиссии (сеть, вывод, API)

class CostCenter(Enum):
    TRAFFIC = "traffic"                # покупка трафика
    TOOLS = "tools"                    # API, прокси, софт
    INFRASTRUCTURE = "infrastructure"  # серверы, домены, хостинг
    OUTSOURCE = "outsource"            # фрилансеры, аутсорс
    CONTENT = "content"                # генерация контента
    OTHER = "other"

class RevenueStream(Enum):
    CPA_NETWORK = "cpa_network"        # Admitad, CPAGrip, MaxBounty...
    AFFILIATE = "affiliate"            # Amazon, iHerb, Booking...
    OWN_PRODUCT = "own_product"        # боты, курсы, шаблоны
    TRAFFIC_SALE = "traffic_sale"      # продажа постов/каналов/сайтов
    OTHER = "other"

@dataclass
class FinanceEvent:
    id: Optional[int] = None
    ts: str = ""
    event_type: str = ""
    amount_usd: float = 0.0
    amount_rub: float = 0.0
    usd_rate: float = 0.0
    cost_center: str = ""
    revenue_stream: str = ""
    scheme_name: str = ""
    network: str = ""
    offer_name: str = ""
    utm_source: str = ""
    utm_medium: str = ""
    utm_campaign: str = ""
    utm_content: str = ""
    click_id: str = ""
    withdrawal_method: str = ""
    fee_usd: float = 0.0
    status: str = "pending"  # pending, confirmed, failed, cancelled
    tax_accrued_usd: float = 0.0
    notes: str = ""
    source: str = "manual"  # manual, auto_poster, arbitrage_execution, cpa_webhook

    def __post_init__(self):
        if not self.ts:
            self.ts = datetime.now().isoformat()

class FinanceCore:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        EXCEL_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._load_usd_rate()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS finance_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    amount_usd REAL NOT NULL,
                    amount_rub REAL NOT NULL,
                    usd_rate REAL NOT NULL,
                    cost_center TEXT,
                    revenue_stream TEXT,
                    scheme_name TEXT,
                    network TEXT,
                    offer_name TEXT,
                    utm_source TEXT,
                    utm_medium TEXT,
                    utm_campaign TEXT,
                    utm_content TEXT,
                    click_id TEXT,
                    withdrawal_method TEXT,
                    fee_usd REAL DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    tax_accrued_usd REAL DEFAULT 0,
                    notes TEXT,
                    source TEXT DEFAULT 'manual',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_finance_ts ON finance_events(ts);
                CREATE INDEX IF NOT EXISTS idx_finance_type ON finance_events(event_type);
                CREATE INDEX IF NOT EXISTS idx_finance_scheme ON finance_events(scheme_name);
                CREATE INDEX IF NOT EXISTS idx_finance_network ON finance_events(network);
                CREATE INDEX IF NOT EXISTS idx_finance_status ON finance_events(status);
                
                CREATE TABLE IF NOT EXISTS usd_rates (
                    date TEXT PRIMARY KEY,
                    rate REAL NOT NULL,
                    source TEXT DEFAULT 'cbr'
                );
                
                CREATE TABLE IF NOT EXISTS tax_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                
                CREATE TABLE IF NOT EXISTS scheme_unit_economics (
                    scheme_name TEXT PRIMARY KEY,
                    total_spend_usd REAL DEFAULT 0,
                    total_revenue_usd REAL DEFAULT 0,
                    total_leads INTEGER DEFAULT 0,
                    total_conversions INTEGER DEFAULT 0,
                    cpc_usd REAL DEFAULT 0,
                    ctr REAL DEFAULT 0,
                    cr REAL DEFAULT 0,
                    epc_usd REAL DEFAULT 0,
                    roi_pct REAL DEFAULT 0,
                    payback_days REAL DEFAULT 0,
                    status TEXT DEFAULT 'testing',
                    last_calculated TEXT
                );
            """)
            conn.commit()

    def _load_usd_rate(self):
        with sqlite3.connect(self.db_path) as conn:
            today = date.today().isoformat()
            row = conn.execute("SELECT rate FROM usd_rates WHERE date=?", (today,)).fetchone()
            if row:
                self.usd_rate = row[0]
            else:
                self.usd_rate = 95.0  # fallback
                self.update_usd_rate(self.usd_rate, "fallback")

    def update_usd_rate(self, rate: float, source: str = "manual"):
        self.usd_rate = rate
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO usd_rates (date, rate, source) VALUES (?, ?, ?)",
                (date.today().isoformat(), rate, source)
            )
            conn.commit()

    def add_event(self, event: FinanceEvent) -> int:
        if event.amount_rub == 0 and event.amount_usd != 0:
            event.amount_rub = round(event.amount_usd * self.usd_rate, 2)
        elif event.amount_usd == 0 and event.amount_rub != 0:
            event.amount_usd = round(event.amount_rub / self.usd_rate, 2)

        # Auto-calculate tax for revenue (4% samozanyatiy default)
        if event.event_type == EventType.REVENUE.value and event.tax_accrued_usd == 0:
            event.tax_accrued_usd = round(event.amount_usd * 0.04, 2)

        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("""
                INSERT INTO finance_events (
                    ts, event_type, amount_usd, amount_rub, usd_rate,
                    cost_center, revenue_stream, scheme_name, network, offer_name,
                    utm_source, utm_medium, utm_campaign, utm_content, click_id,
                    withdrawal_method, fee_usd, status, tax_accrued_usd, notes, source
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.ts, event.event_type, event.amount_usd, event.amount_rub, event.usd_rate,
                event.cost_center, event.revenue_stream, event.scheme_name, event.network, event.offer_name,
                event.utm_source, event.utm_medium, event.utm_campaign, event.utm_content, event.click_id,
                event.withdrawal_method, event.fee_usd, event.status, event.tax_accrued_usd, event.notes, event.source
            ))
            conn.commit()
            event_id = cur.lastrowid

        # Update scheme unit economics
        if event.scheme_name:
            self._recalc_scheme_economics(event.scheme_name)

        return event_id

    def _recalc_scheme_economics(self, scheme_name: str):
        with sqlite3.connect(self.db_path) as conn:
            # Spend
            spend_row = conn.execute("""
                SELECT COALESCE(SUM(amount_usd), 0), COALESCE(SUM(fee_usd), 0)
                FROM finance_events
                WHERE scheme_name = ? AND event_type IN ('spend', 'fee')
            """, (scheme_name,)).fetchone()
            total_spend = spend_row[0] + spend_row[1]

            # Revenue
            rev_row = conn.execute("""
                SELECT COALESCE(SUM(amount_usd), 0), COUNT(*)
                FROM finance_events
                WHERE scheme_name = ? AND event_type = 'revenue'
            """, (scheme_name,)).fetchone()
            total_revenue = rev_row[0]
            total_leads = rev_row[1]

            # Conversions (withdrawal_received)
            conv_row = conn.execute("""
                SELECT COALESCE(SUM(amount_usd), 0), COUNT(*)
                FROM finance_events
                WHERE scheme_name = ? AND event_type = 'withdrawal_received'
            """, (scheme_name,)).fetchone()
            total_conversions = conv_row[1]

            # Clicks (from spend events with click tracking)
            clicks_row = conn.execute("""
                SELECT COUNT(*) FROM finance_events
                WHERE scheme_name = ? AND event_type = 'spend' AND click_id != ''
            """, (scheme_name,)).fetchone()
            total_clicks = clicks_row[0]

            # Calculate metrics
            cpc = total_spend / total_clicks if total_clicks > 0 else 0
            ctr = 0  # Need impressions for this
            cr = total_conversions / total_clicks if total_clicks > 0 else 0
            epc = total_revenue / total_clicks if total_clicks > 0 else 0
            if total_spend > 0:
                roi = ((total_revenue - total_spend) / total_spend * 100)
            elif total_revenue > 0:
                roi = 9999  # Infinite ROI when spend is 0 but revenue exists
            else:
                roi = 0
            payback = total_spend / (total_revenue / 30) if total_revenue > 0 else 0  # rough daily

            # Determine status
            if total_revenue == 0:
                status = "testing"
            elif roi > 100:
                status = "scaling"
            elif roi > 0:
                status = "profitable"
            else:
                status = "unprofitable"

            conn.execute("""
                INSERT OR REPLACE INTO scheme_unit_economics (
                    scheme_name, total_spend_usd, total_revenue_usd, total_leads,
                    total_conversions, cpc_usd, ctr, cr, epc_usd, roi_pct,
                    payback_days, status, last_calculated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scheme_name, total_spend, total_revenue, total_leads,
                total_conversions, cpc, ctr, cr, epc, roi,
                payback, status, datetime.now().isoformat()
            ))
            conn.commit()

    def get_pnl(self, days: int = 30) -> Dict[str, Any]:
        since = (datetime.now() - timedelta(days=days)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT event_type, cost_center, revenue_stream, scheme_name,
                       SUM(amount_usd) as total_usd, COUNT(*) as count
                FROM finance_events
                WHERE ts >= ?
                GROUP BY event_type, cost_center, revenue_stream, scheme_name
            """, (since,)).fetchall()

        pnl = {
            "period_days": days,
            "revenue": {"total_usd": 0, "by_stream": {}, "by_scheme": {}},
            "spend": {"total_usd": 0, "by_center": {}, "by_scheme": {}},
            "fees": {"total_usd": 0},
            "tax_accrued": {"total_usd": 0},
            "net_usd": 0,
            "net_rub": 0,
        }

        for r in rows:
            et = r["event_type"]
            amt = r["total_usd"]
            scheme = r["scheme_name"] or "unknown"
            center = r["cost_center"] or "unknown"
            stream = r["revenue_stream"] or "unknown"

            if et == "revenue":
                pnl["revenue"]["total_usd"] += amt
                pnl["revenue"]["by_stream"][stream] = pnl["revenue"]["by_stream"].get(stream, 0) + amt
                pnl["revenue"]["by_scheme"][scheme] = pnl["revenue"]["by_scheme"].get(scheme, 0) + amt
            elif et in ("spend", "fee"):
                pnl["spend"]["total_usd"] += amt
                if et == "fee":
                    pnl["fees"]["total_usd"] += amt
                else:
                    pnl["spend"]["by_center"][center] = pnl["spend"]["by_center"].get(center, 0) + amt
                pnl["spend"]["by_scheme"][scheme] = pnl["spend"]["by_scheme"].get(scheme, 0) + amt
            elif et == "tax_accrual":
                pnl["tax_accrued"]["total_usd"] += amt

        pnl["net_usd"] = pnl["revenue"]["total_usd"] - pnl["spend"]["total_usd"] - pnl["fees"]["total_usd"]
        pnl["net_rub"] = round(pnl["net_usd"] * self.usd_rate, 2)
        return pnl

    def get_cashflow(self, days: int = 30) -> List[Dict]:
        since = (datetime.now() - timedelta(days=days)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT ts, event_type, amount_usd, amount_rub, scheme_name, network, status, notes
                FROM finance_events
                WHERE ts >= ? AND event_type IN ('spend', 'revenue', 'withdrawal', 'withdrawal_received', 'tax_paid')
                ORDER BY ts
            """, (since,)).fetchall()
        return [dict(r) for r in rows]

    def get_scheme_economics(self, scheme_name: str = None) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if scheme_name:
                rows = conn.execute("SELECT * FROM scheme_unit_economics WHERE scheme_name = ?", (scheme_name,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM scheme_unit_economics ORDER BY roi_pct DESC").fetchall()
        return [dict(r) for r in rows]

    def get_pending_withdrawals(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM finance_events
                WHERE event_type IN ('withdrawal', 'withdrawal_received') AND status != 'cancelled'
                ORDER BY ts
            """).fetchall()
        return [dict(r) for r in rows]

    def get_tax_liability(self) -> Dict[str, float]:
        with sqlite3.connect(self.db_path) as conn:
            # Accrued but not paid
            accrued = conn.execute("""
                SELECT COALESCE(SUM(tax_accrued_usd), 0) FROM finance_events
                WHERE event_type = 'revenue'
            """).fetchone()[0]
            paid = conn.execute("""
                SELECT COALESCE(SUM(amount_usd), 0) FROM finance_events
                WHERE event_type = 'tax_paid'
            """).fetchone()[0]
        return {
            "accrued_usd": round(accrued, 2),
            "paid_usd": round(paid, 2),
            "pending_usd": round(accrued - paid, 2),
            "pending_rub": round((accrued - paid) * self.usd_rate, 2)
        }

    def export_excel(self, filepath: Path = None) -> Path:
        """Export P&L, Cash Flow, Unit Economics to Excel via excel-author pattern."""
        if not filepath:
            filepath = EXCEL_EXPORT_DIR / f"finance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            from openpyxl.utils import get_column_letter
        except ImportError:
            # Fallback: CSV
            csv_path = filepath.with_suffix(".csv")
            self._export_csv(csv_path)
            return csv_path

        wb = Workbook()

        # Styles
        header_font = Font(bold=True, color="FFFFFF", size=11)
        header_fill = PatternFill(start_color="1F6FEB", end_color="1F6FEB", fill_type="solid")
        money_format = '#,##0.00'
        pct_format = '0.00%'
        thin_border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )

        # Sheet 1: P&L Summary
        ws1 = wb.active
        ws1.title = "P&L Summary"
        pnl = self.get_pnl(30)

        ws1.append(["HERMES FINANCE REPORT", "", "", "", f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
        ws1.append(["Period: Last 30 days", "", "", "", f"USD/RUB Rate: {self.usd_rate}"])
        ws1.append([])

        # Revenue
        ws1.append(["REVENUE", "", "", "USD", "RUB"])
        for cell in ws1[ws1.max_row]:
            cell.font = header_font
            cell.fill = header_fill
        for stream, amt in pnl["revenue"]["by_stream"].items():
            ws1.append([f"  {stream}", "", "", amt, round(amt * self.usd_rate, 2)])
        ws1.append(["TOTAL REVENUE", "", "", pnl["revenue"]["total_usd"], round(pnl["revenue"]["total_usd"] * self.usd_rate, 2)])
        ws1.append([])

        # Spend
        ws1.append(["SPEND", "", "", "USD", "RUB"])
        for cell in ws1[ws1.max_row]:
            cell.font = header_font
            cell.fill = header_fill
        for center, amt in pnl["spend"]["by_center"].items():
            ws1.append([f"  {center}", "", "", amt, round(amt * self.usd_rate, 2)])
        ws1.append(["TOTAL SPEND", "", "", pnl["spend"]["total_usd"], round(pnl["spend"]["total_usd"] * self.usd_rate, 2)])
        ws1.append([])

        # Fees
        ws1.append(["FEES", "", "", pnl["fees"]["total_usd"], round(pnl["fees"]["total_usd"] * self.usd_rate, 2)])
        ws1.append([])

        # Net
        ws1.append(["NET PROFIT", "", "", pnl["net_usd"], pnl["net_rub"]])
        for cell in ws1[ws1.max_row]:
            cell.font = Font(bold=True, size=12, color="00FF00" if pnl["net_usd"] >= 0 else "FF0000")

        # Sheet 2: Cash Flow
        ws2 = wb.create_sheet("Cash Flow")
        ws2.append(["Date", "Type", "Scheme", "Network", "USD", "RUB", "Status", "Notes"])
        for cell in ws2[1]:
            cell.font = header_font
            cell.fill = header_fill
        for row in self.get_cashflow(30):
            ws2.append([
                row["ts"][:19], row["event_type"], row["scheme_name"] or "",
                row["network"] or "", row["amount_usd"], round(row["amount_rub"], 2),
                row["status"], row["notes"] or ""
            ])

        # Sheet 3: Unit Economics
        ws3 = wb.create_sheet("Unit Economics")
        ws3.append(["Scheme", "Spend $", "Revenue $", "Leads", "Conversions", "CPC $", "CR", "EPC $", "ROI %", "Payback Days", "Status"])
        for cell in ws3[1]:
            cell.font = header_font
            cell.fill = header_fill
        for row in self.get_scheme_economics():
            ws3.append([
                row["scheme_name"], row["total_spend_usd"], row["total_revenue_usd"],
                row["total_leads"], row["total_conversions"], row["cpc_usd"],
                row["cr"], row["epc_usd"], row["roi_pct"], row["payback_days"], row["status"]
            ])

        # Sheet 4: Tax Liability
        ws4 = wb.create_sheet("Tax Liability")
        tax = self.get_tax_liability()
        ws4.append(["Item", "USD", "RUB"])
        ws4.append(["Tax Accrued (4%)", tax["accrued_usd"], round(tax["accrued_usd"] * self.usd_rate, 2)])
        ws4.append(["Tax Paid", tax["paid_usd"], round(tax["paid_usd"] * self.usd_rate, 2)])
        ws4.append(["Tax Pending", tax["pending_usd"], tax["pending_rub"]])

        # Sheet 5: Pending Withdrawals
        ws5 = wb.create_sheet("Pending Withdrawals")
        ws5.append(["Date", "Scheme", "Network", "Method", "USD", "RUB", "Fee $", "Status", "Notes"])
        for cell in ws5[1]:
            cell.font = header_font
            cell.fill = header_fill
        for row in self.get_pending_withdrawals():
            ws5.append([
                row["ts"][:19], row["scheme_name"] or "", row["network"] or "",
                row["withdrawal_method"] or "", row["amount_usd"], row["amount_rub"],
                row["fee_usd"], row["status"], row["notes"] or ""
            ])

        # Auto-width columns
        for ws in wb.worksheets:
            for col in ws.columns:
                max_len = max(len(str(cell.value or "")) for cell in col)
                ws.column_dimensions[get_column_letter(col[0].column)].width = min(max_len + 4, 50)

        wb.save(filepath)
        return filepath

    def _export_csv(self, filepath: Path):
        import csv
        pnl = self.get_pnl(30)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Section", "Item", "USD", "RUB"])
            writer.writerow(["REVENUE", "TOTAL", pnl["revenue"]["total_usd"], round(pnl["revenue"]["total_usd"] * self.usd_rate, 2)])
            for k, v in pnl["revenue"]["by_stream"].items():
                writer.writerow(["REVENUE", k, v, round(v * self.usd_rate, 2)])
            writer.writerow(["SPEND", "TOTAL", pnl["spend"]["total_usd"], round(pnl["spend"]["total_usd"] * self.usd_rate, 2)])
            for k, v in pnl["spend"]["by_center"].items():
                writer.writerow(["SPEND", k, v, round(v * self.usd_rate, 2)])
            writer.writerow(["FEES", "TOTAL", pnl["fees"]["total_usd"], round(pnl["fees"]["total_usd"] * self.usd_rate, 2)])
            writer.writerow(["NET", "PROFIT", pnl["net_usd"], pnl["net_rub"]])

# Convenience functions for autonomous_agent integration
def log_spend(scheme: str, amount_usd: float, cost_center: str, network: str = "", notes: str = "", click_id: str = ""):
    fc = FinanceCore()
    return fc.add_event(FinanceEvent(
        event_type=EventType.SPEND.value,
        amount_usd=amount_usd,
        cost_center=cost_center,
        scheme_name=scheme,
        network=network,
        click_id=click_id,
        notes=notes,
        source="autonomous_agent"
    ))

def log_revenue(scheme: str, amount_usd: float, revenue_stream: str, network: str, offer: str = "", utm: dict = None):
    fc = FinanceCore()
    return fc.add_event(FinanceEvent(
        event_type=EventType.REVENUE.value,
        amount_usd=amount_usd,
        revenue_stream=revenue_stream,
        scheme_name=scheme,
        network=network,
        offer_name=offer,
        utm_source=utm.get("source", "") if utm else "",
        utm_medium=utm.get("medium", "") if utm else "",
        utm_campaign=utm.get("campaign", "") if utm else "",
        utm_content=utm.get("content", "") if utm else "",
        source="autonomous_agent"
    ))

def log_withdrawal_request(scheme: str, amount_usd: float, network: str, method: str, fee_usd: float = 0):
    fc = FinanceCore()
    return fc.add_event(FinanceEvent(
        event_type=EventType.WITHDRAWAL.value,
        amount_usd=amount_usd,
        scheme_name=scheme,
        network=network,
        withdrawal_method=method,
        fee_usd=fee_usd,
        status="pending",
        source="autonomous_agent"
    ))

def log_withdrawal_received(scheme: str, amount_usd: float, network: str, method: str, fee_usd: float = 0):
    fc = FinanceCore()
    return fc.add_event(FinanceEvent(
        event_type=EventType.WITHDRAWAL_RECEIVED.value,
        amount_usd=amount_usd,
        scheme_name=scheme,
        network=network,
        withdrawal_method=method,
        fee_usd=fee_usd,
        status="confirmed",
        source="autonomous_agent"
    ))

def get_finance_summary() -> Dict:
    fc = FinanceCore()
    return {
        "pnl_30d": fc.get_pnl(30),
        "schemes": fc.get_scheme_economics(),
        "tax": fc.get_tax_liability(),
        "pending_withdrawals": fc.get_pending_withdrawals(),
        "usd_rate": fc.usd_rate
    }

if __name__ == "__main__":
    import sys
    fc = FinanceCore()
    if len(sys.argv) < 2:
        print("Usage: finance_core.py <pnl|cashflow|schemes|tax|withdrawals|export|summary>")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "pnl":
        print(json.dumps(fc.get_pnl(30), indent=2, ensure_ascii=False))
    elif cmd == "cashflow":
        print(json.dumps(fc.get_cashflow(30), indent=2, ensure_ascii=False))
    elif cmd == "schemes":
        print(json.dumps(fc.get_scheme_economics(), indent=2, ensure_ascii=False))
    elif cmd == "tax":
        print(json.dumps(fc.get_tax_liability(), indent=2, ensure_ascii=False))
    elif cmd == "withdrawals":
        print(json.dumps(fc.get_pending_withdrawals(), indent=2, ensure_ascii=False))
    elif cmd == "export":
        path = fc.export_excel()
        print(f"Exported to: {path}")
    elif cmd == "summary":
        print(json.dumps(get_finance_summary(), indent=2, ensure_ascii=False))
    else:
        print(f"Unknown command: {cmd}")