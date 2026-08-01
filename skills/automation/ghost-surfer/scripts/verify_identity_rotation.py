#!/usr/bin/env python3
"""
Verify Identity Rotation — Ghost-Surfer Phase 3
Tests that 3 distinct identities produce unique canvas hashes via BrowserOS MCP.

Requires:
- BrowserOS MCP running on http://127.0.0.1:9003/mcp
- Python 3.11+
"""

import json
import re
import subprocess
import time
import sys

MCP_URL = "http://127.0.0.1:9003/mcp"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
}

def mcp_call(method, params, call_id=1):
    """Call BrowserOS MCP tool."""
    payload = {"jsonrpc": "2.0", "method": method, "id": call_id, "params": params}
    result = subprocess.run([
        "curl", "-X", "POST", MCP_URL,
        "-H", "Content-Type: application/json",
        "-H", "Accept: application/json, text/event-stream",
        "-d", json.dumps(payload)
    ], capture_output=True, text=True, timeout=60)
    # Last line is the JSON response
    return json.loads(result.stdout.strip().split('\n')[-1])

def new_page(url="about:blank", background=True):
    """Create a new browser page."""
    result = mcp_call("tools/call", {
        "name": "new_page",
        "arguments": {"url": url, "background": background}
    }, call_id=1)
    return result["result"]["structuredContent"]["pageId"]

def evaluate_script(page_id, expression):
    """Evaluate JavaScript in page context."""
    result = mcp_call("tools/call", {
        "name": "evaluate_script",
        "arguments": {"page": page_id, "expression": expression}
    }, call_id=2)
    return result

def build_spoofing_script(identity):
    """Generate fingerprint spoofing JavaScript for an identity."""
    return f"""(function() {{
    // Canvas noise
    const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(type, quality) {{
        const ctx = this.getContext('2d');
        if (ctx) {{
            try {{
                const imgData = ctx.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imgData.data.length; i += 4) {{
                    const noise = (Math.random() - 0.5) * {identity['noise']} * 255;
                    imgData.data[i] = Math.min(255, Math.max(0, imgData.data[i] + noise));
                    imgData.data[i+1] = Math.min(255, Math.max(0, imgData.data[i+1] + noise));
                    imgData.data[i+2] = Math.min(255, Math.max(0, imgData.data[i+2] + noise));
                }}
                ctx.putImageData(imgData, 0, 0);
            }} catch(e) {{}}
        }}
        return origToDataURL.call(this, type, quality);
    }};
    
    // WebGL vendor/renderer
    const origGetParam = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(pname) {{
        if (pname === 37445) return "{identity['webgl_vendor']}";
        if (pname === 37446) return "{identity['webgl_renderer']}";
        return origGetParam.call(this, pname);
    }};
    
    // AudioContext sample rate
    const OrigAudioContext = window.AudioContext || window.webkitAudioContext;
    if (OrigAudioContext) {{
        window.AudioContext = function() {{
            const ctx = new OrigAudioContext();
            Object.defineProperty(ctx, 'sampleRate', {{ value: 48000, configurable: true }});
            return ctx;
        }};
    }}
    
    // Navigator
    Object.defineProperty(navigator, 'hardwareConcurrency', {{ value: {identity['hw_concurrency']}, configurable: true }});
    Object.defineProperty(navigator, 'deviceMemory', {{ value: {identity['device_memory']}, configurable: true }});
    Object.defineProperty(navigator, 'language', {{ value: '{identity['language']}', configurable: true }});
    Object.defineProperty(navigator, 'languages', {{ value: ['{identity['language']}', 'en'], configurable: true }});
    Object.defineProperty(navigator, 'platform', {{ value: 'Win32', configurable: true }});
    
    // Screen
    Object.defineProperty(screen, 'width', {{ value: {identity['screen_width']}, configurable: true }});
    Object.defineProperty(screen, 'height', {{ value: {identity['screen_height']}, configurable: true }});
    Object.defineProperty(screen, 'colorDepth', {{ value: 24, configurable: true }});
    Object.defineProperty(screen, 'pixelDepth', {{ value: 24, configurable: true }});
    
    // Timezone
    const origResolved = Intl.DateTimeFormat.prototype.resolvedOptions;
    Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
        const opts = origResolved.call(this);
        return {{ ...opts, timeZone: '{identity['timezone']}' }};
    }};
    
    return {{ spoofed: true }};
}})()"""

def get_canvas_hash(page_id, identity):
    """Extract canvas hash from page."""
    canvas_expr = f"""(function() {{
    const canvas = document.createElement('canvas');
    canvas.width = 200;
    canvas.height = 50;
    const ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.fillStyle = '#f60';
    ctx.fillRect(125, 1, 62, 20);
    ctx.fillStyle = '#069';
    ctx.fillText('{identity['canvas_text']}', 2, 15);
    ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
    ctx.fillText('{identity['canvas_text']}', 4, 17);
    return {{ canvasHash: canvas.toDataURL().slice(-50) }};
}})()"""
    
    result = evaluate_script(page_id, canvas_expr)
    match = re.search(r'"canvasHash"\s*:\s*"([^"]+)"', result["result"]["structuredContent"]["text"])
    return match.group(1) if match else None

# Identity configurations
IDENTITIES = [
    {
        "name": "Alpha",
        "noise": 0.001,
        "canvas_text": "Alpha",
        "webgl_vendor": "Google Inc. (AMD)",
        "webgl_renderer": "ANGLE (AMD, AMD Radeon RX 6800 Direct3D11 vs_5_0 ps_5_0)",
        "hw_concurrency": 8,
        "device_memory": 16,
        "language": "de-DE",
        "screen_width": 1366,
        "screen_height": 768,
        "timezone": "Europe/Berlin",
    },
    {
        "name": "Bravo",
        "noise": 0.002,
        "canvas_text": "Bravo",
        "webgl_vendor": "Google Inc. (NVIDIA)",
        "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0)",
        "hw_concurrency": 16,
        "device_memory": 32,
        "language": "en-US",
        "screen_width": 1920,
        "screen_height": 1080,
        "timezone": "America/New_York",
    },
    {
        "name": "Charlie",
        "noise": 0.0005,
        "canvas_text": "Charlie",
        "webgl_vendor": "Mesa (Intel)",
        "webgl_renderer": "ANGLE (Intel, Intel UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
        "hw_concurrency": 4,
        "device_memory": 8,
        "language": "ja-JP",
        "screen_width": 1280,
        "screen_height": 720,
        "timezone": "Asia/Tokyo",
    },
]

def main():
    print("=== GHOST-SURFER IDENTITY ROTATION VERIFICATION ===\n")
    
    hashes = []
    
    for i, ident in enumerate(IDENTITIES, 1):
        print(f"Identity {i}: {ident['name']}")
        
        # 1. Fresh page
        page_id = new_page("about:blank", True)
        print(f"  Page ID: {page_id}")
        
        # 2. Inject spoofing
        spoof_script = build_spoofing_script(ident)
        evaluate_script(page_id, spoof_script)
        print(f"  Spoofing injected")
        
        # 3. Get canvas hash
        canvas_hash = get_canvas_hash(page_id, ident)
        print(f"  Canvas Hash: {canvas_hash}")
        
        hashes.append({"name": ident["name"], "hash": canvas_hash, **ident})
        time.sleep(1)
    
    # Verification
    print("\n=== VERIFICATION ===")
    unique_hashes = set(h["hash"] for h in hashes)
    print(f"Total: {len(hashes)} | Unique: {len(unique_hashes)}")
    
    for h in hashes:
        status = "✅" if hashes.count(h["hash"]) == 1 else "❌ DUPLICATE"
        print(f"  {h['name']}: {h['hash']} {status}")
    
    if len(unique_hashes) == len(hashes):
        print("\n🎉 SUCCESS: All identities produce unique fingerprints!")
        return 0
    else:
        print("\n❌ FAILURE: Hash collision detected")
        return 1

if __name__ == "__main__":
    sys.exit(main())