# Recovering a Truncated/Overwritten .py from __pycache__ Bytecode

Scenario (2026-07-31): `scripts/self_improvement_loop.py` (989 lines, ~38KB) was
overwritten during a patch and truncated to 94 lines (only one function survived).
The file was NOT in git history (untracked), no backup existed — but
`scripts/__pycache__/self_improvement_loop.cpython-311.pyc` still held the full
compiled module from the last successful run.

## Recovery Steps

### 1. Check all cheap sources first
```bash
git log --all --oneline -- <file>      # tracked? (empty = untracked)
git stash list && git stash show -p stash@{0} -- <file>
tar -tzf system_state_backup.tar.gz | grep <name>   # any backups?
find . -name "<file>" -not -path "*/.git/*"          # other copies
```

### 2. Extract the code object from the .pyc
Python 3.11+ header is 16 bytes (magic 4 + flags 4 + hash 8):
```python
import struct, marshal
with open('<file>.cpython-311.pyc', 'rb') as f:
    data = f.read()
code = marshal.loads(data[16:])   # module code object
```

### 3. Walk the code object for structure (NO decompiler needed)
```python
for const in code.co_consts:
    if hasattr(const, 'co_name'):
        print(const.co_name)          # every function/class name
        print(ast.get_docstring(const))  # docstrings = contract
# String constants in order of appearance (error messages, SQL, patterns)
print([c for c in code.co_consts if isinstance(c, str)])
# co_names = every imported name + attribute called (reveals API usage)
print(code.co_names)
```
This yields: full function list, docstrings, all literal strings (SQL,
classifier patterns, event names), and the names used for imports/calls —
enough to reconstruct the file with correct signatures and logic.

### 4. Check the exact API of every called module before reconstructing
The pyc's `co_names` shows `emit`, `consume`, `semantic_search` etc. Verify
signatures from the live source:
```bash
python -c "import ast; print([n.args.args for n in ast.walk(ast.parse(open('scripts/emit_event.py').read())) if isinstance(n, ast.FunctionDef) and n.name=='emit'])"
```

### 5. Reconstruct and verify
- Rebuild the file with the recovered signatures/strings
- `python -m py_compile <file>` — syntax
- Run it end-to-end — it must produce the same artifacts as before
  (suggestions JSON, KC writes, events fired)

## Pitfalls
- **`pycdc` from pip is NOT the decompiler** — it's an unrelated travel package.
  The real pycdc is a C++ project you'd have to build; don't waste time.
- **`dis.dis()` on a 3.11 pyc under Python 3.13 fails** with
  `IndexError: tuple index out of range` (incompatible instruction formats).
  Don't need disassembly anyway — co_consts/co_names give the structure.
- `.pyc` may be from an OLDER version of the file than the last on-disk state —
  reconstruct the structure from pyc, but re-check current schemas/APIs
  (PRAGMA table_info, function signatures) before finalizing.
- If no .pyc exists (file never ran successfully), this path is dead — check
  `logs/` for the last traceback containing the module's real call flow.
