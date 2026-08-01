#!/usr/bin/env python3
"""FAANG Prep Mini App Generator.
Generates a Telegram Mini App HTML with coding problems + TON premium section.
Usage: python scripts/famp_generator.py
"""

import json, os

OUT = "projects/famp-prep/index.html"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

problems = {
    "Массивы": [
        {"title": "Two Sum", "difficulty": "Easy",
         "code": "def twoSum(nums, target):\n    prev = {}\n    for i, n in enumerate(nums):\n        diff = target - n\n        if diff in prev:\n            return [prev[diff], i]\n        prev[n] = i",
         "explanation": "Хэш-таблица: для каждого числа ищем разницу target - n. O(n) время, O(n) память."},
        {"title": "Maximum Subarray", "difficulty": "Medium",
         "code": "def maxSubArray(nums):\n    max_sum = nums[0]\n    cur = 0\n    for n in nums:\n        if cur < 0: cur = 0\n        cur += n\n        max_sum = max(max_sum, cur)\n    return max_sum",
         "explanation": "Алгоритм Кадана: обнуляем сумму если отрицательная. O(n), O(1)."},
        {"title": "Contains Duplicate", "difficulty": "Easy",
         "code": "def containsDuplicate(nums):\n    return len(nums) != len(set(nums))",
         "explanation": "Сравниваем длину массива с длиной множества. O(n), O(n)."}
    ],
    "Строки": [
        {"title": "Valid Parentheses", "difficulty": "Easy",
         "code": "def isValid(s):\n    stack = []\n    pairs = {')': '(', '}': '{', ']': '['}\n    for c in s:\n        if c in pairs:\n            if not stack or stack.pop() != pairs[c]:\n                return False\n        else:\n            stack.append(c)\n    return not stack",
         "explanation": "Стек для отслеживания открывающих скобок. O(n), O(n)."},
        {"title": "Longest Substring", "difficulty": "Medium",
         "code": "def lengthOfLongestSubstring(s):\n    seen = {}\n    left = max_len = 0\n    for right, c in enumerate(s):\n        if c in seen and seen[c] >= left:\n            left = seen[c] + 1\n        seen[c] = right\n        max_len = max(max_len, right - left + 1)\n    return max_len",
         "explanation": "Скользящее окно с хэш-картой позиций символов. O(n), O(n)."},
        {"title": "Valid Anagram", "difficulty": "Easy",
         "code": "def isAnagram(s, t):\n    if len(s) != len(t): return False\n    from collections import Counter\n    return Counter(s) == Counter(t)",
         "explanation": "Сравниваем частотные словари символов. O(n), O(n)."}
    ],
    "Деревья": [
        {"title": "Max Depth of Binary Tree", "difficulty": "Easy",
         "code": "def maxDepth(root):\n    if not root: return 0\n    return 1 + max(maxDepth(root.left), maxDepth(root.right))",
         "explanation": "Рекурсивный DFS: глубина = 1 + макс(левая, правая). O(n), O(h)."},
        {"title": "Invert Binary Tree", "difficulty": "Easy",
         "code": "def invertTree(root):\n    if root:\n        root.left, root.right = invertTree(root.right), invertTree(root.left)\n    return root",
         "explanation": "Меняем местами левого и правого потомка рекурсивно. O(n), O(h)."},
        {"title": "Symmetric Tree", "difficulty": "Easy",
         "code": "def isSymmetric(root):\n    def mirror(a, b):\n        if not a and not b: return True\n        if not a or not b: return False\n        return (a.val == b.val\n                and mirror(a.left, b.right)\n                and mirror(a.right, b.left))\n    return mirror(root, root)",
         "explanation": "Проверяем зеркальность левого и правого поддеревьев. O(n), O(h)."}
    ]
}

cat_icons = {"Массивы": "📊", "Строки": "📝", "Деревья": "🌳"}

html = f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no">
<title>FAANG PREP</title>
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<style>
:root {{ --bg: #0d0d12; --card: #1a1a24; --accent: #6366f1; --text: #f1f1f6; --muted: #8b8ba3; --easy: #22c55e; --med: #eab308; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:var(--bg); color:var(--text); padding:16px 14px 100px; }}
h1 {{ text-align:center; font-size:22px; letter-spacing:2px; text-transform:uppercase; margin:16px 0 24px; background:linear-gradient(135deg,#6366f1,#a855f7); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
.cat {{ margin-bottom:28px; }}
.cat-title {{ font-size:17px; font-weight:700; margin-bottom:12px; color:var(--muted); display:flex; align-items:center; gap:8px; }}
.card {{ background:var(--card); border-radius:14px; padding:14px 16px; margin-bottom:10px; border:1px solid rgba(255,255,255,0.06); }}
.card-hdr {{ display:flex; justify-content:space-between; align-items:center; cursor:pointer; }}
.card-hdr:active {{ opacity:0.7; }}
.title {{ font-weight:600; font-size:15px; }}
.diff {{ font-size:11px; font-weight:700; padding:2px 8px; border-radius:6px; text-transform:uppercase; }}
.Easy {{ color:var(--easy); background:rgba(34,197,94,0.12); }}
.Medium {{ color:var(--med); background:rgba(234,179,8,0.12); }}
.body {{ display:none; margin-top:12px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.08); }}
pre {{ background:#08080e; padding:12px; border-radius:10px; font-size:13px; line-height:1.5; overflow-x:auto; color:#a9dc76; font-family:'JetBrains Mono','Fira Code',monospace; }}
.exp {{ font-size:13px; color:var(--muted); margin-top:8px; line-height:1.5; }}
.premium {{ margin-top:36px; background:linear-gradient(135deg,#312e81,#6b21a8); border-radius:18px; padding:24px 20px; text-align:center; }}
.premium h3 {{ font-size:18px; margin-bottom:6px; }}
.premium p {{ font-size:14px; color:rgba(255,255,255,0.75); margin-bottom:16px; }}
.ton-btn {{ display:inline-block; background:#fff; color:#312e81; border:none; padding:14px 32px; border-radius:30px; font-weight:700; font-size:15px; cursor:pointer; text-decoration:none; transition:transform .1s; }}
.ton-btn:active {{ transform:scale(.96); }}
small {{ display:block; text-align:center; margin-top:24px; color:var(--muted); font-size:12px; }}
</style>
</head>
<body>
<h1>𓃠 FAANG PREP</h1>
'''

for cat, items in problems.items():
    html += f'<div class="cat"><div class="cat-title">{cat_icons[cat]} {cat}</div>'
    for p in items:
        pid = p['title'].replace(' ', '_').lower()
        html += f'''
<div class="card">
  <div class="card-hdr" onclick="t(\'{pid}\')">
    <span class="title">{p['title']}</span>
    <span class="diff {p['difficulty']}">{p['difficulty']}</span>
  </div>
  <div id="{pid}" class="body">
    <pre>{p['code']}</pre>
    <div class="exp">{p['explanation']}</div>
  </div>
</div>'''
    html += '</div>'

html += '''
<div class="premium">
  <h3>🚀 Pro Access</h3>
  <p>50+ задач · AI Mock Interview · Полные разборы</p>
  <a href="https://tonhub.app/connect" class="ton-btn" target="_blank">Оплатить 1 TON</a>
</div>

<small>FAANG Prep v1.0 · Решения от сообщества</small>

<script>
const tg=window.Telegram.WebApp;tg.expand();
tg.MainButton.setText('Поделиться');tg.MainButton.show();
tg.MainButton.onClick(()=>{tg.HapticFeedback.impactOccurred('medium');tg.openLink('https://t.me/share/url?url=https://famp-prep.vercel.app')});
function t(i){const e=document.getElementById(i);e.style.display=e.style.display==='block'?'none':'block'}
</script>
</body>
</html>'''

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"✅ FAANG Prep Mini App created at {OUT}")
print(f"   {sum(len(items) for items in problems.values())} задач")
print(f"   {len(problems)} категорий")
print(f"   TON premium секция добавлена")
