#!/usr/bin/env python3
"""
Quality Gate — standalone HTML/CSS checker
Usage: python qa_check.py <path/to/index.html>
"""

import sys
import re
import os

def check_html(filepath):
    issues = []
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Structure
    tags = {'html': 0, 'body': 0, 'main': 0, 'header': 0, 'footer': 0, 'section': 0}
    for tag in tags:
        opens = len(re.findall(f'<{tag}[\\s>]', html))
        closes = len(re.findall(f'</{tag}>', html))
        if opens != closes:
            issues.append(f'❌ <{tag}>: {opens} opens, {closes} closes')

    # 2. Images without alt
    imgs = re.findall(r'<img\s[^>]*>', html)
    for img in imgs:
        if 'alt=' not in img:
            src = re.search(r'src="([^"]+)"', img)
            issues.append(f'⚠️  Image missing alt: {src.group(1) if src else "unknown"}')

    # 3. Empty links
    links = re.findall(r'<a\s[^>]*href="([^"]*)"[^>]*>', html)
    for href in links:
        if href in ('#', '', '#'):
            text = re.search(r'>([^<]+)<', html[html.find(f'href="{href}"'):html.find(f'href="{href}"')+200])
            issues.append(f'⚠️  Empty link: {text.group(1) if text else "unknown"}')

    # 4. WCAG checks
    if 'skip-link' not in html:
        issues.append('❌ WCAG: missing skip-link')
    if ':focus-visible' not in html:
        issues.append('❌ WCAG: missing focus-visible')
    if 'role="main"' not in html:
        issues.append('❌ WCAG: missing role="main"')
    if 'role="banner"' not in html:
        issues.append('❌ WCAG: missing role="banner"')
    if 'role="contentinfo"' not in html:
        issues.append('❌ WCAG: missing role="contentinfo"')

    # 5. Form labels
    labels = re.findall(r'<label[^>]*>', html)
    for label in labels:
        if 'for=' not in label:
            text = re.search(r'>([^<]+)<', html[html.find(label):html.find(label)+100])
            issues.append(f'⚠️  Label missing for=: {text.group(1) if text else "unknown"}')

    # 6. Local asset files exist
    base_dir = os.path.dirname(os.path.abspath(filepath))
    local_imgs = re.findall(r'<img[^>]*src="([^"]+)"', html)
    for src in local_imgs:
        if src.startswith('http') or src.startswith('//') or src.startswith('data:'):
            continue
        asset_path = os.path.join(base_dir, src)
        if not os.path.exists(asset_path):
            issues.append(f'❌ Image not found: {src}')
    
    # 7. Content completeness - no placeholder text
    placeholders = ['добавьте фото', 'добавьте отзыв', 'Фото косметолога', 'Фото до/после']
    for ph in placeholders:
        if ph.lower() in html.lower():
            issues.append(f'⚠️  Placeholder text remains: "{ph}"')
    
    # 8. Meta description
    if '<meta name="description"' not in html and '<meta property="og:description"' not in html:
        issues.append('⚠️  Missing meta description or OG description')
    
    return issues
    return issues

def main():
    if len(sys.argv) < 2:
        print("Usage: python qa_check.py <file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)
    
    print("=== QUALITY GATE REPORT ===")
    print(f"File: {filepath}")
    print()
    
    issues = check_html(filepath)
    
    if not issues:
        print("✅ ALL CHECKS PASSED")
        print("✅ Структура: OK")
        print("✅ Ресурси: OK")
        print("✅ WCAG: OK")
        print()
        print("Вердикт: PASS")
        sys.exit(0)
    else:
        print(f"\nIssues found: {len(issues)}")
        print()
        for issue in issues:
            print(issue)
        print()
        print("Вердикт: REWORK")
        sys.exit(1)

if __name__ == '__main__':
    main()
