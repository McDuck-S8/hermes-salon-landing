#!/usr/bin/env python3
"""Simple HTTP server for Hermes Dashboard."""
import http.server
import socketserver
import os
import sys

PORT = 8765
DASHBOARD_DIR = r"D:\Portable_Soft\hermes\dashboard_data"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def log_message(self, format, *args):
        # Suppress log messages
        pass

if __name__ == "__main__":
    os.chdir(DASHBOARD_DIR)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Hermes Dashboard running at http://localhost:{PORT}")
        print(f"Serving from: {DASHBOARD_DIR}")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down...")
            httpd.shutdown()