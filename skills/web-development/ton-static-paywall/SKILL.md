---
name: ton-static-paywall
description: Add TON Connect paywall to static HTML — for demos/education only. NOT for commercial payments (no server-side verification possible)
version: "1.1"
tags: [ton, web3, paywall, ton-connect, static-site, demo-only, education, content-locking]
---

# TON Static Paywall

> ⚠️ **CRITICAL: Static hosting is NOT for commercial payments.**
>
> GitHub Pages (and all pure static hosts) **cannot verify transactions server-side**. Anyone with DevTools can edit the JS and bypass the paywall in 10 seconds. Client-side-only payment verification is **not real** — it's a visual lock, not a security boundary.
>
> **When this pattern is OK:**
> - Demos, prototypes, proof-of-concepts
> - Educational content (honour-system lock)
> - Portfolio pieces showing TON Connect integration
>
> **When NOT to use this pattern:**
> - Any product where a bypass costs real money
> - Commercial payments of any size
> - Anything you'd be embarrassed to explain to a paying customer who got blocked
>
> **For real payment products** → see [Backend Alternatives](#backend-alternatives) at the end of this skill.

## When to Use (Honestly)

- Demos and prototypes of content-locking mechanics
- Educational content (tutorials, guides on honour system)
- Portfolio pieces demonstrating TON Connect integration
- Internal tools where users are trusted
- Learning/practising TON Connect integration without server costs

## When NOT to Use

- **Real commercial products** — static paywalls are trivially bypassable
- **Paid content you actually need to monetise** — a bypass costs you revenue
- **Any situation requiring server-side verification** — no backend = no verification
- **Products for paying customers** — unprofessional, damages trust

## Architecture

```
Static HTML page (GitHub Pages / Vercel / Netlify)
  ├── tonconnect-manifest.json  ← wallet reads app metadata
  ├── icon-180.png              ← shown in wallet connect modal
  └── index.html                ← all logic in one file
        ├── @tonconnect/ui via CDN  ← connects any TON wallet
        ├── TonConnectUI.sendTransaction()  ← user pays
        └── localStorage              ← remembers payment
```

No backend, no database, no server-side verification. Payment 'verification' is client-side only — the wallet returns a signed `boc` that the page trusts blindly. This is the fundamental limitation of the static approach.

## Setup

### 1. Create the Manifest

`tonconnect-manifest.json` — must be publicly accessible:

```json
{
  "url": "https://your-domain.com/app",
  "name": "Your App Name",
  "iconUrl": "https://your-domain.com/app/icon-180.png",
  "termsOfUseUrl": "https://your-domain.com/app/",
  "privacyPolicyUrl": "https://your-domain.com/app/"
}
```

### 2. Create a 180×180 PNG Icon

Generate a minimal icon with Python:

```python
import struct, zlib, os

def make_png(w, h, r, g, b, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    def chunk(t, d):
        c = t + d
        return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
    raw = b''
    for y in range(h):
        raw += b'\x00' + bytes([r,g,b]) * w
    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)))
        f.write(chunk(b'IDAT', zlib.compress(raw)))
        f.write(chunk(b'IEND', b''))
```

### 3. Import TON Connect in HTML

Use the UI kit (NOT the raw SDK — the UI kit provides wallet selection modal, connect button, error handling):

```html
<script type="module">
import { TonConnectUI } from 'https://cdn.jsdelivr.net/npm/@tonconnect/ui@3.0.0/+esm';

const tonConnectUI = new TonConnectUI({
  manifestUrl: 'https://your-domain.com/app/tonconnect-manifest.json',
  buttonRootId: 'tc-button',  // <div> where the connect button renders
  uiPreferences: { theme: 'DARK' },
});
</script>
```

### 4. Listen for Wallet Changes

```javascript
tonConnectUI.onStatusChange(wallet => {
  if (wallet) {
    // Wallet connected — show pay button
  } else {
    // Disconnected — show connect button
  }
});
```

### 5. Send Transaction

```javascript
const result = await tonConnectUI.sendTransaction({
  validUntil: Math.floor(Date.now() / 1000) + 600,  // 10 min expiry
  network: '-239',  // mainnet; use '-3' for testnet
  messages: [{
    address: 'UQ...your-wallet-address...',
    amount: '1000000000',  // 1 TON = 1,000,000,000 nanograms
  }],
});
// result.boc contains the signed external message
```

### 6. Persist Unlock

```javascript
localStorage.setItem('app_unlocked', 'true');
```

Check on page load:
```javascript
if (localStorage.getItem('app_unlocked') === 'true') {
  document.getElementById('content').classList.add('unlocked');
}
```

## UX Pattern

The standard content-locking flow:

1. **Preview (blurred)** — show a blurred preview of the content with a lock overlay
2. **Connect** — user connects TON wallet via TON Connect modal
3. **Pay** — clear price display + pay button
4. **Unlock** — on successful transaction, remove blur + overlay + show full content
5. **Remember** — localStorage keeps them unlocked on return visits

```html
<div class="content-area" id="contentArea">
  <div class="preview" id="contentPreview">[blurred content]</div>
  <div class="overlay" id="contentOverlay">
    <div>🔒 Pay 1 TON to unlock</div>
    <button id="connectBtn">Connect Wallet</button>
  </div>
</div>
```

## Price Display

Always show:
- Price in TON **and** approximate USD (e.g., "1 TON ≈ $2")
- What the user gets (lifetime access, updates, support)
- Trust signals (no KYC, instant access, money-back guarantee if applicable)

## Content Structure (the locked product)

The locked content should be genuinely valuable. Examples:
- **Guide**: 5 strategies, each with step-by-step instructions, code snippets, links
- **Template**: boilerplate code the user can copy and modify
- **Tool**: a working mini-app or calculator

## Deploy

Host the manifest, icon, and HTML together. GitHub Pages / Vercel / Netlify all work for demos. For real products, see Backend Alternatives above.

GitHub Pages:
```bash
# Files in repo/docs/app/ (if Pages serves from /docs)
git add docs/app/
git commit -m "app: add TON paywall page"
git push
# Live at: https://user.github.io/repo/app/
```

## Backend Alternatives

For real payment products, use one of:

- **Python/Flask + TON SDK** — server-side transaction verification via toncenter.com API. Check `getTransactions()` for incoming payments.
- **Node.js + Express + @tonconnect/sdk** — same logic, JS ecosystem.
- **Cloudflare Workers + TON API** — edge function verifies payment before serving content (V8 isolates, 100K req/day free).
- **Dedicated payment service** — OpenNode, Coinbase Commerce, NowPayments. They handle the full flow.

The key difference: server-side verification queries the blockchain directly instead of trusting the client's wallet response.

## Pitfalls

| Pitfall | Fix |
|---------|------|
| Manifest 404 or CORS | Manifest must be at a public URL the wallet can fetch. Test with `curl` before connecting. |
| `import` fails in browser | Use `@tonconnect/ui` NOT `@tonconnect/sdk`. UI kit has CDN bundle; SDK is headless and harder to load. |
| Transaction rejected silently | Check `catch (e)` for `rejected` or `timeout` messages. Show user-friendly error text. |
| Wrong network | Test with `network: '-3'` (testnet) first. Mainnet = `'-239'`. Wrong network = silent failure. |
| Burn address as recipient | The example address `UQAAAA...JKZ` is a burn address. User must replace with their real TON address. |
| Wallet not installed | Fallback message: "Install Tonkeeper or open this page in Tonkeeper in-app browser." |
| localStorage cleared | User clears cache → content is locked again. They must pay again. Document this limitation. |
| **Client-side bypass** | **This is NOT a security boundary.** Anyone can edit the JS in DevTools to remove the lock. Only use for honour-system or demo content. |
| GitHub Pages for payments | GitHub Pages (and all static hosts) cannot verify payments server-side. This looks unprofessional for a paid product. Use a backend instead. |
| Windows CRLF in git | `git config core.autocrlf true` — warnings are cosmetic, files work. |
| `buttonRootId` after disconnect | TON Connect UI removes its button DOM on disconnect. Re-assign `buttonRootId` to re-render. |
| TWA return URL | For Telegram Mini Apps, set `actionsConfiguration.twaReturnUrl` in constructor. |

## CDN URLs (verified working)

| Package | URL |
|---------|-----|
| `@tonconnect/ui` v3 | `https://cdn.jsdelivr.net/npm/@tonconnect/ui@3.0.0/+esm` |
| `@tonconnect/sdk` v4 | `https://cdn.jsdelivr.net/npm/@tonconnect/sdk@4.0.0/+esm` |

Always verify CDN URLs with `curl -s -o /dev/null -w "%{http_code}" <url>` before shipping.

## Related

- `github-pages-deploy` — deploy the static files
- `content-pipeline` — generate the locked content
