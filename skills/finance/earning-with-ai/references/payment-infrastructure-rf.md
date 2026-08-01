# Payment Infrastructure for RF/Crimea

## Recommended Setup (Start)

### 1. Sberbank Card (Direct Transfers)
- No commission for person-to-person
- Instant transfers
- Good for: initial clients, trust building

### 2. ЮMoney (Online Payments)
- Register: yoomoney.ru
- Commission: 0.5-3%
- Features: invoicing, API for bots
- Good for: online payments, automation

## Advanced Setup (Growth)

### 3. Robokassa (Payment Gateway)
- All payment methods (cards, e-wallets, SBP)
- Auto-receipts (54-FZ compliant)
- API for Telegram bots
- Commission: 2-5%
- Register: robokassa.ru

### 4. Sberbank Acquiring
- All cards accepted
- High trust
- Commission: 2-3%
- Requires: IP or LLC registration

### 5. Bybit P2P (Crypto)
- No limits
- International payments
- How: RUB → USDT → withdraw to card
- Commission: 0-1%
- Register: bybit.com

## IP Registration Guide

### Documents Needed
1. Passport
2. INN (tax number)
3. Application form P21001
4. State duty payment (800 RUB)

### OKVED Codes (IT Services)
- 62.01 — Software development
- 62.02 — Software consulting
- 62.09 — IT services
- 63.11 — Data processing

### How to Register
1. Go to nalog.ru
2. Fill application P21001
3. Pay 800 RUB duty
4. Submit documents (online or in person)
5. Receive OGRNIP in 3 business days

### Tax Options
- **Self-employed** (npd.nalog.ru): 4% individuals, 6% legal
  - Limit: 2.4M RUB/year
  - Simple, but can't hire
- **IP with USN**: 6% of revenue
  - Can hire employees
  - More opportunities
  - Quarterly reporting

## Invoice Template

```
INVOICE #___ from ___.___.2026

Provider:
IP Full Name
INN: XXXXXXXXXXXX
OGRNIP: XXXXXXXXXXXXXXXXX
Account: XXXXXXXXXXXXXXXXXXXXXX
Bank: Sberbank
BIK: 044525225

Client:
Company Name
INN: XXXXXXXXXX
Account: XXXXXXXXXXXXXXXXXXXXXX

| # | Service | Qty | Price | Total |
|---|---------|-----|-------|-------|
| 1 | AI Bot | 1 | 25000 | 25000 |
| 2 | Integration | 1 | 5000 | 5000 |
| 3 | Training | 1 | 3000 | 3000 |
|   | TOTAL: |   |       | 33000 |

Total: 33,000 (Thirty-three thousand) RUB
Tax: Not applicable (USN)

Payment due: 3 business days

IP Full Name
Signature / Full Name /
```

## Auto-Invoice Generation

```python
import sqlite3
from datetime import datetime, timedelta

def create_invoice(client_id, service, price, db_path="crm.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("SELECT hotel_name, contact_name, email FROM clients WHERE id = ?", 
              (client_id,))
    client = c.fetchone()
    
    invoice = f"""
INVOICE from {datetime.now().strftime('%d.%m.%Y')}

Provider: IP Full Name
Client: {client[0]}
Contact: {client[1]}

Service: {service}
Amount: {price} RUB
Due: {(datetime.now() + timedelta(days=3)).strftime('%d.%m.%Y')}

Bank details:
Account: XXXXXXXXXXXXXXXXXXXXXX
Bank: Sberbank
BIK: 044525225
"""
    conn.close()
    return invoice
```

## Risk Mitigation

| Risk | Solution |
|------|----------|
| Card blocking | Use ЮMoney/crypto backup |
| Tax issues | Register as self-employed first |
| Sanctions | VPN + crypto for international |
| Client non-payment | 50% advance required |

## Files
- Payment guide: `data/plans/payment_guide.md`
- Contract template: `data/plans/contract_template.md`
