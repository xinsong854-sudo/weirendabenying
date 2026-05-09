#!/usr/bin/env python3
"""捏Ta图库上传 - 一键启动，浏览器打开 localhost:9876 即用"""
import json, base64, os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

API = "https://api.talesofai.cn"
PORT = 9876

HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>捏Ta 图库上传</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);min-height:100vh;color:#eaeaea;padding:20px}
.container{max-width:500px;margin:0 auto}
h1{text-align:center;font-size:22px;margin:20px 0 4px}
.sub{text-align:center;color:#888;font-size:13px;margin-bottom:20px}
.card{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);border-radius:16px;padding:20px;margin-bottom:16px;backdrop-filter:blur(10px)}
.card-label{font-size:13px;color:#999;margin-bottom:8px;display:block}
input[type=password]{width:100%;padding:12px 14px;border-radius:10px;border:1px solid rgba(255,255,255,.15);background:rgba(0,0,0,.3);color:#fff;font-size:14px;outline:none}
input:focus{border-color:#a78bfa}
.drop-zone{border:2px dashed rgba(255,255,255,.2);border-radius:14px;padding:36px 20px;text-align:center;cursor:pointer;transition:.2s}
.drop-zone:hover{border-color:#a78bfa;background:rgba(167,139,250,.08)}
.drop-zone.has-file{border-style:solid;border-color:#34d399}
#preview{max-width:160px;max-height:160px;border-radius:10px;margin-top:12px;display:none}
.btn{width:100%;padding:14px;border:0;border-radius:12px;font-size:15px;font-weight:700;cursor:pointer;background:linear-gradient(135deg,#a78bfa,#7c3aed);color:#fff;transition:.2s}
.btn:hover{opacity:.9}
.btn:disabled{opacity:.4;cursor:not-allowed}
.status{font-size:13px;margin-top:12px;text-align:center}
.status.ok{color:#34d399}
.status.err{color:#ef4444}
.result{margin-top:12px}
.result a{display:block;padding:12px;border-radius:10px;background:rgba(52,211,153,.12);color:#34d399;font-size:12px;word-break:break-all;text-decoration:none}
.result img{max-width:100%;border-radius:10px;margin-top:8px;display:none}
</style>
</head>
<body>
<div class="container">
<h1>捏Ta 图库上传</h1>
<p class="sub">选择图片，粘贴 Token，一键上传</p>
<div class="card">
<label class="card-label">Token</label>
<input type="password" id="token" placeholder="粘贴 NIETA_ACCESS_TOKEN">
</div>
<div class="card">
<label class="card-label">选择图片</label>
<div class="drop-zone" id="dropZone"><div>点击或拖拽图片</div><small style="color:#666">PNG / JPG / WebP</small></div>
<img id="preview">
<input type="file" id="fileInput" accept="image/*" style="display:none">
</div>
<button class="btn" id="uploadBtn" disabled>上传到图库</button>
<div class="status" id="status"></div>
<div class="result" id="result"></div>
</div>
<script>
var tokenEl=document.getElementById("token"),dropZone=document.getElementById("dropZone"),
fileInput=document.getElementById("fileInput"),preview=document.getElementById("preview"),
uploadBtn=document.getElementById("uploadBtn"),statusEl=document.getElementById("status"),
resultEl=document.getElementById("result"),selectedFile=null;
var saved=localStorage.getItem("nieta_upload_token");if(saved)tokenEl.value=saved;
tokenEl.addEventListener("input",function(){localStorage.setItem("nieta_upload_token",tokenEl.value.trim());checkReady()});
dropZone.addEventListener("click",function(){fileInput.click()});
dropZone.addEventListener("dragover",function(e){e.preventDefault();dropZone.classList.add("drag")});
dropZone.addEventListener("dragleave",function(){dropZone.classList.remove("drag")});
dropZone.addEventListener("drop",function(e){e.preventDefault();dropZone.classList.remove("drag");var f=e.dataTransfer.files[0];if(f&&f.type.startsWith("image/"))handleFile(f)});
fileInput.addEventListener("change",function(){var f=fileInput.files[0];if(f)handleFile(f)});
function handleFile(f){selectedFile=f;dropZone.classList.add("has-file");dropZone.querySelector("div").textContent=f.name+" ("+(f.size/1024).toFixed(0)+"KB)";var r=new FileReader();r.onload=function(e){preview.src=e.target.result;preview.style.display="block"};r.readAsDataURL(f);checkReady()}
function checkReady(){uploadBtn.disabled=!(tokenEl.value.trim()&&selectedFile)}
uploadBtn.addEventListener("click",async function(){var token=tokenEl.value.trim();if(!token||!selectedFile)return;uploadBtn.disabled=true;uploadBtn.textContent="上传中...";statusEl.textContent="";statusEl.className="status";resultEl.innerHTML="";
try{var base64=await new Promise(function(r){var reader=new FileReader();reader.onload=function(){r(reader.result.split(",")[1])};reader.readAsDataURL(selectedFile)});
var suffix=selectedFile.name.split(".").pop()||"png";
statusEl.textContent="上传中...";statusEl.className="status";
var resp=await fetch("/upload",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token:token,suffix:suffix,file:base64})});
var data=await resp.json();
if(data.ok){statusEl.textContent="上传成功！";statusEl.className="status ok";resultEl.innerHTML='<a href="'+data.view_url+'" target="_blank">'+data.view_url+'</a><img src="'+data.view_url+'" onload="this.style.display=\'block\'" onerror="this.remove()">'}else{throw new Error(data.error)}}
catch(err){statusEl.textContent=err.message;statusEl.className="status err"}
finally{uploadBtn.disabled=false;uploadBtn.textContent="上传到图库"}});
</script>
</body>
</html>'''


class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

    def do_POST(self):
        if self.path != "/upload":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        token = body.get("token", "")
        suffix = body.get("suffix", "png")
        file_b64 = body.get("file", "")

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        try:
            r = requests.get(f"{API}/v1/oss/upload-signed-url?suffix={suffix}",
                headers={"x-token": token}, timeout=10)
            r.raise_for_status()
            sign = r.json()

            r2 = requests.put(sign["upload_url"], data=base64.b64decode(file_b64), timeout=30)
            if r2.status_code != 200:
                raise Exception(f"OSS {r2.status_code}")

            r3 = requests.post(f"{API}/v1/artifact/picture",
                json={"url": sign["view_url"]},
                headers={"x-token": token}, timeout=10)
            r3.raise_for_status()

            result = {"ok": True, "view_url": sign["view_url"], "artifact": r3.json()}
        except Exception as e:
            result = {"ok": False, "error": str(e)}

        self.wfile.write(json.dumps(result, ensure_ascii=False).encode())

    def log_message(self, fmt, *args):
        pass


if __name__ == "__main__":
    import webbrowser, threading
    print(f"\n  捏Ta 图库上传: http://localhost:{PORT}\n")
    threading.Timer(0.8, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
    HTTPServer(("0.0.0.0", PORT), Server).serve_forever()
