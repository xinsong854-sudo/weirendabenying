#!/usr/bin/env python3
"""
伪人大本营 - SCP 档案库
捏Ta 用户登录后浏览世界观、伪人档案、人类档案等
"""
import json, os, base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

API = "https://api.talesofai.cn"
PORT = 9876

# 加载数据
with open('/workspace/pages/pseudo-human-data.json', 'r', encoding='utf-8') as f:
    DATA = json.load(f)

LORE_CATEGORIES = list(DATA['lore'].keys())

HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>伪人大本营 - SCP档案库</title>
<style>
:root{--bg:#f5f4f0;--card:#fff;--border:#e0dcd5;--text:#2c2c2c;--accent:#8b0000;--accent2:#c41e3a;--muted:#78766d;--tag-bg:#f0ede6}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Georgia,"Times New Roman",serif;background:var(--bg);color:var(--text);min-height:100vh;line-height:1.6}
.page{padding:20px}
.container{max-width:900px;margin:0 auto}

/* 登录页 */
.login-box{max-width:400px;margin:80px auto;background:var(--card);border:1px solid var(--border);padding:36px;text-align:center}
.login-box h1{font-size:24px;letter-spacing:4px;color:var(--accent);margin-bottom:6px}
.login-box .sub{color:var(--muted);font-size:12px;margin-bottom:28px}
.login-box input{width:100%;padding:10px 14px;border:1px solid var(--border);font-size:13px;font-family:monospace;outline:none;background:var(--bg)}
.login-box input:focus{border-color:var(--accent)}
.login-box .btn{width:100%;padding:10px;margin-top:14px;background:var(--accent);color:#fff;border:0;font-size:13px;letter-spacing:3px;cursor:pointer;text-transform:uppercase}
.login-box .btn:hover{background:var(--accent2)}
.msg{font-size:12px;margin-top:10px}

/* 顶部栏 */
.topbar{background:var(--card);border-bottom:1px solid var(--border);padding:12px 20px;display:flex;justify-content:space-between;align-items:center}
.topbar .logo{font-weight:700;letter-spacing:3px;color:var(--accent);font-size:16px}
.topbar .user{display:flex;align-items:center;gap:10px;font-size:13px}
.topbar img{width:28px;height:28px;border-radius:50%}
.topbar a{color:var(--accent);cursor:pointer;text-decoration:none;font-size:12px}

/* 首页 */
.hero{text-align:center;padding:48px 20px 32px}
.hero h1{font-size:28px;letter-spacing:6px;color:var(--accent);margin-bottom:8px}
.hero .tagline{color:var(--muted);font-size:14px;letter-spacing:2px;margin-bottom:24px}
.hero .stats{display:flex;justify-content:center;gap:32px;font-size:12px;color:var(--muted)}
.hero .stats span{color:var(--accent);font-weight:700;font-size:16px}

/* 分类卡片 */
.section-title{font-size:14px;letter-spacing:3px;color:var(--accent);margin:28px 0 14px;padding-bottom:6px;border-bottom:1px solid var(--border)}
.category-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin-bottom:24px}
.cat-card{background:var(--card);border:1px solid var(--border);padding:16px;cursor:pointer;transition:all .15s}
.cat-card:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:0 2px 8px rgba(0,0,0,.06)}
.cat-card .name{font-size:14px;font-weight:700;color:var(--text)}
.cat-card .count{font-size:11px;color:var(--muted);margin-top:4px}

/* 详情页 */
.back-btn{font-size:12px;color:var(--accent);cursor:pointer;letter-spacing:2px;margin-bottom:20px;display:inline-block}
.entry-list{}
.entry{background:var(--card);border:1px solid var(--border);padding:20px;margin-bottom:12px}
.entry .title{font-size:15px;font-weight:700;color:var(--accent);margin-bottom:8px}
.entry .content{font-size:13px;color:var(--text);white-space:pre-line;line-height:1.8}
.entry .meta{font-size:11px;color:var(--muted);margin-top:8px}
.entry .classification{display:inline-block;background:var(--tag-bg);padding:2px 8px;font-size:10px;letter-spacing:1px;margin-right:6px;text-transform:uppercase}

.search-box{width:100%;padding:10px 14px;border:1px solid var(--border);font-size:13px;margin-bottom:20px;outline:none;background:var(--card)}
.search-box:focus{border-color:var(--accent)}

.hidden{display:none!important}
</style>
</head>
<body>
<div class="page">
<!-- 登录 -->
<div id="loginPage" class="login-box">
  <h1>THE PSEUDO-HUMAN ARCHIVES</h1>
  <div class="sub">伪人大本营 · SCP 档案库</div>
  <input type="password" id="tokenInput" placeholder="输入 NIETA_ACCESS_TOKEN">
  <button class="btn" id="loginBtn">验证身份</button>
  <div class="msg" id="loginMsg"></div>
</div>

<!-- 主界面 -->
<div id="mainPage" class="hidden">
  <div class="topbar">
    <div class="logo">PSEUDO-HUMAN ARCHIVES</div>
    <div class="user">
      <img id="userAvatar" src="">
      <span id="userName"></span>
      <a onclick="logout()">注销</a>
    </div>
  </div>
  <div class="container">
    <div class="hero">
      <h1 id="archiveTitle"></h1>
      <div class="tagline" id="archiveTagline"></div>
      <div class="stats">
        <div>热度 <span id="statHeat"></span></div>
        <div>订阅 <span id="statSubs"></span></div>
        <div>条目 <span id="statLore"></span></div>
      </div>
    </div>

    <!-- 分类列表 -->
    <div id="categoryView">
      <div class="section-title">档案分类</div>
      <div class="category-grid" id="categoryGrid"></div>
    </div>

    <!-- 详情视图 -->
    <div id="detailView" class="hidden">
      <div class="back-btn" onclick="showCategories()">← 返回档案分类</div>
      <input class="search-box" id="searchInput" placeholder="搜索档案条目..." oninput="filterEntries()">
      <div class="entry-list" id="entryList"></div>
    </div>
  </div>
</div>
</div>

<script>
const API = "/api";
let token = "";
let allData = null;
let currentCategory = "";

document.getElementById("loginBtn").addEventListener("click", async () => {
  token = document.getElementById("tokenInput").value.trim();
  if (!token) return;
  const msg = document.getElementById("loginMsg");
  msg.textContent = "验证中...";
  try {
    const r = await fetch(API + "/verify", { headers: { "x-token": token } });
    const user = await r.json();
    if (!r.ok || !user.uuid) throw new Error("令牌无效");
    document.getElementById("userName").textContent = user.nick_name || user.name;
    document.getElementById("userAvatar").src = user.avatar_url || "";
    document.getElementById("loginPage").classList.add("hidden");
    document.getElementById("mainPage").classList.remove("hidden");
    loadArchive();
  } catch(e) {
    msg.textContent = "❌ " + (e.message || "登录失败");
  }
});

document.getElementById("tokenInput").addEventListener("keydown", e => {
  if (e.key === "Enter") document.getElementById("loginBtn").click();
});

async function loadArchive() {
  const r = await fetch(API + "/archive");
  allData = await r.json();
  document.getElementById("archiveTitle").textContent = allData.name;
  document.getElementById("archiveTagline").textContent = allData.tagline;
  document.getElementById("statHeat").textContent = (allData.stats.heat / 10000).toFixed(0) + "万";
  document.getElementById("statSubs").textContent = allData.stats.subscribers;
  document.getElementById("statLore").textContent = allData.stats.lore_count;
  showCategories();
}

function showCategories() {
  document.getElementById("categoryView").classList.remove("hidden");
  document.getElementById("detailView").classList.add("hidden");
  const grid = document.getElementById("categoryGrid");
  grid.innerHTML = "";
  if (!allData) return;
  for (let [cat, entries] of Object.entries(allData.lore)) {
    const card = document.createElement("div");
    card.className = "cat-card";
    card.innerHTML = `<div class="name">${cat}</div><div class="count">${entries.length} 条档案</div>`;
    card.addEventListener("click", () => showCategory(cat));
    grid.appendChild(card);
  }
}

function showCategory(cat) {
  currentCategory = cat;
  document.getElementById("categoryView").classList.add("hidden");
  document.getElementById("detailView").classList.remove("hidden");
  document.getElementById("searchInput").value = "";
  renderEntries(allData.lore[cat] || []);
}

function renderEntries(entries) {
  const list = document.getElementById("entryList");
  list.innerHTML = "";
  entries.forEach((e, i) => {
    const div = document.createElement("div");
    div.className = "entry";
    const cls = getClassification(e.description);
    div.innerHTML = `
      <div class="title">${cls} ${e.name}</div>
      <div class="content">${escapeHtml(e.description)}</div>
    `;
    list.appendChild(div);
  });
}

function getClassification(desc) {
  if (!desc) return "";
  if (desc.includes("🟥")) return '<span class="classification">🟥 HAZARD</span>';
  if (desc.includes("🟧")) return '<span class="classification">🟧 DANGER</span>';
  if (desc.includes("🟨")) return '<span class="classification">🟨 CAUTION</span>';
  if (desc.includes("🟩")) return '<span class="classification">🟩 SAFE</span>';
  if (desc.includes("⬜")) return '<span class="classification">⬜ REALITY</span>';
  return "";
}

function filterEntries() {
  const q = document.getElementById("searchInput").value.toLowerCase();
  const entries = allData.lore[currentCategory] || [];
  if (!q) { renderEntries(entries); return; }
  renderEntries(entries.filter(e =>
    e.name.toLowerCase().includes(q) || e.description.toLowerCase().includes(q)
  ));
}

function escapeHtml(s) { const d=document.createElement("div");d.textContent=s;return d.innerHTML; }
function logout() {
  token = ""; allData = null;
  document.getElementById("loginPage").classList.remove("hidden");
  document.getElementById("mainPage").classList.add("hidden");
}
</script>
</body>
</html>"""

class Server(BaseHTTPRequestHandler):
    def _json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode())
            return

        if self.path == "/api/archive":
            self._json(DATA)
            return

        self.send_error(404)

    def do_POST(self):
        if self.path == "/api/verify":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length)) if length > 0 else {}
            token = self.headers.get("x-token", body.get("token", ""))
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10)
                r.raise_for_status()
                self._json(r.json())
            except Exception as e:
                self._json({"error": str(e)}, 401)
            return

        self.send_error(404)

    def log_message(self, f, *a): pass


if __name__ == "__main__":
    import webbrowser, threading
    print(f"\n  伪人大本营 SCP 档案库: http://localhost:{PORT}\n")
    threading.Timer(0.8, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
    HTTPServer(("0.0.0.0", PORT), Server).serve_forever()
