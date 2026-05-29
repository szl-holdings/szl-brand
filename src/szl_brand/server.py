"""Local development server for live brand asset preview.

Serves generated assets with a gallery UI, enabling rapid iteration
on social previews and anatomy figures without leaving the terminal.
"""

from __future__ import annotations

import http.server
import json
import socketserver
from pathlib import Path
from urllib.parse import unquote

GALLERY_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>SZL Brand — Asset Gallery</title>
<style>
  :root {
    --void: #0A0A0F;
    --abyss: #12121A;
    --obsidian: #1A1A24;
    --accent: #805AD5;
    --accent-bright: #A882FF;
    --text-primary: #F0F0F0;
    --text-secondary: #B4B4BE;
    --text-muted: #6E6E78;
    --card-border: rgba(255,255,255,0.06);
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: var(--void);
    color: var(--text-primary);
    min-height: 100vh;
    padding: 2rem;
  }
  header {
    display: flex; align-items: center; gap: 1rem;
    margin-bottom: 2rem; padding-bottom: 1rem;
    border-bottom: 1px solid var(--card-border);
  }
  header h1 { font-size: 1.5rem; font-weight: 700; }
  header .tag {
    background: rgba(128,90,213,0.15);
    border: 1px solid var(--accent);
    color: var(--accent-bright);
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 1.5rem;
  }
  .card {
    background: var(--abyss);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.2s;
  }
  .card:hover {
    border-color: var(--accent);
    transform: translateY(-2px);
  }
  .card img {
    width: 100%;
    height: auto;
    display: block;
  }
  .card-meta {
    padding: 0.75rem 1rem;
    display: flex; justify-content: space-between; align-items: center;
  }
  .card-name { font-size: 0.875rem; color: var(--text-secondary); font-family: monospace; }
  .card-size { font-size: 0.75rem; color: var(--text-muted); }
  .empty {
    text-align: center; padding: 4rem;
    color: var(--text-muted); font-size: 1.1rem;
  }
</style>
</head>
<body>
<header>
  <h1>SZL Brand</h1>
  <span class="tag">Asset Gallery</span>
</header>
<div class="grid" id="gallery"></div>
<script>
fetch('/api/assets')
  .then(r => r.json())
  .then(assets => {
    const grid = document.getElementById('gallery');
    if (!assets.length) {
      grid.innerHTML = '<div class="empty">No assets found. Run <code>szl-brand generate</code> first.</div>';
      return;
    }
    assets.forEach(a => {
      const card = document.createElement('div');
      card.className = 'card';
      card.innerHTML = `
        <img src="/asset/${encodeURIComponent(a.path)}" alt="${a.name}" loading="lazy" />
        <div class="card-meta">
          <span class="card-name">${a.name}</span>
          <span class="card-size">${(a.size / 1024).toFixed(1)} KB</span>
        </div>`;
      grid.appendChild(card);
    });
  });
</script>
</body>
</html>"""


class AssetHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler for the asset gallery."""

    asset_dirs: list[Path] = []

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self._serve_html(GALLERY_HTML)
        elif self.path == "/api/assets":
            self._serve_asset_list()
        elif self.path.startswith("/asset/"):
            self._serve_asset(self.path[7:])
        else:
            self.send_error(404)

    def _serve_html(self, content: str):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(content.encode())

    def _serve_asset_list(self):
        assets = []
        for d in self.asset_dirs:
            if d.exists():
                for f in sorted(d.rglob("*")):
                    if f.is_file() and f.suffix.lower() in {
                        ".png",
                        ".jpg",
                        ".svg",
                        ".webp",
                        ".pdf",
                    }:
                        assets.append(
                            {
                                "name": f.name,
                                "path": str(f),
                                "size": f.stat().st_size,
                            }
                        )
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(assets).encode())

    def _serve_asset(self, path: str):
        path = unquote(path)
        file_path = Path(path)
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404)
            return
        content_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml",
            ".webp": "image/webp",
            ".pdf": "application/pdf",
        }
        ct = content_types.get(file_path.suffix.lower(), "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(file_path.stat().st_size))
        self.end_headers()
        with open(file_path, "rb") as f:
            self.wfile.write(f.read())

    def log_message(self, format, *args):
        pass


def serve(port: int = 8742, asset_dirs: list[Path] | None = None) -> None:
    """Start the asset gallery server."""
    if asset_dirs:
        AssetHandler.asset_dirs = asset_dirs
    else:
        AssetHandler.asset_dirs = [
            Path("social-previews"),
            Path("/tmp/social-previews"),
        ]

    with socketserver.TCPServer(("", port), AssetHandler) as httpd:
        print("\n  ┌─────────────────────────────────────────┐")
        print("  │  SZL Brand Gallery                       │")
        print(f"  │  http://localhost:{port}                  │")
        print("  │  Press Ctrl+C to stop                    │")
        print("  └─────────────────────────────────────────┘\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Server stopped.")
