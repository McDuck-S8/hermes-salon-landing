#!/usr/bin/env python3
"""
Markdown → Beautiful HTML converter.
Dark theme, responsive, tables, code, charts, Euler/Venn diagrams.

Features:
  - Markdown → HTML with GitHub-dark theme
  - Tables with striped rows
  - Code blocks with syntax background
  - Charts via Chart.js (bar, pie, line, radar, doughnut)
  - Euler/Venn diagrams as inline SVG (2-3 sets)
  - Responsive layout

Usage:
  python md2html.py input.md [output.html] [--charts]
  --charts  enable Chart.js for ```chart blocks
"""
import sys
import re
import math
from pathlib import Path

THEME = {
    'bg': '#0d1117',
    'surface': '#161b22',
    'border': '#30363d',
    'text': '#e6edf3',
    'muted': '#8b949e',
    'accent': '#58a6ff',
    'green': '#3fb950',
    'red': '#f85149',
    'yellow': '#d29922',
    'purple': '#bc8cff',
    'orange': '#d87622',
    'code_bg': '#1c2128',
}

CHART_COLORS = ['#58a6ff', '#3fb950', '#d29922', '#f85149', '#bc8cff', '#d87622', '#79c0ff', '#56d364']


def gen_venn_svg(data, theme):
    """Generate SVG for Euler/Venn diagram (2 or 3 sets).
    data = {'circles': [{label, value}], 'intersections': [{label, value}]}
    """
    sets = data.get('circles', [])
    inters = data.get('intersections', [])
    n = len(sets)
    width, height = 500, 400
    r = 110  # circle radius
    cx, cy = width // 2, height // 2 + 20

    colors = ['#58a6ff', '#3fb950', '#d29922']
    colors_alpha = ['rgba(88,166,255,0.25)', 'rgba(63,185,80,0.25)', 'rgba(210,153,34,0.25)']
    stroke_colors = ['#58a6ff', '#3fb950', '#d29922']

    svg = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="max-width:500px;width:100%;margin:1rem auto;display:block;background:{theme["bg"]}">']
    svg.append(f'<rect width="{width}" height="{height}" fill="{theme["bg"]}" rx="8"/>')

    def add_label(x, y, s, size=14, y_offset=0):
        """Add a text label with optional value below."""
        svg.append(f'<text x="{x}" y="{y+y_offset}" text-anchor="middle" fill="{theme["text"]}" font-size="{size}" font-weight="600">{s.get("label", "")}</text>')
        if s.get('value'):
            svg.append(f'<text x="{x}" y="{y+y_offset+18}" text-anchor="middle" fill="{theme["muted"]}" font-size="12">{s["value"]}</text>')

    if n == 1:
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{colors_alpha[0]}" stroke="{stroke_colors[0]}" stroke-width="2"/>')
        add_label(cx, cy-8, sets[0], size=16)

    elif n == 2:
        dx = r * 0.6
        x1, y1 = cx - dx, cy
        x2, y2 = cx + dx, cy
        svg.append(f'<circle cx="{x1}" cy="{y1}" r="{r}" fill="{colors_alpha[0]}" stroke="{stroke_colors[0]}" stroke-width="2"/>')
        svg.append(f'<circle cx="{x2}" cy="{y2}" r="{r}" fill="{colors_alpha[1]}" stroke="{stroke_colors[1]}" stroke-width="2"/>')
        # Outside labels
        add_label(x1 - r * 0.45, cy-8, sets[0]) if sets else None
        add_label(x2 + r * 0.45, cy-8, sets[1]) if len(sets) > 1 else None
        # Intersection  in center
        if inters:
            add_label(cx, cy-8, inters[0], size=13)
        # Show "both" count
        elif len(sets) > 2:
            add_label(cx, cy-8, sets[2], size=13)

    elif n >= 3:
        angles = [-math.pi/2, math.pi/6, 5*math.pi/6]  # top, bottom-right, bottom-left
        dist = r * 0.65
        centers = [(cx + dist * math.cos(a), cy + dist * math.sin(a)) for a in angles]
        for i, (x, y) in enumerate(centers):
            svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{colors_alpha[i]}" stroke="{stroke_colors[i]}" stroke-width="2"/>')
        # Labels outside each circle
        label_pos = [(cx, cy - r * 1.35), (cx + r * 1.2, cy + r * 0.7), (cx - r * 1.2, cy + r * 0.7)]
        for i, s in enumerate(sets[:3]):
            if i < len(label_pos):
                add_label(label_pos[i][0], label_pos[i][1], s)
        # Center triple intersection
        for inter in inters:
            add_label(cx, cy-4, inter, size=13)

    svg.append('</svg>')
    return '\n'.join(svg)


def parse_venn_block(lines):
    """Parse venn fenced block into main sets and intersections.
    Labels containing ∩, ∩, 'and', 'intersection' = intersection label.
    Returns: {'circles': [{label, value}], 'intersections': [{label, value}]}
    """
    circles = []
    inter = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^([A-Za-zА-Яа-яЁё\s]+?)(?:\s*[:-]\s*)(.+)$', line)
        label, value = '', ''
        if m:
            label = m.group(1).strip()
            rest = m.group(2).strip()
            val_m = re.search(r'\(([^)]+)\)', rest)
            value = val_m.group(1) if val_m else rest
        else:
            label = line

        # Detect intersection markers (∩ unicode, or label starts with intersection keyword)
        lower_label = label.lower().strip()
        intersection_words = ('both', 'all', 'оба', 'все', 'and', 'intersection', 'пересечение', 'overlap')
        if '∩' in lower_label or lower_label.split()[0] in intersection_words:
            inter.append({'label': label, 'value': value})
        else:
            circles.append({'label': label, 'value': value})

    return {'circles': circles[:3], 'intersections': inter}


def parse_chart_block(lines):
    """Parse a chart fenced block into {type, datasets, labels}."""
    chart = {'type': 'bar', 'labels': [], 'datasets': [{'label': '', 'data': []}]}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('type:'):
            chart['type'] = line.split(':', 1)[1].strip()
        elif line.startswith('label:'):
            chart['datasets'][0]['label'] = line.split(':', 1)[1].strip()
        elif re.match(r'^\s*-\s+', line):
            item = re.sub(r'^\s*-\s+', '', line)
            if ':' in item:
                parts = item.split(':', 1)
                chart['labels'].append(parts[0].strip())
                try:
                    chart['datasets'][0]['data'].append(float(parts[1].strip()))
                except ValueError:
                    chart['datasets'][0]['data'].append(0)
            else:
                chart['labels'].append(item)
    return chart


def gen_chart_html(chart, chart_id):
    """Generate Chart.js HTML for a chart block."""
    labels_json = json.dumps(chart['labels'])
    data_json = json.dumps(chart['datasets'][0]['data'])
    type_str = chart['type']
    label_str = chart['datasets'][0]['label']

    color_str = str(CHART_COLORS[:len(chart['datasets'][0]['data'])])
    bg = 'rgba(88,166,255,0.5)' if type_str in ('bar', 'radar') else color_str
    if type_str in ('pie', 'doughnut'):
        bg = color_str

    return f'''<div style="max-width:600px;margin:1rem auto;">
  <canvas id="chart_{chart_id}"></canvas>
</div>
<script>
new Chart(document.getElementById('chart_{chart_id}'), {{
  type: '{type_str}',
  data: {{
    labels: {labels_json},
    datasets: [{{
      label: '{label_str}',
      data: {data_json},
      backgroundColor: {color_str},
      borderColor: {color_str},
      borderWidth: 1
    }}]
  }},
  options: {{
    responsive: true,
    plugins: {{ legend: {{ labels: {{ color: '#8b949e' }} }} }},
    scales: {{
      x: {{ ticks: {{ color: '#8b949e' }}, grid: {{ color: '#30363d' }} }},
      y: {{ ticks: {{ color: '#8b949e' }}, grid: {{ color: '#30363d' }} }}
    }}
  }}
}});
</script>'''


def md_to_html(md_text: str, enable_charts: bool = False) -> str:
    """Convert markdown to HTML with enhanced styling."""
    lines = md_text.split('\n')
    html_parts = []
    in_table = False
    in_code = False
    in_venn = False
    in_chart = False
    code_lang = ''
    code_lines = []
    chart_counter = [0]

    def flush_table(rows):
        if not rows:
            return ''
        out = '<table>\n<thead>\n<tr>'
        for cell in rows[0]:
            out += f'<th>{cell.strip()}</th>'
        out += '</tr>\n</thead>\n<tbody>\n'
        for row in rows[1:]:
            out += '<tr>'
            for cell in row:
                out += f'<td>{cell.strip()}</td>'
            out += '</tr>\n'
        out += '</tbody>\n</table>'
        return out

    def inline_format(text):
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        return text

    def flush_code():
        escaped = '\n'.join(code_lines).replace('<', '&lt;').replace('>', '&gt;')
        return f'<pre><code>{escaped}</code></pre>'

    table_rows = []
    for line in lines:
        stripped = line.strip()

        # Close any open fenced block
        if stripped.startswith('```'):
            if in_venn:
                sets = parse_venn_block(code_lines)
                html_parts.append(gen_venn_svg(sets, THEME))
                code_lines = []
                in_venn = False
                continue
            if in_chart:
                chart = parse_chart_block(code_lines)
                chart_counter[0] += 1
                html_parts.append(gen_chart_html(chart, chart_counter[0]))
                code_lines = []
                in_chart = False
                continue
            if in_code:
                html_parts.append(flush_code())
                code_lines = []
                in_code = False
                continue
            # Open new code block
            code_lang = stripped[3:].strip()
            if in_table:
                html_parts.append(flush_table(table_rows))
                table_rows = []
                in_table = False
            if code_lang == 'venn':
                in_venn = True
                code_lines = []
            elif code_lang == 'chart':
                in_chart = True
                code_lines = []
            else:
                in_code = True
                code_lines = []
            continue

        if in_venn:
            code_lines.append(line)
            continue
        if in_chart:
            code_lines.append(line)
            continue
        if in_code:
            code_lines.append(line)
            continue

        # Table detection
        if '|' in stripped and stripped.startswith('|'):
            cells = [c for c in stripped.split('|')[1:-1]]
            if all(re.match(r'^[-:]+$', c.strip()) for c in cells):
                continue
            table_rows.append(cells)
            in_table = True
            continue
        elif in_table:
            html_parts.append(flush_table(table_rows))
            table_rows = []
            in_table = False

        # Empty line
        if not stripped:
            html_parts.append('')
            continue

        # Headers
        if stripped.startswith('#'):
            m = re.match(r'^(#{1,6})\s+(.*)', stripped)
            if m:
                level = len(m.group(1))
                text = inline_format(m.group(2))
                html_parts.append(f'<h{level}>{text}</h{level}>')
                continue

        # Horizontal rule
        if stripped in ('---', '***', '___'):
            html_parts.append('<hr>')
            continue

        # Blockquote
        if stripped.startswith('>'):
            text = inline_format(stripped[1:].strip())
            html_parts.append(f'<blockquote>{text}</blockquote>')
            continue

        # List items
        if re.match(r'^[-*]\s+', stripped):
            text = inline_format(stripped[2:].strip())
            html_parts.append(f'<li>{text}</li>')
            continue
        if re.match(r'^\d+\.\s+', stripped):
            text = inline_format(re.sub(r'^\d+\.\s+', '', stripped))
            html_parts.append(f'<li>{text}</li>')
            continue

        # Regular paragraph
        html_parts.append(f'<p>{inline_format(stripped)}</p>')

    if in_table:
        html_parts.append(flush_table(table_rows))
    if in_code:
        html_parts.append(flush_code())
    if in_venn:
        sets = parse_venn_block(code_lines)
        html_parts.append(gen_venn_svg(sets, THEME))

    return '\n'.join(html_parts)


def convert(input_path: str, output_path: str = None, charts: bool = False) -> str:
    """Convert markdown file to HTML. Returns output path."""
    import json as _json
    global json
    json = _json
    inp = Path(input_path)
    if not inp.exists():
        print(f"File not found: {input_path}")
        sys.exit(1)

    if output_path is None:
        output_path = str(inp.with_suffix('.html'))

    md_text = inp.read_text(encoding='utf-8')
    title = inp.stem.replace('_', ' ').replace('-', ' ').title()
    body = md_to_html(md_text, enable_charts=charts)

    chart_script = ''
    if charts:
        chart_script = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>\n'

    template = HTML_TEMPLATE.replace('{chart_script}', chart_script)
    html = template.format(title=title, body=body, **THEME)
    Path(output_path).write_text(html, encoding='utf-8')
    print(f"✓ {output_path}")
    return output_path


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{chart_script}<style>
:root {{
  --bg: {bg};
  --surface: {surface};
  --border: {border};
  --text: {text};
  --muted: {muted};
  --accent: {accent};
  --green: {green};
  --red: {red};
  --yellow: {yellow};
  --code-bg: {code_bg};
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  padding: 2rem;
  max-width: 900px;
  margin: 0 auto;
}}
h1 {{ font-size: 2rem; margin: 1.5rem 0 0.5rem; color: var(--accent); border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }}
h2 {{ font-size: 1.5rem; margin: 1.5rem 0 0.5rem; color: var(--text); }}
h3 {{ font-size: 1.2rem; margin: 1rem 0 0.5rem; color: var(--yellow); }}
p {{ margin: 0.5rem 0; }}
a {{ color: var(--accent); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
hr {{ border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }}
strong {{ color: var(--text); }}
em {{ color: var(--muted); }}
table {{
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.9rem;
}}
th, td {{
  padding: 0.6rem 1rem;
  border: 1px solid var(--border);
  text-align: left;
}}
th {{
  background: var(--surface);
  color: var(--accent);
  font-weight: 600;
}}
tr:nth-child(even) {{ background: var(--surface); }}
tr:hover {{ background: rgba(88, 166, 255, 0.05); }}
code {{
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  background: var(--code-bg);
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-size: 0.85em;
  color: var(--yellow);
}}
pre {{
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1rem;
  margin: 1rem 0;
  overflow-x: auto;
  font-size: 0.85rem;
  line-height: 1.5;
}}
pre code {{
  background: none;
  padding: 0;
  color: var(--text);
}}
ul, ol {{ margin: 0.5rem 0 0.5rem 1.5rem; }}
li {{ margin: 0.25rem 0; }}
blockquote {{
  border-left: 3px solid var(--accent);
  padding: 0.5rem 1rem;
  margin: 1rem 0;
  background: var(--surface);
  border-radius: 0 6px 6px 0;
  color: var(--muted);
}}
.stats {{
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin: 1rem 0;
}}
.stat {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem 1.5rem;
  text-align: center;
  min-width: 120px;
}}
.stat-value {{
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--accent);
}}
.stat-label {{
  font-size: 0.8rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}}
.tag {{
  display: inline-block;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0.15rem 0.6rem;
  font-size: 0.75rem;
  color: var(--muted);
  margin: 0.1rem;
}}
.emoji {{ font-size: 1.2em; }}
@media (max-width: 600px) {{
  body {{ padding: 1rem; }}
  .stats {{ flex-direction: column; }}
}}
</style>
</head>
<body>
{body}
</body>
</html>"""


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python md2html.py input.md [output.html] [--charts]")
        sys.exit(1)
    args = sys.argv[1:]
    inp = args[0]
    out = None
    charts = '--charts' in args
    if len(args) >= 2 and args[1] != '--charts':
        out = args[1]
    convert(inp, out, charts=charts)
