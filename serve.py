#!/usr/bin/env python3
"""
Servidor local — El Oráculo de Edunuel
Sirve el sitio y la API /api/horoscopo (misma ruta que en producción).

Uso:
  python3 serve.py
  Abre http://127.0.0.1:8080/admin.html
"""
from __future__ import annotations

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(ROOT, "data", "horoscopo.json")
ADMIN_PIN = os.environ.get("ADMIN_PIN", "edunuel2026")
PORT = int(os.environ.get("PORT", "8080"))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_OPTIONS(self):
        if urlparse(self.path).path == "/api/horoscopo":
            self.send_response(204)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Admin-Pin")
            self.end_headers()
            return
        self.send_error(404)

    def do_GET(self):
        if urlparse(self.path).path == "/api/horoscopo":
            self._send_json_file()
            return
        return super().do_GET()

    def do_POST(self):
        if urlparse(self.path).path != "/api/horoscopo":
            self.send_error(404)
            return

        if self.headers.get("X-Admin-Pin", "") != ADMIN_PIN:
            self._json_response(403, {"error": "PIN incorrecto"})
            return

        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(data.get("signs"), list) or not data["signs"]:
                raise ValueError("JSON inválido: falta la lista de signos")
            os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
            with open(JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
            self._json_response(200, {"ok": True, "updated": data.get("updated")})
        except (json.JSONDecodeError, ValueError) as exc:
            self._json_response(400, {"error": str(exc)})

    def _send_json_file(self):
        try:
            with open(JSON_PATH, encoding="utf-8") as f:
                payload = f.read().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(payload)
        except FileNotFoundError:
            self._json_response(404, {"error": "Horóscopo no disponible"})

    def _json_response(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)


def main():
    os.chdir(ROOT)
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Sitio:  http://127.0.0.1:{PORT}/")
    print(f"Admin:  http://127.0.0.1:{PORT}/admin.html")
    print("Publicar horóscopo → botón «Publicar cambios»")
    print("Ctrl+C para detener")
    server.serve_forever()


if __name__ == "__main__":
    main()
