import sqlite3

DB_PATH = 'cache/knowledge_cube.db'


> Revisit: when class extraction, class classification, or class-based routing changes. Last touched: 2026-07-02.
def get_uncategorized():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, raw_text FROM experiences WHERE axis_domain="uncategorized"')
    rows = c.fetchall()
    print(f'Total uncategorized: {len(rows)}')
    for rid, txt in rows:
        print(f'{rid}|{txt[:200]}')
    conn.close()
    return rows

def classify_and_update(updates):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for domain, eid in updates:
        c.execute('UPDATE experiences SET axis_domain=?, tags=?, confidence=? WHERE id=?',
                  (domain, 'auto_tagged_llm', 0.7, eid))
    conn.commit()
    print(f'Updated {len(updates)} entries')
    conn.close()

if __name__ == '__main__':
    rows = get_uncategorized()
    
    # Classification rules
    CHITCHAT_PATTERNS = ['ну ', 'да', 'нет', 'ок', 'ага', 'привет', 'пока', 'спасибо', 'хорошо']
    CODE_PATTERNS = ['python', 'javascript', 'install', 'pip', 'npm', 'import', 'function', 'class', 'code', 'programming', 'api']
    BUG_PATTERNS = ['error', 'fix', 'crash', 'bug', 'exception', 'traceback', 'failed', 'doesn\'t work', 'не работает']
    COMM_PATTERNS = ['telegram', 'bot', 'message', 'chat', 'messaging', 'channel']
    TERM_PATTERNS = ['terminal', 'shell', 'command', 'bash', 'process', 'background']
    LEARN_PATTERNS = ['learn', 'understand', 'explain', 'how to', 'что такое', 'почему', 'зачем']
    RESEARCH_PATTERNS = ['compare', 'research', 'analysis', 'difference', 'vs', 'better', 'best']
    FILE_PATTERNS = ['file', 'directory', 'folder', 'path', 'read', 'write', 'save']
    DEVOPS_PATTERNS = ['server', 'deploy', 'docker', 'container', 'config', 'nginx', 'systemd']
    BROWSER_PATTERNS = ['browser', 'selenium', 'chrome', 'firefox', 'page', 'click']
    DATA_PATTERNS = ['data', 'csv', 'json', 'database', 'sql', 'parse', 'convert']
    CREATIVE_PATTERNS = ['design', 'creative', 'image', 'art', 'color', 'font', 'style']
    ARCH_PATTERNS = ['architecture', 'pattern', 'design pattern', 'structure', 'framework']
    DEBUG_PATTERNS = ['debug', 'monitor', 'log', 'watch', 'trace', 'investigate']
    
    updates = []
    for rid, txt in rows:
        txt_lower = txt.lower() if txt else ''
        
        if any(p in txt_lower for p in CHITCHAT_PATTERNS) and len(txt) < 50:
            domain = 'system'
        elif any(p in txt_lower for p in BUG_PATTERNS):
            domain = 'bugfix'
        elif any(p in txt_lower for p in CODE_PATTERNS):
            domain = 'coding'
        elif any(p in txt_lower for p in COMM_PATTERNS):
            domain = 'communication'
        elif any(p in txt_lower for p in TERM_PATTERNS):
            domain = 'terminal'
        elif any(p in txt_lower for p in LEARN_PATTERNS):
            domain = 'learning'
        elif any(p in txt_lower for p in RESEARCH_PATTERNS):
            domain = 'research'
        elif any(p in txt_lower for p in FILE_PATTERNS):
            domain = 'file_ops'
        elif any(p in txt_lower for p in DEVOPS_PATTERNS):
            domain = 'devops'
        elif any(p in txt_lower for p in BROWSER_PATTERNS):
            domain = 'browser'
        elif any(p in txt_lower for p in DATA_PATTERNS):
            domain = 'data'
        elif any(p in txt_lower for p in CREATIVE_PATTERNS):
            domain = 'creative'
        elif any(p in txt_lower for p in ARCH_PATTERNS):
            domain = 'architecture'
        elif any(p in txt_lower for p in DEBUG_PATTERNS):
            domain = 'debugging'
        else:
            domain = 'system'  # default fallback
        
        updates.append((domain, rid))
    
    classify_and_update(updates)
    print('Done')
