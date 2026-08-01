# Gumroad Payout Audit — 2026-07-24

## Задача
Проверить, можно ли получать деньги с Gumroad из Крыма.

## Метод проверки
- Официальные страницы Gumroad Help Center
- OFAC sanctioned countries list
- PayPal/Stripe policies
- Blog summaries vs official docs (user correction: не вершки, а корешки)

## Результат

### Gumroad payout methods
| Метод | Статус для Крыма | Причина |
|-------|------------------|---------|
| Direct bank transfer (Stripe) | ❌ | Stripe не работает в sanctioned regions |
| PayPal | ❌ | PayPal приостановлен в РФ с 2022 |
| Payoneer | ❌ | Gumroad не поддерживает как payout |
| Wise | ❌ | Gumroad не поддерживает |

### Регистрационные требования
- Full legal name (как в паспорте) ✅
- Address verification ❓ (нужен адрес не в Крыму)
- W-8BEN form (освобождение от 24% налога США)
- Government ID scan (паспорт)
- Bank/PayPal account для вывода → упирается в санкции

### Вывод
Gumroad как платформа НЕ ПОДХОДИТ для Крыма из-за санкционных ограничений Stripe и PayPal.

### Рабочие альтернативы для вывода
1. USDT → KuCoin P2P → T-Банк (работает, 0.1-1%)
2. USDT → BestChange → RUB (работает, 3-5%)
3. Whop (3%) — проверить регистрацию для РФ
4. Самостоятельный приём USDT (свой лендинг, 0% комиссии платформы)

### Что нужно для любого проекта (правило)
1. ✅ Проверить вывод средств (payout)
2. ✅ Проверить пополнение (deposit)
3. ✅ Проверить регистрацию (KYC/docs)
4. ✅ Проверить санкционный статус
5. ✅ Найти workaround если прямые методы не работают
