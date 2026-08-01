
import subprocess, re, json, sys
sys.path.insert(0, "D:/Portable_Soft/hermes/scripts")

urls = [
    "https://www.youtube.com/watch?v=L9vDhq_W3Tk",
    "https://www.youtube.com/watch?v=8m-YA7jphM0", 
    "https://www.youtube.com/watch?v=qiDalcMeBFk"
]

from autonomy.tactical_buffer import TacticalBuffer
tb = TacticalBuffer()

for url in urls:
    vid = url.split("v=")[1].split("&")[0]
    print(f"Processing {vid}...")
    
    # oembed через proxy
    try:
        result = subprocess.run([
            "curl", "-sL", "--max-time", "10",
            "--proxy", "socks5://127.0.0.1:10806",
            f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json"
        ], capture_output=True, text=True, timeout=15, env={**os.environ, **{"ALL_PROXY": "socks5://127.0.0.1:10806", "HTTPS_PROXY": "socks5://127.0.0.1:10806"}})
        
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            title = data.get("title", "Unknown")
            author = data.get("author_name", "Unknown")
            print(f"{vid}: {title} by {author}")
            
            # Save to tactical buffer
            from autonomy.tactical_buffer import TacticalBuffer
            tb = TacticalBuffer()
            tb.add(
                param=f"video_{vid}",
                value={"video_id": vid, "title": title, "author": author, "concepts": ["extracted"]},
                source="video",
                context_tags={"task_type": "video_research", "video_id": vid}
            )
    except Exception as e:
        print(f"Error for {vid}: {e}")
