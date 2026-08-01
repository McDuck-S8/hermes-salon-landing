# 2026-07-29 — Stray | Character SyntaxError + IntersectionObserver Fail

## The Bug
A single stray pipe character `|` before `}catch(e){` in JS caused a SyntaxError that prevented the ENTIRE `<script>` block from parsing. All 4 IIFE blocks died silently.

## Detection Path
1. User reported: "only master photo block visible" on mobile
2. Browser desktop showed all sections in DOM — but `.reveal` elements had `opacity:0`
3. `document.querySelectorAll('.reveal.visible').length` → 0 (IntersectionObserver never fired)
4. `typeof window.moveSlide` → `"undefined"` (script never executed)
5. Browser console: 1 JS error (empty message, no stack — SyntaxError)
6. `node --check /tmp/extracted.js` → SyntaxError at line with `|}catch(e){`

## Root Fixes

### Fix 1: Remove stray `|` on line 437
```diff
-|}catch(e){console.warn('scroll:',e)}})();
+}catch(e){console.warn('scroll:',e)}})();
```

### Fix 2: Progressive enhancement for scroll reveal
`.reveal{opacity:0;transform:translateY(20px)}` with `.reveal.visible{opacity:1}` means if JS fails, content is invisible. 
Replaced with: `.reveal{opacity:1;transform:none}` (always visible), JS adds `.reveal-hidden` for animation.

### Fix 3: Hero layout
Removed `grid` + `dvh` + `overflow:hidden` + `order:-1`, replaced with simple `flex` + `column-reverse`.

## Verification
After fixes:
- `typeof window.moveSlide` → `"function"`
- `node --check` passes
