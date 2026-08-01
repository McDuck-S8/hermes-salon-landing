---
name: free-static-hosting
description: Comprehensive database of free static site hosting services — comparison, limits, setup, and deploy commands for each platform.
version: "1.0"
tags: [static-site, hosting, free-tier, deployment, netlify, vercel, cloudflare-pages, github-pages]
---

# Free Static Site Hosting — Database & Skills

## Quick Comparison

| Platform | Free Tier Limits | Custom Domain | SSL | Builds/month | CI/CD | Notes |
|----------|----------------|---------------|-----|-------------|-------|-------|
| **GitHub Pages** | 1GB, 100GB/mo bandwidth, 500MB/file | ✅ (with CNAME) | ✅ Auto | Unlimited | Git push | Public repo only (free); 10 builds/h |
| **Cloudflare Pages** | Unlimited bandwidth, 500 builds/mo, 1 build concurrency | ✅ | ✅ Auto | 500 | Git deploy | Best free tier; 300+ edge PoPs |
| **Netlify** | 100GB bandwidth, 300 build min/mo | ✅ | ✅ Auto | 300 | Git deploy | Forms, Functions, Split testing |
| **Vercel** | 100GB bandwidth, 6000 build min/mo | ✅ | ✅ Auto | Unlimited | Git deploy | Great for Next.js; Serverless Functions |
| **Render** | 100GB bandwidth, static sites | ✅ | ✅ Auto | Unlimited | Git deploy | Also free PostgreSQL, Redis |
| **Surge** | Unlimited bandwidth; CLI-based | ✅ (CNAME) | ✅ Auto | N/A (CLI push) | CLI deploy | Simplest — `surge` command |
| **GitLab Pages** | Unlimited bandwidth (no stated soft limit) | ✅ (CNAME) | ✅ Auto | Unlimited | Git push | Private repos allowed; 400 build min/mo |
| **Firebase Hosting** | 10GB storage, 360MB/day bandwidth | ✅ | ✅ Auto | N/A | CLI deploy | Google Cloud ecosystem |
| **Puter** | Free subdomain puter.site, drag-and-drop | ❌ | ✅ Auto | N/A | Drag & drop | Easiest — no CLI needed |
| **Bunny.net** | 500MB storage, 5GB bandwidth/mo | ✅ (paid DNS) | ✅ | N/A | ZIP/API | Cheap paid; minimal free tier |

## Platform Details

### 1. GitHub Pages
- **URL**: https://pages.github.com
- **Deploy**: `git push` to `main` or `gh-pages` branch; sources from `/` or `/docs`
- **Domain**: `https://<user>.github.io/<repo>/`
- **Limits**: 1GB repo, 100GB/mo bandwidth, 10 builds/hour, 500MB per file
- **Forms**: ❌ No server-side
- **Setup**:
  ```bash
  # Push HTML to repo, then enable in Settings > Pages
  # OR via CLI:
  gh api repos/$OWNER/$REPO/pages --method POST \
    -f source[branch]=main \
    -f source[path]=/docs
  ```
- **Verdict**: ✅ Best for open-source projects, landing pages
- **Pitfalls**: ❗ Public repo only (free); ❗ Only `/` or `/docs` as source; ❗ No serverless functions

### 2. Cloudflare Pages
- **URL**: https://pages.cloudflare.com
- **Deploy**: Git repo or CLI (`wrangler pages deploy`)
- **Domain**: `https://<project>.pages.dev`
- **Limits**: **Unlimited bandwidth**, 500 builds/month, 1 concurrent build, 500 files, 25MB/file
- **Functions**: ✅ Cloudflare Workers (edge functions)
- **Setup**:
  ```bash
  # Via CLI:
  npm install -g wrangler
  wrangler pages project create <project-name>
  wrangler pages deploy docs/ --project-name=<project-name>
  ```
- **Verdict**: ✅ **BEST free tier overall** — unlimited bandwidth, edge functions, 300+ PoPs
- **Pitfalls**: ❗ 500 builds/month limit can be tight with active development; ❗ V8 isolate runtime (not Node.js)

### 3. Netlify
- **URL**: https://netlify.com
- **Deploy**: Git repo, CLI, or drag-and-drop
- **Domain**: `https://<site-name>.netlify.app`
- **Limits**: 100GB bandwidth, 300 build minutes/month, 1 concurrent build
- **Functions**: ✅ Netlify Functions (AWS Lambda, 125K requests/mo free)
- **Forms**: ✅ Netlify Forms for static sites
- **Setup**:
  ```bash
  npm install -g netlify-cli
  netlify deploy --prod --dir docs/
  ```
- **Verdict**: ✅ Great DX, forms & serverless built-in
- **Pitfalls**: ❗ 300 min build limit; ❗ Bandwidth cap lower than Cloudflare

### 4. Vercel
- **URL**: https://vercel.com
- **Deploy**: Git repo or CLI
- **Domain**: `https://<project>.vercel.app`
- **Limits**: 100GB bandwidth, 6000 build minutes/month, 1 concurrent build
- **Functions**: ✅ Vercel Serverless Functions
- **Setup**:
  ```bash
  npm install -g vercel
  vercel --prod docs/
  ```
- **Verdict**: ✅ Best for Next.js; generous build minutes
- **Pitfalls**: ❗ Per-team (not per-project) bandwidth; ❗ Analytics behind paid tier

### 5. Render
- **URL**: https://render.com
- **Deploy**: Git repo
- **Domain**: `https://<project>.onrender.com`
- **Limits**: 100GB bandwidth, static sites free, unlimited builds
- **Features**: ✅ Also offers free PostgreSQL (1GB), Redis, and cron jobs
- **Setup**:
  ```bash
  # Connect GitHub repo in dashboard; auto-deploys on push
  ```
- **Verdict**: ✅ Good for full-stack prototypes (static + DB)
- **Pitfalls**: ❗ Free tier spins down after inactivity (not for static); ❗ Slower than Cloudflare edge

### 6. Surge
- **URL**: https://surge.sh
- **Deploy**: CLI only
- **Domain**: `https://<name>.surge.sh`
- **Limits**: Unlimited bandwidth, 1GB storage (claimed unlimited)
- **Features**: Simplest deploy — single command
- **Setup**:
  ```bash
  npm install -g surge
  # One command:
  surge docs/ my-project.surge.sh
  ```
- **Verdict**: ✅ Simplest deploy; good for quick demos
- **Pitfalls**: ❗ No serverless; ❗ CLI-only; ❗ No git-based auto-deploy

### 7. GitLab Pages
- **URL**: https://gitlab.com/pages
- **Deploy**: Git push + `.gitlab-ci.yml`
- **Domain**: `https://<user>.gitlab.io/<repo>/`
- **Limits**: 400 build minutes/month (shared runners), **private repos allowed**
- **Setup**:
  ```yaml
  # .gitlab-ci.yml
  pages:
    stage: deploy
    script:
      - cp -r docs/ public/
    artifacts:
      paths:
        - public/
    only:
      - main
  ```
- **Verdict**: ✅ Private repos on free tier; CI/CD pipeline
- **Pitfalls**: ❗ Requires CI/CD config; ❗ Less intuitive than GitHub Pages

### 8. Firebase Hosting
- **URL**: https://firebase.google.com/products/hosting
- **Deploy**: CLI
- **Domain**: `https://<project>.web.app`
- **Limits**: 10GB storage, 360MB/day bandwidth, 10GB/mo download
- **Functions**: ✅ Firebase Functions + Firestore DB
- **Setup**:
  ```bash
  npm install -g firebase-tools
  firebase init hosting
  firebase deploy --only hosting
  ```
- **Verdict**: ✅ Good for Google Cloud ecosystem
- **Pitfalls**: ❗ Bandwidth very limited; ❗ Heavy SDK

### 9. Puter
- **URL**: https://puter.com
- **Deploy**: Browser drag-and-drop or API
- **Domain**: `https://<name>.puter.site`
- **Limits**: Free subdomain, instant deploy, no build step
- **Setup**:
  ```
  Drag your project folder into Puter → right-click → "Publish as Website"
  ```
- **Verdict**: ✅ Easiest setup for non-developers
- **Pitfalls**: ❗ No custom domain (free tier); ❗ Unknown reliability/longevity

## Decision Tree

```
For client landing pages (static HTML/CSS/JS):
├── Want easiest + unlimited bandwidth?  → Cloudflare Pages
├── Already on GitHub?                    → GitHub Pages
├── Need forms or serverless?             → Netlify
├── Need Next.js or SSG?                  → Vercel
├── Want private repo?                    → GitLab Pages
├── Quick throwaway demo?                 → Surge
└── Need full stack (DB + hosting)?       → Render
```

## Recommended Pattern for This Project

Our current setup uses:
- **GitHub Pages** from `docs/` folder — works, zero cost
- **One repo** → multiple subdirectories per client (`docs/fargo/`, `docs/salon/`, etc.)

For new clients:
1. Create landing page in `demos/<client-name>/`
2. Mirror to `docs/<client-name>/`
3. Commit & push → auto-deploys

To add **Cloudflare Pages** as a second free option:
```bash
npm install -g wrangler
wrangler pages project create hermes-landings
wrangler pages deploy docs/ --project-name=hermes-landings
# → https://hermes-landings.pages.dev
```

## Limitations on Current Machine

| Platform | CLI Works? | Notes |
|----------|-----------|-------|
| GitHub Pages (gh) | ✅ | Authenticated |
| Git push | ✅ | Via git remote |
| Cloudflare (wrangler) | ⚠️ Untested | May require login |
| Netlify CLI | ⚠️ Untested | May timeout on proxy |
| Vercel CLI | ⚠️ Untested | May timeout on proxy |
| Surge CLI | ⚠️ Untested | May timeout on proxy |

**Workaround**: Browser-based dashboard setup works for all platforms (no CLI needed).
