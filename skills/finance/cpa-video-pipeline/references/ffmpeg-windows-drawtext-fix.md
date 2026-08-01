# FFmpeg drawtext on Windows — Critical pitfall

## The problem

On Windows, **drive letters with colons** (`C:`, `D:`) **break FFmpeg drawtext** because `:` is the filter option separator in FFmpeg's filterchain syntax.

```bash
# ❌ ERROR: FFmpeg parses "C" as fontfile value, "/Windows/..." as new unnamed option
ffmpeg -vf "drawtext=fontfile=C:/Windows/Fonts/arial.ttf:fontsize=36"
# AVFilterGraph: No option name near '/Windows/Fonts/...'
```

## The fix — three rules

### Rule 1: Relative paths only

Copy fonts to a path without drive letters:

```python
# ✅ Works
font = os.path.relpath("scripts/assets/arial.ttf").replace("\\", "/")
filter_str = f"drawtext=text=Hello:fontfile={font}:fontsize=36"
cmd = ["ffmpeg", "-y", "-i", video_in, "-vf", filter_str, video_out]
```

### Rule 2: Use `text=`, not `textfile=`

`textfile=` paths (temp files in `%TEMP%`) always have a drive letter. Use `text=` directly when possible:

```python
# Before: tempfile with drive letter → broken
tf = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
tf.write("Hello World")
filter_str = f"drawtext=textfile={tf.name}:fontfile={font}"  # ❌

# After: inline text → works (if text has no : or ' chars)
filter_str = f"drawtext=text=Hello World:fontfile={font}:fontsize=36"  # ✅
```

### Rule 3: Auto-copy system font on first run

```python
import os, shutil

ASSETS_DIR = Path("scripts/assets")
FONT_PATH = str(ASSETS_DIR / "Roboto-Bold.ttf")

if not os.path.exists(FONT_PATH):
    os.makedirs(ASSETS_DIR, exist_ok=True)
    src = r"C:\Windows\Fonts\arial.ttf"  # system font
    if os.path.exists(src):
        shutil.copy2(src, FONT_PATH)

# Use relative path — no drive letter
font_rel = os.path.relpath(FONT_PATH).replace("\\", "/")
```

## Why does this happen?

FFmpeg's filter string parser uses `:` as the separator between filter options:
```
drawtext=text=Hello:fontfile=...:fontsize=36:fontcolor=white
         ^                 ^          ^
         option1           option2    option3
```

A Windows path `C:/Windows/Fonts/font.ttf` contains `:` after `C`, so the parser sees:
- `fontfile=C` → fontfile = "C" (wrong)
- `/Windows/Fonts/font.ttf` → next option starts, has no name → error

On Linux, paths never contain colons, so this bug doesn't appear.

## Test if drawtext works

```bash
ffmpeg -y -f lavfi -i "color=c=#1a1a2e:s=608x1080:d=3" \
  -vf "drawtext=text=Hello:fontfile=scripts/assets/arial.ttf:fontsize=36" \
  -c:v libx264 -preset ultrafast test_output.mp4
```

If this fails, check your font path for drive letters.
