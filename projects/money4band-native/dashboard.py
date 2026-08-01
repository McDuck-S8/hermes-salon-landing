"""
Money4Band Native — Web Dashboard
══════════════════════════════════
Lightweight web dashboard using aiohttp.
Shows status, earnings, and controls for all apps.
"""

import json
import asyncio
from pathlib import Path
from aiohttp import web


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>💰 Money4Band Native</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #0a0a0f; color: #e0e0e0; min-height: 100vh; }
  .header { background: linear-gradient(135deg, #1a1a2e, #16213e);
             padding: 24px 32px; border-bottom: 1px solid #333; }
  .header h1 { font-size: 24px; color: #00d4ff; }
  .header p { color: #888; margin-top: 4px; font-size: 14px; }
  .container { max-width: 1200px; margin: 0 auto; padding: 24px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
           gap: 16px; margin-top: 16px; }
  .card { background: #12121a; border: 1px solid #2a2a3a; border-radius: 12px;
          padding: 20px; transition: border-color 0.2s; }
  .card:hover { border-color: #00d4ff; }
  .card-header { display: flex; justify-content: space-between; align-items: center; }
  .card-title { font-size: 18px; font-weight: 600; }
  .badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
  .badge-running { background: #0a3d0a; color: #4ade80; }
  .badge-stopped { background: #3d0a0a; color: #f87171; }
  .badge-disabled { background: #2a2a3a; color: #888; }
  .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 16px; }
  .stat { text-align: center; padding: 12px; background: #0a0a12; border-radius: 8px; }
  .stat-value { font-size: 20px; font-weight: 700; color: #00d4ff; }
  .stat-label { font-size: 11px; color: #888; margin-top: 2px; text-transform: uppercase; }
  .error { color: #f87171; font-size: 13px; margin-top: 8px; }
  .controls { margin-top: 16px; display: flex; gap: 8px; }
  .btn { padding: 8px 16px; border-radius: 8px; border: none; cursor: pointer;
         font-size: 13px; font-weight: 600; transition: opacity 0.2s; }
  .btn:hover { opacity: 0.8; }
  .btn-primary { background: #00d4ff; color: #000; }
  .btn-danger { background: #f87171; color: #000; }
  .total { text-align: center; padding: 24px; background: linear-gradient(135deg, #12121a, #1a1a2e);
           border-radius: 12px; border: 1px solid #2a2a3a; margin-bottom: 16px; }
  .total-value { font-size: 36px; font-weight: 700; color: #4ade80; }
  .total-label { color: #888; font-size: 14px; }
  #auto-refresh { color: #888; font-size: 12px; margin-top: 8px; }
</style>
</head>
<body>
<div class="header">
  <h1>💰 Money4Band Native</h1>
  <p>Passive income from unused bandwidth — no Docker needed</p>
</div>
<div class="container">
  <div class="total">
    <div class="total-label">Total Earnings</div>
    <div class="total-value" id="total-earnings">$0.00</div>
    <div id="auto-refresh">Auto-refresh: 30s</div>
  </div>
  <div class="grid" id="apps-grid"></div>
</div>
<script>
async function refresh() {
  try {
    const resp = await fetch('/api/status');
    const data = await resp.json();
    const grid = document.getElementById('apps-grid');
    grid.innerHTML = '';
    let total = 0;
    data.forEach(app => {
      const earning = parseFloat(app.earnings.replace('$','')) || 0;
      total += earning;
      const badgeClass = app.running ? 'badge-running' : (app.config_ok ? 'badge-stopped' : 'badge-disabled');
      const statusText = app.running ? 'RUNNING' : (app.config_ok ? 'STOPPED' : 'NO CONFIG');
      grid.innerHTML += `
        <div class="card">
          <div class="card-header">
            <span class="card-title">${app.name.toUpperCase()}</span>
            <span class="badge ${badgeClass}">${statusText}</span>
          </div>
          <div class="stats">
            <div class="stat">
              <div class="stat-value">${app.earnings}</div>
              <div class="stat-label">Earnings</div>
            </div>
            <div class="stat">
              <div class="stat-value">${app.uptime}</div>
              <div class="stat-label">Uptime</div>
            </div>
            <div class="stat">
              <div class="stat-value">${app.bandwidth}</div>
              <div class="stat-label">Shared</div>
            </div>
            <div class="stat">
              <div class="stat-value">${app.pid || '—'}</div>
              <div class="stat-label">PID</div>
            </div>
          </div>
          ${app.error ? `<div class="error">⚠️ ${app.error}</div>` : ''}
        </div>`;
    });
    document.getElementById('total-earnings').textContent = '$' + total.toFixed(4);
  } catch(e) { console.error(e); }
}
refresh();
setInterval(refresh, 30000);
</script>
</body>
</html>"""


class Dashboard:
    def __init__(self, manager):
        self.manager = manager
    
    async def handle_index(self, request):
        return web.Response(text=DASHBOARD_HTML, content_type="text/html")
    
    async def handle_status(self, request):
        status = self.manager.get_all_status()
        return web.json_response(status)
    
    async def handle_start(self, request):
        app = request.match_info.get("app")
        if app and app in self.manager.runners:
            ok = self.manager.runners[app].start()
            return web.json_response({"ok": ok, "app": app})
        elif not app:
            results = self.manager.start_all()
            return web.json_response({"ok": True, "results": results})
        return web.json_response({"ok": False, "error": "App not found"}, status=404)
    
    async def handle_stop(self, request):
        app = request.match_info.get("app")
        if app and app in self.manager.runners:
            self.manager.runners[app].stop()
            return web.json_response({"ok": True, "app": app})
        elif not app:
            self.manager.stop_all()
            return web.json_response({"ok": True})
        return web.json_response({"ok": False, "error": "App not found"}, status=404)


def run_dashboard(manager, port=8080):
    dashboard = Dashboard(manager)
    app = web.Application()
    app.router.add_get("/", dashboard.handle_index)
    app.router.add_get("/api/status", dashboard.handle_status)
    app.router.add_post("/api/start/{app}", dashboard.handle_start)
    app.router.add_post("/api/start", dashboard.handle_start)
    app.router.add_post("/api/stop/{app}", dashboard.handle_stop)
    app.router.add_post("/api/stop", dashboard.handle_stop)
    
    print(f"🌐 Dashboard: http://localhost:{port}")
    web.run_app(app, port=port, print=None)
