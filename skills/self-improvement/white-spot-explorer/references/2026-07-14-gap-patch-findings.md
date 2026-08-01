# Gap-Patch Session 2026-07-14 — Verified Findings

## Closed White Spots

### 1. @wallet (Telegram) KYC
- **Source:** help.wallet.tg official — Identity Verification articles
- **Verification:** official_docs, confidence 1.0
- **Findings:**
  - Basic level (name, DOB, phone) mandatory for ALL users
  - Extended level: identity document + liveness check
  - Advanced level: document + proof of address + liveness
  - External withdrawal to Tonkeeper works at Basic level
- **Implication:** @wallet is custodial KYC, but TON → @wallet → Tonkeeper is viable

### 2. KuCoin P2P + Russia Crypto Regulation 2026
- **Sources:** KuCoin blog, help.wallet.tg, tradersunion.com, coinspot.io
- **Verification:** cross_referenced, confidence 1.0
- **Findings:**
  - P2P with Sber/Tinkoff banned since Aug 2023
  - **Russia legalized crypto July 1, 2026** — crypto = financial asset
  - Only licensed exchanges allowed, KYC/AML mandatory
  - Non-qualified investors: 300K RUB/yr cap
  - Foreign exchanges (KuCoin, Bybit) may be blocked
  - User existing method: Crypto → USDT (TRC20) → KuCoin P2P → T-Bank

### 3. Publish0x
- **Source:** direct browser check
- **Verification:** direct_check, confidence 0.95
- **Findings:** BLOCKED by Cloudflare. Returns 403. Not accessible without VPN/proxy.

### 4. USDT Withdrawal Pathways (Crimea)
- **Sources:** Multiple (Whitebird, Bybit, Tonkeeper, KuCoin)
- **Verification:** cross_referenced, confidence 0.95
- **4 verified pathways:**
  1. KuCoin P2P → T-Bank (existing, faces regulatory risk)
  2. Whitebird (Belarusian): USDT→RUB→MIR/VISA CIS card, $12K/tx, 5-6% fee, full KYC required
  3. Tonkeeper → Bybit: TON→CEX→card, KYC required
  4. @wallet Basic → Tonkeeper: TON to self-custody without extra KYC
- **Key insight:** All CEX→fiat paths require KYC. Only P2P/cash avoids KYC.

### 5. MEXC KYC (Deferred — requires VPN)
- **Status:** UNVERIFIED
- **Blocked by:** 403 from current network
- **Task created:** `knowledge/okf/deferred-tasks/mexc-kyc-vpn.md`
- **Requires:** VPN access to verify directly

## CPA Records Rejected (56 total)
- Lowest confidence to 0.3, tagged #rejected-by-user
- Includes: CPAGrip, OGAds, AdCombo, cityads, maxbounty, CPA conventions, CPA research, Content-Locking-CPA

## 105 White Spots Classification
- **knowledge domains (47):** Need user to confirm interest
- **session dumps (41):** Technical, no action needed
- **auto-seeded concepts (11):** Garbage, delete pending confirmation
- **skill-domain mappings (5):** Raise confidence to 1.0
- **human domain analysis (1):** Need user input

## SQLite Workarounds
- Tags column has malformed JSON (`..., auto_tagged, auto_tagged`)
- Fix: `substr(tags, 1, instr(tags, '],') + 1)` before json_set
- Two DBs: `~/.hermes/cache/` (small, 14 cols) vs `D:/Portable_Soft/hermes/cache/` (large, 22 tables, 18 cols)
