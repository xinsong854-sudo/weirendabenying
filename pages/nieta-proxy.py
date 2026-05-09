#!/usr/bin/env python3
"""捏Ta图库上传代理 - 绕过浏览器 CORS 限制"""
import json, sys, os, base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

API = "https://api.talesofai.cn"
PORT = 9876

class Proxy(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        data = json.loads(body)
        token = data.get("token", "")
        suffix = data.get("suffix", "png")
        file_b64 = data.get("file", "")

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        try:
            # Step 1: 获取签名 URL
            r = requests.get(f"{API}/v1/oss/upload-signed-url?suffix={suffix}",
                headers={"x-token": token})
            r.raise_for_status()
            sign = r.json()
            upload_url = sign["upload_url"]
            view_url = sign["view_url"]

            # Step 2: 上传到 OSS（不带 Content-Type，否则签名校验失败）
            file_bytes = base64.b64decode(file_b64)
            r2 = requests.put(upload_url, data=file_bytes)
            if r2.status_code != 200:
                raise Exception(f"OSS返回 {r2.status_code}: {r2.text[:200]}")

            # Step 3: 注册入库
            r3 = requests.post(f"{API}/v1/artifact/picture",
                json={"url": view_url},
                headers={"x-token": token})
            r3.raise_for_status()
            artifact = r3.json()

            result = {"ok": True, "view_url": view_url, "artifact": artifact}
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode())

        except Exception as e:
            result = {"ok": False, "error": str(e)}
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode())

    def log_message(self, fmt, *args):
        msg = args[0] if args else ""
        print(f"[proxy] {msg}", flush=True)

if __name__ == "__main__":
    print(f"捏Ta 上传代理启动: http://localhost:{PORT}")
    print("保持此窗口运行，然后在浏览器中打开 upload 页面")
    HTTPServer(("0.0.0.0", PORT), Proxy).serve_forever()
