# Content Vault — Reference Implementation

**Status: DELETED** — removed from repo on 2026-07-14. User rejected the approach.

## Why It Was Rejected

The user's exact feedback:
> "GitHub Pages не для коммерческих платежей. TON Connect без бэкенда — несерьёзно, нельзя проверить платёж. Выглядит непрофессионально для продукта за деньги."

Translated: GitHub Pages is not for commercial payments. TON Connect without backend is unprofessional — payment can't be verified. Looks unprofessional for a paid product.

## Key Lessons

1. **Static hosting (GitHub Pages) cannot verify payments server-side.** A user with DevTools can bypass the paywall in seconds.
2. **Client-side-only payment verification is not real.** The wallet's signed `boc` is returned to the page, but the page has no way to verify it against a server-side source of truth.
3. **For real payment products:** use a backend (Python/Flask, Node.js) or a dedicated payment service (OpenNode, Coinbase Commerce).
4. **Static paywalls are OK for:** demos, prototypes, honour-system educational content. NOT for anything where a bypass costs real money.

## Original Implementation Details (archived)

The page was deployed at `https://mcduck-s8.github.io/hermes-salon-landing/content-vault/` and deleted via commit `e1f24413f`.

### Architecture (for reference)

- Single HTML file with all CSS/JS inlined
- `@tonconnect/ui` v3 via CDN (`cdn.jsdelivr.net/npm/@tonconnect/ui@3.0.0/+esm`)
- Wallet selection modal, connect/disconnect, and transaction flow
- localStorage persistence for "already unlocked"
- Content: 5 guide chapters about TON earning strategies

### File Structure

| File | Purpose |
|------|---------|
| `index.html` | Complete single-file app: HTML + CSS + JS |
| `tonconnect-manifest.json` | TON Connect app metadata |
| `icon-180.png` | Wallet modal icon (generated via Python struct+zlib) |

### State Machine

```
disconnected → connect wallet → connected (unpaid) → send tx → paying → confirmed → unlocked
                                                                     ↓ failed → connected (error shown)
```

### CDN URLs (verified working)

| Package | URL |
|---------|-----|
| `@tonconnect/ui` v3 | `https://cdn.jsdelivr.net/npm/@tonconnect/ui@3.0.0/+esm` |
| `@tonconnect/sdk` v4 | `https://cdn.jsdelivr.net/npm/@tonconnect/sdk@4.0.0/+esm` |

### Pitfalls Encountered

| Issue | Fix |
|-------|------|
| First attempt used raw `@tonconnect/sdk` | Switched to `@tonconnect/ui` which has built-in UI components |
| No price on first version | Added prominent price card with TON + USD |
| No content preview | Added blurred preview with lock overlay before payment |
| `buttonRootId` not re-rendering after disconnect | Re-assign `buttonRootId` in the disconnect handler |
| **Static approach rejected** | **Don't use static hosting for payment products — use a backend.** |
