#!/usr/bin/env python3
"""
伪人大本营 — 捏Ta 登录 + 档案库 + 成员系统
python3 server.py  →  localhost:3000
"""
import json, os, time, sqlite3, hashlib, mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests

API = "https://api.talesofai.cn"
PORT = 3000
DB = os.path.join(os.path.dirname(__file__) or ".", "pseudo_human.db")
BASE_DIR = os.path.dirname(__file__) or "."
DATA = os.path.join(BASE_DIR, "pseudo-human-data.json")
DIST_DIR = os.path.join(BASE_DIR, "dist")

# ═══════════ 数据库 ═══════════
def get_db():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    return db

def init_db():
    db = get_db()
    # 成员表
    db.execute("""CREATE TABLE IF NOT EXISTS members(
        uuid TEXT PRIMARY KEY, name TEXT, avatar TEXT, role TEXT DEFAULT 'member', title TEXT DEFAULT '', avatar_frame TEXT DEFAULT 'none', signature TEXT DEFAULT '',
        online INTEGER DEFAULT 0, last_seen INTEGER, joined_at INTEGER DEFAULT (strftime('%s','now'))
    )""")
    # 兼容旧库：已有 members 表时补充 title 字段
    try:
        db.execute("ALTER TABLE members ADD COLUMN title TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        db.execute("ALTER TABLE members ADD COLUMN avatar_frame TEXT DEFAULT 'none'")
    except sqlite3.OperationalError:
        pass
    try:
        db.execute("ALTER TABLE members ADD COLUMN signature TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    # 评论表
    db.execute("""CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT, entry_uuid TEXT NOT NULL,
        user_uuid TEXT NOT NULL, user_name TEXT, user_avatar TEXT,
        content TEXT NOT NULL, created_at INTEGER DEFAULT (strftime('%s','now'))
    )""")
    # 论坛发言表：真实后端存储，所有用户按频道同步可见
    db.execute("""CREATE TABLE IF NOT EXISTS forum_posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        channel TEXT NOT NULL,
        user_uuid TEXT NOT NULL,
        user_name TEXT,
        user_avatar TEXT,
        content TEXT NOT NULL,
        images_json TEXT DEFAULT '[]',
        revoked INTEGER DEFAULT 0,
        revoked_by TEXT,
        created_at INTEGER DEFAULT (strftime('%s','now'))
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS forum_channels(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        name TEXT NOT NULL UNIQUE,
        description TEXT DEFAULT '',
        created_by TEXT,
        created_at INTEGER DEFAULT (strftime('%s','now'))
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS activities(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        status TEXT DEFAULT '进行中',
        description TEXT DEFAULT '',
        created_by TEXT,
        created_at INTEGER DEFAULT (strftime('%s','now'))
    )""")
    db.execute("""CREATE TABLE IF NOT EXISTS wiki_submissions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target TEXT NOT NULL,
        submit_type TEXT NOT NULL,
        content TEXT NOT NULL,
        images_json TEXT DEFAULT '[]',
        user_uuid TEXT,
        user_name TEXT,
        status TEXT DEFAULT 'pending',
        reviewed_by TEXT DEFAULT '',
        reviewed_at INTEGER,
        review_note TEXT DEFAULT '',
        created_at INTEGER DEFAULT (strftime('%s','now'))
    )""")
    for sql in (
        "ALTER TABLE wiki_submissions ADD COLUMN reviewed_by TEXT DEFAULT ''",
        "ALTER TABLE wiki_submissions ADD COLUMN reviewed_at INTEGER",
        "ALTER TABLE wiki_submissions ADD COLUMN review_note TEXT DEFAULT ''",
    ):
        try:
            db.execute(sql)
        except sqlite3.OperationalError:
            pass
    db.execute("""CREATE TABLE IF NOT EXISTS private_messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_uuid TEXT NOT NULL,
        to_uuid TEXT NOT NULL,
        from_name TEXT,
        from_avatar TEXT,
        content TEXT NOT NULL,
        created_at INTEGER DEFAULT (strftime('%s','now'))
    )""")
    # Wiki 词条表：用于后端检索，避免数据变大后全部压给前端搜索
    db.execute("""CREATE TABLE IF NOT EXISTS entries(
        uuid TEXT PRIMARY KEY,
        category TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        updated_at INTEGER DEFAULT (strftime('%s','now'))
    )""")
    db.execute("CREATE INDEX IF NOT EXISTS idx_c_entry ON comments(entry_uuid)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_c_time ON comments(created_at DESC)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_entries_category ON entries(category)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_entries_name ON entries(name)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_forum_channel_time ON forum_posts(channel, created_at DESC)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_forum_channels_time ON forum_channels(created_at DESC)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_activities_time ON activities(created_at DESC)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_wiki_submissions_time ON wiki_submissions(created_at DESC)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_private_pair_time ON private_messages(from_uuid, to_uuid, created_at DESC)")
    
    # 初始化管理员
    admins = [
        ("b91c3751186d4f649576686168347900","安诺涅","https://oss.talesofai.cn/sts/b91c3751186d4f649576686168347900/6440132a-feb9-4fd2-9a44-5ff3440928e2.jpg","chief"),
        ("33d2a9f8e07b4082889974553ddee0b2","非常_","https://oss.talesofai.cn/sts/33d2a9f8e07b4082889974553ddee0b2/951d632d-b297-4fe5-ad5f-673ee9716fa6.jpeg","deputy"),
        ("065c51c544ce46b691ba89ac9df6c86d","蓝丞","https://oss.talesofai.cn/sts/065c51c544ce46b691ba89ac9df6c86d/3ebe1701-f1ad-4926-8b94-df898ca5fdb5.jpg","admin"),
        ("17049dd3bb9448f2adcdccfb81c319af","化而为","https://oss.talesofai.cn/sts/17049dd3bb9448f2adcdccfb81c319af/86e81415-df73-4e1c-9b44-4e0e9e4ea265.jpeg","admin"),
        ("179e3837a3044a369c627a2139492886","道阻且长","https://oss.talesofai.cn/sts/179e3837a3044a369c627a2139492886/cb633deb-5144-43a9-9a7d-b4ae35f22756.jpeg","admin"),
        ("359af92e1e4e48ea90d85005d8d9bfbf","桃花不换酒","https://oss.talesofai.cn/sts/359af92e1e4e48ea90d85005d8d9bfbf/7725c644-b7d5-4ec8-b52a-1f07cd7ddb4d.jpeg","admin"),
        ("785d16cc3595466481569ca264c6b927","西西","https://oss.talesofai.cn/sts/785d16cc3595466481569ca264c6b927/40dd6cc8-8da2-4268-9eed-0a8688e575ab.jpeg","admin"),
        ("9ffcad2ea18642879d90626753337c34","秋雨微澜","https://oss.talesofai.cn/sts/9ffcad2ea18642879d90626753337c34/aeb73add-c386-443e-8850-eae4f0de69f3.jpeg","admin"),
        ("bd475d65674c434b87f8ea2fc0a2f5aa","海姆姆","https://oss.talesofai.cn/sts/bd475d65674c434b87f8ea2fc0a2f5aa/ac37c4cb-4491-44f5-b3af-f287a8199ca7.jpeg","admin"),
        ("ec8c80fe3a71450ab3e8964375631f65","AlcheMist","https://oss.talesofai.cn/sts/ec8c80fe3a71450ab3e8964375631f65/917cb630-6300-4bbe-9737-31e74678d52b.jpeg","admin"),
        ("fbbee96a06624b7589549466991cc15a","鄢滙","https://oss.talesofai.cn/sts/fbbee96a06624b7589549466991cc15a/41a8f038-f3fb-4bc7-a494-9f3307a893a0.png","admin"),
    ]
    for uuid, name, avatar, role in admins:
        db.execute("INSERT OR IGNORE INTO members(uuid,name,avatar,role) VALUES(?,?,?,?)", (uuid, name, avatar, role))
    db.commit()
    db.close()

init_db()

# ═══════════ 加载档案 ═══════════
with open(DATA, "r", encoding="utf-8") as f:
    ARCHIVE = json.load(f)

ALL_ENTRIES = []
for cat, entries in ARCHIVE["lore"].items():
    for e in entries:
        ALL_ENTRIES.append({**e, "category": cat})

ALL_JSON = json.dumps(ALL_ENTRIES, ensure_ascii=False)
ARCHIVE_JSON = json.dumps(ARCHIVE, ensure_ascii=False)


def rebuild_archive_cache():
    global ALL_ENTRIES, ALL_JSON, ARCHIVE_JSON
    ALL_ENTRIES = []
    for cat, entries in ARCHIVE["lore"].items():
        for e in entries:
            ALL_ENTRIES.append({**e, "category": cat})
    ALL_JSON = json.dumps(ALL_ENTRIES, ensure_ascii=False)
    ARCHIVE_JSON = json.dumps(ARCHIVE, ensure_ascii=False)

def persist_archive():
    ARCHIVE["stats"]["lore_count"] = sum(len(v) for v in ARCHIVE.get("lore", {}).values())
    tmp = DATA + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(ARCHIVE, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA)
    rebuild_archive_cache()
    sync_entries_to_db()

def parse_wiki_submission(row):
    try:
        payload = json.loads(row["content"] or "{}")
    except Exception:
        payload = {"content": row["content"] or ""}
    if not isinstance(payload, dict):
        payload = {"content": str(payload)}
    try:
        images = json.loads(row["images_json"] or "[]")
    except Exception:
        images = []
    payload.setdefault("images", images)
    payload.setdefault("category", row["target"])
    payload.setdefault("entry_name", "")
    payload.setdefault("body", payload.get("content", ""))
    return payload

def apply_wiki_submission(row):
    payload = parse_wiki_submission(row)
    typ = row["submit_type"] or payload.get("type") or "新增词条"
    category = str(payload.get("category") or row["target"] or "").strip()[:80]
    entry_name = str(payload.get("entry_name") or "").strip()[:80]
    body = str(payload.get("body") or payload.get("content") or "").strip()
    images = payload.get("images") if isinstance(payload.get("images"), list) else []
    images = [str(x) for x in images if str(x).startswith(("http://", "https://"))][:9]
    if not category:
        raise ValueError("缺少分类名称")
    ARCHIVE.setdefault("lore", {}).setdefault(category, [])
    if typ == "新建分类" and not entry_name:
        if body:
            ARCHIVE["lore"][category].append({"name": category, "description": body + ("\n\n" + "\n".join(images) if images else ""), "uuid": hashlib.md5(f"{category}:{time.time()}".encode()).hexdigest()})
        persist_archive(); return
    if not entry_name:
        raise ValueError("缺少条目名称")
    desc = body
    if images:
        desc = (desc + "\n\n" if desc else "") + "图片：\n" + "\n".join(images)
    entries = ARCHIVE["lore"][category]
    found = None
    for e in entries:
        if str(e.get("name", "")).strip() == entry_name:
            found = e; break
    if found:
        if typ == "修订词条":
            found["description"] = desc
        else:
            old = str(found.get("description", "")).rstrip()
            found["description"] = (old + "\n\n" + desc).strip() if old else desc
    else:
        uid = hashlib.md5(f"{category}:{entry_name}:{time.time()}".encode()).hexdigest()
        entries.append({"name": entry_name, "description": desc, "uuid": uid})
    persist_archive()

def sync_entries_to_db():
    """把 JSON Wiki 同步进 SQLite，供后端参数化搜索使用。"""
    db = get_db()
    now = int(time.time())
    seen = []
    for entry in ALL_ENTRIES:
        uuid = str(entry.get("uuid", "")).strip()
        if not uuid:
            continue
        seen.append(uuid)
        db.execute("""INSERT INTO entries(uuid, category, name, description, updated_at)
                    VALUES(?,?,?,?,?)
                    ON CONFLICT(uuid) DO UPDATE SET
                    category=excluded.category,
                    name=excluded.name,
                    description=excluded.description,
                    updated_at=excluded.updated_at""",
                   (uuid, entry.get("category", ""), entry.get("name", ""), entry.get("description", ""), now))
    if seen:
        placeholders = ",".join("?" for _ in seen)
        db.execute(f"DELETE FROM entries WHERE uuid NOT IN ({placeholders})", seen)
    db.commit()
    db.close()

sync_entries_to_db()

# ═══════════ 前端 ═══════════
PAGE = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>伪人大本营</title>
<style>
:root{{--bg:#f6f5f1;--card:#fff;--border:#e4e0d8;--text:#2b2b2b;--muted:#8a8778;--red:#8b1a1a;--red2:#b91c1c;--gold:#b8860b}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Georgia,"Times New Roman","Songti SC",serif;background:var(--bg);color:var(--text);min-height:100vh;line-height:1.65}}
/* 登录 */
.login-wrap{{display:flex;align-items:center;justify-content:center;min-height:100vh;padding:24px;background:linear-gradient(180deg,#f0ede6,#f6f5f1 50%,#e8e4db)}}
.login-card{{width:100%;max-width:420px;background:var(--card);border:1px solid var(--border);padding:36px 28px;text-align:center;box-shadow:0 2px 12px rgba(0,0,0,.06)}}
.login-card .emblem{{font-size:40px;margin-bottom:6px}}
.login-card h1{{font-size:20px;letter-spacing:6px;color:var(--red);margin-bottom:2px;font-weight:400}}
.login-card .tagline{{color:var(--muted);font-size:12px;margin-bottom:28px;letter-spacing:2px}}
.login-card .field{{display:flex;align-items:center;height:50px;border-bottom:1px solid var(--border);margin-bottom:4px}}
.login-card .prefix{{flex:none;margin-right:12px;color:var(--text);font-size:16px;font-weight:600}}
.login-card input{{min-width:0;flex:1;height:48px;border:0;outline:0;padding:0;background:transparent;color:var(--text);font-size:15px;font-family:inherit}}
.login-card input::placeholder{{color:var(--muted)}}
.login-card .code-btn{{flex:none;min-width:88px;height:32px;margin-left:10px;border:1px solid var(--red);border-radius:16px;background:transparent;color:var(--red);font-size:12px;font-weight:600;cursor:pointer;letter-spacing:1px}}
.login-card .code-btn:disabled{{opacity:.4}}
.login-card .agree{{display:flex;gap:6px;align-items:flex-start;margin-top:16px;color:var(--muted);font-size:11px;line-height:18px;text-align:left}}
.login-card .agree input{{flex:0 0 13px;width:13px;height:13px;min-width:13px;margin:2px 0 0;accent-color:var(--red)}}
.login-card .agree a{{color:var(--red);text-decoration:none;font-weight:600}}
.login-card .submit{{width:100%;height:48px;margin-top:24px;border:0;border-radius:6px;color:#fff;font-size:14px;letter-spacing:4px;font-weight:600;cursor:pointer;background:var(--red);font-family:inherit;text-transform:uppercase}}
.login-card .submit:hover{{background:var(--red2)}}
.login-card .submit:disabled{{opacity:.5}}
.login-card .msg{{margin-top:12px;font-size:12px;min-height:18px}}
.login-card .foot{{margin-top:24px;font-size:11px;color:var(--muted)}}
/* 顶栏 */
.topbar{{background:var(--card);border-bottom:1px solid var(--border);padding:0 20px;display:flex;justify-content:space-between;align-items:center;height:52px;position:sticky;top:0;z-index:20}}
.topbar .logo{{font-weight:700;letter-spacing:3px;color:var(--red);font-size:15px;cursor:pointer}}
.topbar .user-grp{{display:flex;align-items:center;gap:10px;font-size:13px}}
.topbar .user-grp img{{width:30px;height:30px;border-radius:50%;border:1px solid var(--border)}}
.topbar .user-grp button{{background:none;border:1px solid var(--border);color:var(--muted);font-size:11px;padding:4px 10px;cursor:pointer;letter-spacing:1px;font-family:inherit}}
.topbar .user-grp button:hover{{border-color:var(--red);color:var(--red)}}
.badge-chief{{font-size:10px;background:var(--red);color:#fff;padding:2px 8px;border-radius:2px;letter-spacing:2px}}
.badge-deputy{{font-size:10px;background:var(--gold);color:#fff;padding:2px 8px;border-radius:2px;letter-spacing:2px}}
.badge-admin{{font-size:10px;background:var(--gold);color:#fff;padding:2px 8px;border-radius:2px;letter-spacing:2px}}
/* 主内容 */
.main{{max-width:960px;margin:0 auto;padding:0 20px 60px}}
.hero{{text-align:center;padding:44px 0 28px}}
.hero h2{{font-size:26px;letter-spacing:5px;color:var(--red);font-weight:400;margin-bottom:6px}}
.hero .sub{{color:var(--muted);font-size:13px;letter-spacing:3px}}
.hero .stats-row{{display:flex;justify-content:center;gap:36px;margin-top:20px;flex-wrap:wrap}}
.hero .stat{{text-align:center}}
.hero .stat .val{{font-size:20px;font-weight:700;color:var(--red)}}
.hero .stat .lbl{{font-size:11px;color:var(--muted);letter-spacing:2px}}
.search-bar{{position:relative;margin-bottom:24px}}
.search-bar input{{width:100%;padding:12px 16px 12px 40px;border:1px solid var(--border);font-size:14px;outline:none;background:var(--card);font-family:inherit}}
.search-bar input:focus{{border-color:var(--red)}}
.search-bar .sicon{{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:var(--muted)}}
.search-results{{display:none;position:absolute;top:100%;left:0;right:0;background:var(--card);border:1px solid var(--border);border-top:0;max-height:360px;overflow-y:auto;z-index:10;box-shadow:0 2px 12px rgba(0,0,0,.06)}}
.search-results .item{{padding:12px 16px;cursor:pointer;border-bottom:1px solid var(--border);display:flex;justify-content:space-between}}
.search-results .item:hover{{background:var(--bg)}}
.search-results .item .name{{font-size:14px;font-weight:600}}
.search-results .item .cat{{font-size:11px;color:var(--muted)}}
.sec-title{{font-size:12px;letter-spacing:3px;color:var(--muted);text-transform:uppercase;margin:28px 0 14px;padding-bottom:6px;border-bottom:1px solid var(--border)}}
/* 成员 */
.member-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:8px;margin-bottom:24px}}
.member-card{{display:flex;align-items:center;gap:10px;background:var(--card);border:1px solid var(--border);padding:10px 14px;border-radius:4px;transition:all .15s}}
.member-card:hover{{border-color:var(--red)}}
.member-card img{{width:36px;height:36px;border-radius:50%;border:1px solid var(--border)}}
.member-card .m-info{{flex:1;min-width:0}}
.member-card .m-name{{font-size:13px;font-weight:600;display:flex;align-items:center;gap:6px}}
.member-card .m-time{{font-size:10px;color:var(--muted)}}
.m-status{{width:8px;height:8px;border-radius:50%;flex-shrink:0}}
.m-online{{background:#22c55e;box-shadow:0 0 6px rgba(34,197,94,.4)}}
.m-offline{{background:#d4d0c8}}
.m-chief{{border-color:var(--red);background:#fefafa}}
/* 分类 */
.cat-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px}}
.cat-card{{background:var(--card);border:1px solid var(--border);padding:18px 16px;cursor:pointer;transition:all .15s}}
.cat-card:hover{{border-color:var(--red);transform:translateY(-2px);box-shadow:0 4px 16px rgba(139,26,26,.08)}}
.cat-card .name{{font-size:14px;font-weight:600}}
.cat-card .count{{font-size:11px;color:var(--muted);margin-top:4px}}
.breadcrumb{{font-size:12px;color:var(--muted);padding:20px 0 16px;cursor:pointer}}
.breadcrumb b{{color:var(--red)}}
.entry{{background:var(--card);border:1px solid var(--border);padding:24px;margin-bottom:14px}}
.entry .entry-head{{display:flex;align-items:center;gap:10px;margin-bottom:10px;flex-wrap:wrap}}
.entry .entry-title{{font-size:16px;font-weight:700;color:var(--red)}}
.entry .badge{{display:inline-block;padding:3px 10px;font-size:10px;letter-spacing:1px;font-weight:600;border-radius:2px}}
.b-red{{background:#fde8e8;color:var(--red)}}.b-orange{{background:#fef3c7;color:#92400e}}
.b-yellow{{background:#fef9c3;color:#854d0e}}.b-green{{background:#dcfce7;color:#166534}}.b-gray{{background:var(--bg);color:var(--muted)}}
.entry .body{{font-size:13px;line-height:1.9;white-space:pre-line}}
.comments-section{{margin-top:20px;padding-top:20px;border-top:1px solid var(--border)}}
.comments-section h3{{font-size:13px;letter-spacing:2px;color:var(--muted);margin-bottom:16px;text-transform:uppercase}}
.comment{{display:flex;gap:12px;padding:14px 0;border-bottom:1px solid var(--border)}}
.comment img{{width:32px;height:32px;border-radius:50%;border:1px solid var(--border);flex-shrink:0}}
.comment .c-body{{flex:1;min-width:0}}
.comment .c-head{{display:flex;align-items:center;gap:8px;margin-bottom:4px;flex-wrap:wrap}}
.comment .c-name{{font-size:13px;font-weight:600}}
.comment .c-time{{font-size:11px;color:var(--muted)}}
.comment .c-text{{font-size:13px;line-height:1.7;word-break:break-word}}
.comment-form{{display:flex;gap:10px;margin-top:20px;align-items:flex-start}}
.comment-form img{{width:32px;height:32px;border-radius:50%;border:1px solid var(--border);flex-shrink:0}}
.comment-form textarea{{flex:1;min-height:60px;padding:10px 14px;border:1px solid var(--border);font-size:13px;outline:none;resize:vertical;font-family:inherit;background:var(--bg);border-radius:4px}}
.comment-form textarea:focus{{border-color:var(--red)}}
.comment-form button{{padding:8px 20px;background:var(--red);color:#fff;border:0;font-size:12px;letter-spacing:2px;cursor:pointer;font-family:inherit;border-radius:4px;white-space:nowrap}}
.comment-form button:hover{{background:var(--red2)}}
.comment-form button:disabled{{opacity:.5}}
.comment-count{{font-size:12px;color:var(--muted);cursor:pointer}}
.comment-count:hover{{color:var(--red)}}
.hidden{{display:none!important}}
@media(max-width:600px){{
.login-card{{padding:28px 18px}}.login-card h1{{font-size:16px;letter-spacing:3px}}
.hero h2{{font-size:20px;letter-spacing:3px}}.hero .stats-row{{gap:20px}}
.cat-grid{{grid-template-columns:repeat(2,1fr);gap:8px}}.member-grid{{grid-template-columns:repeat(2,1fr)}}
.cat-card{{padding:14px 12px}}.cat-card .name{{font-size:13px}}
.entry{{padding:16px}}.entry .body{{font-size:12px}}
.topbar{{padding:0 14px}}.topbar .logo{{font-size:12px;letter-spacing:2px}}
}}
</style>
</head>
<body>
<div id="loginPage" class="login-wrap"><div class="login-card">
<div class="emblem">⚜️</div><h1>伪人大本营</h1><p class="tagline">机密档案库 · 身份核验</p>
<div class="field"><span class="prefix">+86</span><input id="phone" type="tel" inputmode="numeric" maxlength="11" placeholder="请输入手机号" autocomplete="tel"></div>
<div class="field"><input id="code" type="text" inputmode="numeric" maxlength="4" placeholder="验证码" autocomplete="one-time-code"><button id="sendBtn" class="code-btn">获取验证码</button></div>
<label class="agree"><input id="agree" type="checkbox"><span>我已阅读并同意 <a href="https://oss.talesofai.cn/static/blackboard/protocol-page/user-agreement.html" target="_blank">用户协议</a> 和 <a href="https://oss.talesofai.cn/static/blackboard/protocol-page/privacy-policy.html" target="_blank">隐私政策</a></span></label>
<button id="loginSubmit" class="submit">登 录</button>
<div class="msg" id="loginMsg"></div>
<div class="foot">未注册手机号验证后将自动登录 · t.nieta.art/UTLCFvWs</div>
</div></div>

<div id="mainPage" class="hidden">
<div class="topbar"><div class="logo" onclick="showHome()">伪人大本营</div><div class="user-grp"><img id="userAvatar"><span id="userName"></span><span id="userBadge"></span><button onclick="logout()">注销</button></div></div>
<div class="main">
<div class="hero"><h2 id="archiveTitle"></h2><p class="sub" id="archiveTagline"></p>
<div class="stats-row"><div class="stat"><div class="val" id="statHeat"></div><div class="lbl">热度</div></div><div class="stat"><div class="val" id="statSubs"></div><div class="lbl">订阅</div></div><div class="stat"><div class="val" id="statLore"></div><div class="lbl">条目</div></div><div class="stat"><div class="val" id="statMembers"></div><div class="lbl">成员</div></div></div></div>
<div class="search-bar"><span class="sicon">🔍</span><input type="text" id="globalSearch" placeholder="搜索全部档案..." oninput="globalSearch()"><div class="search-results" id="searchResults"></div></div>
<div id="homeView">
<div class="sec-title">大本营成员</div><div class="member-grid" id="memberGrid"></div>
<div class="sec-title">档案分类</div><div class="cat-grid" id="categoryGrid"></div>
</div>
<div id="categoryView" class="hidden"><div class="breadcrumb" onclick="showHome()"><b>←</b> 返回档案分类</div><div class="search-bar"><span class="sicon">🔍</span><input type="text" id="catSearch" placeholder="在当前分类中搜索..." oninput="filterCat()"></div><div id="entryList"></div></div>
<div id="entryView" class="hidden"><div class="breadcrumb" onclick="showCategory(currentCat)"><b>←</b> 返回</div><div id="singleEntry"></div>
<div class="comments-section"><h3>档案评论</h3><div id="commentList"></div>
<div class="comment-form"><img id="commentAvatar"><textarea id="commentInput" placeholder="写下你的评论..." rows="2"></textarea><button id="commentBtn" onclick="postComment()">发表</button></div></div></div>
</div></div>

<script src="https://oss.talesofai.cn/fe_assets/libs/gt4.js"></script>
<script>
var API_="https://api.talesofai.cn",me=null,myRole=null,allData=null,currentCat="",currentEntry=null,token="";
var ARCHIVE_={ARCHIVE_JSON},ALL_ENTRIES={ALL_JSON};

/* ═══ 登录 ═══ */
var ph=document.getElementById("phone"),cd=document.getElementById("code"),sb=document.getElementById("sendBtn"),
    ag=document.getElementById("agree"),lb=document.getElementById("loginSubmit"),lm=document.getElementById("loginMsg"),
    timer=0,tid=null;
/* ═══ 极验验证码（按需初始化） ═══ */
function initCaptcha(){{
  return new Promise(function(resolve,reject){{
    if(!window.initGeetest4){{reject("验证码组件加载失败，请刷新页面");return}}
    var done=false;
    var tid=setTimeout(function(){{if(!done){{done=true;reject("验证码加载超时（网络问题），请稍后重试")}}}},10000);
    window.initGeetest4({{
      captchaId:"e000881b946cad6dcc39aa1eb40c80b0",product:"popup",protocol:"https://",
      hideSuccess:true,mask:{{outside:false}}
    }},function(obj){{
      clearTimeout(tid);
      if(done)return;
      obj.onSuccess(function(){{var v=obj.getValidate();obj.destroy();resolve(v)}});
      obj.onError(function(e){{obj.destroy();reject("安全验证出错，请重试")}});
      obj.onClose(function(){{obj.destroy();reject("验证已取消")}});
      obj.onReady(function(){{obj.showCaptcha()}});
    }});
  }});
}}
function vp(p){{return /^1[3456789]\d{{9}}$/.test(p)}}
sb.onclick=async()=>{{
  var p=ph.value.trim();if(!vp(p)){{lm.textContent="请输入正确的手机号";lm.style.color="var(--red)";return}}
  lm.textContent="加载验证码...";lm.style.color="var(--muted)";sb.disabled=true;
  var validate;
  try{{validate=await initCaptcha()}}catch(e){{sb.disabled=false;lm.textContent=e;lm.style.color="var(--red)";return}}
  lm.textContent="发送中...";lm.style.color="var(--muted)";
  try{{
    var r=await fetch("/api/proxy/request-code",{{method:"POST",headers:{{"Content-Type":"application/json"}},body:JSON.stringify({{phone_num:p,captcha_validate:validate}})}});
    var t=await r.text(),d=null;try{{d=t?JSON.parse(t):null}}catch(e){{d=t}}
    if(!r.ok)throw new Error((d&&typeof d==="object"?d.message||d.msg||d.error||d.detail||JSON.stringify(d):d)||r.statusText);
    lm.textContent="验证码已发送";lm.style.color="var(--red)";
    timer=60;sb.textContent=timer+"s";clearInterval(tid);
    tid=setInterval(function(){{timer--;sb.textContent=timer+"s";if(timer<=0){{clearInterval(tid);sb.disabled=false;sb.textContent="获取验证码"}}}},1000);
  }}catch(e){{sb.disabled=false;lm.textContent="发送失败："+e.message;lm.style.color="var(--red)";}}
}};
lb.onclick=async()=>{{
  var p=ph.value.trim(),c=cd.value.trim();
  if(!vp(p)){{lm.textContent="请输入正确的手机号";lm.style.color="var(--red)";return}}
  if(!/^\d{{4}}$/.test(c)){{lm.textContent="请输入4位验证码";lm.style.color="var(--red)";return}}
  if(!ag.checked){{lm.textContent="请先阅读并同意协议";lm.style.color="var(--red)";return}}
  lb.disabled=true;lb.textContent="登录中...";lm.textContent="";
  try{{
    var r=await fetch("/api/proxy/verify-code",{{method:"POST",headers:{{"Content-Type":"application/json"}},body:JSON.stringify({{phone_num:p,code:c}})}});
    var t=await r.text(),data=null;try{{data=t?JSON.parse(t):null}}catch(e){{data=t}}
    if(!r.ok)throw new Error((data&&typeof data==="object"?data.message||data.msg||data.error:data)||r.statusText);
    token=data&&data.token?data.token:"";if(!token)throw new Error("未获取到令牌");
    localStorage.setItem("NIETA_ACCESS_TOKEN",token);
    var ur=await fetch(API_+"/v1/user/",{{headers:{{"x-token":token}}}});me=await ur.json();
    // 后端注册
    await fetch("/api/verify",{{method:"POST",headers:{{"Content-Type":"application/json","x-token":token}},body:JSON.stringify(me)}});
    var vr=await fetch("/api/members/role?uuid="+me.uuid);var rd=await vr.json();myRole=rd.role||"member";
    enterMain();
  }}catch(e){{lm.textContent="登录失败："+(e.message||e);lm.style.color="var(--red)"}}
  finally{{lb.disabled=false;lb.textContent="登 录"}}
}};
function enterMain(){{
  document.getElementById("userName").textContent=me.nick_name||me.name;
  document.getElementById("userAvatar").src=me.avatar_url||"";
  var b=document.getElementById("userBadge");b.innerHTML="";
  if(myRole==="chief")b.innerHTML='<span class="badge-chief">⚜️ 营长</span>';
  else if(myRole==="deputy")b.innerHTML='<span class="badge-deputy">⚜️ 二营长</span>';
  else if(myRole==="admin")b.innerHTML='<span class="badge-admin">管理员</span>';
  document.getElementById("loginPage").classList.add("hidden");
  document.getElementById("mainPage").classList.remove("hidden");
  allData=ARCHIVE_;
  document.getElementById("archiveTitle").textContent="伪人大本营";
  document.getElementById("archiveTagline").textContent=allData.tagline;
  document.getElementById("statHeat").textContent=(allData.stats.heat/1e4).toFixed(0)+"万";
  document.getElementById("statSubs").textContent=allData.stats.subscribers;
  document.getElementById("statLore").textContent=allData.stats.lore_count;
  showHome();
}}

var saved=localStorage.getItem("NIETA_ACCESS_TOKEN");
if(saved){{document.getElementById("loginSubmit").disabled=true;document.getElementById("loginSubmit").textContent="自动登录中...";document.getElementById("loginMsg").textContent="检测到已保存的登录状态";document.getElementById("loginMsg").style.color="var(--muted)";fetch(API_+"/v1/user/",{{headers:{{"x-token":saved}}}}).then(function(r){{return r.json()}}).then(function(u){{if(u.uuid){{me=u;token=saved;fetch("/api/verify",{{method:"POST",headers:{{"Content-Type":"application/json","x-token":token}},body:JSON.stringify(me)}});fetch("/api/members/role?uuid="+u.uuid).then(function(r){{return r.json()}}).then(function(d){{myRole=d.role||"member";enterMain()}})}}else{{document.getElementById("loginSubmit").disabled=false;document.getElementById("loginSubmit").textContent="登 录";document.getElementById("loginMsg").textContent=""}}}}).catch(function(){{document.getElementById("loginSubmit").disabled=false;document.getElementById("loginSubmit").textContent="登 录";document.getElementById("loginMsg").textContent=""}})}}

/* ═══ 成员 ═══ */
function renderMembers(){{
  fetch("/api/members").then(function(r){{return r.json()}}).then(function(members){{
    var g=document.getElementById("memberGrid");if(!g)return;g.innerHTML="";
    document.getElementById("statMembers").textContent=members.length;
    members.forEach(function(m){{
      var roleBadge="",cardClass="";
      if(m.role==="chief"){{roleBadge='<span class="badge-chief">营长</span>';cardClass=" m-chief"}}
      else if(m.role==="deputy"){{roleBadge='<span class="badge-deputy">二营长</span>'}}
      else if(m.role==="admin"){{roleBadge='<span class="badge-admin">管理</span>'}}
      var d=document.createElement("div");d.className="member-card"+cardClass;
      d.innerHTML='<img src="'+esc(m.avatar)+'" onerror="this.style.display=\\'none\\'"><div class="m-info"><div class="m-name">'+esc(m.name)+' '+roleBadge+'</div><div class="m-time">'+(m.online?'在线':timeAgo(m.last_seen))+'</div></div><div class="m-status '+(m.online?'m-online':'m-offline')+'"></div>';
      g.appendChild(d);
    }});
  }});
}}

function showHome(){{
  document.getElementById("homeView").classList.remove("hidden");
  document.getElementById("categoryView").classList.add("hidden");
  document.getElementById("entryView").classList.add("hidden");
  renderMembers();
  var g=document.getElementById("categoryGrid");g.innerHTML="";
  var cats=Object.entries(allData.lore);cats.sort(function(a,b){{return b[1].length-a[1].length}});
  cats.forEach(function(e){{var d=document.createElement("div");d.className="cat-card";d.innerHTML='<div class="name">'+esc(e[0])+'</div><div class="count">'+e[1].length+' 条档案</div>';d.onclick=function(){{showCategory(e[0])}};g.appendChild(d)}});
}}
function showCategory(cat){{currentCat=cat;window.scrollTo(0,0);document.getElementById("homeView").classList.add("hidden");document.getElementById("categoryView").classList.remove("hidden");document.getElementById("entryView").classList.add("hidden");document.getElementById("catSearch").value="";renderEntries(allData.lore[cat]||[])}}
function renderEntries(entries){{var l=document.getElementById("entryList");l.innerHTML="";entries.forEach(function(e){{var d=document.createElement("div");d.className="entry";d.innerHTML='<div class="entry-head">'+badge(e.description)+'<span class="entry-title">'+esc(e.name)+'</span></div><div class="body">'+fmt(e.description)+'</div><div style="margin-top:12px"><span class="comment-count" onclick="event.stopPropagation();showEntry(\\''+e.uuid+'\\')">💬 '+comCount(e.uuid)+' 条评论</span></div>';d.style.cursor="pointer";d.onclick=function(){{showEntry(e.uuid)}};l.appendChild(d)}})}}
function comCount(uuid){{var c=getComments();return (c[uuid]||[]).length}}
function showEntry(uuid){{window.scrollTo(0,0);var entry=ALL_ENTRIES.find(function(e){{return e.uuid===uuid}});if(!entry)return;currentEntry=entry;document.getElementById("homeView").classList.add("hidden");document.getElementById("categoryView").classList.add("hidden");document.getElementById("entryView").classList.remove("hidden");document.querySelector("#entryView .breadcrumb b").nextSibling.textContent=" 返回 "+entry.category;document.getElementById("singleEntry").innerHTML='<div class="entry"><div class="entry-head">'+badge(entry.description)+'<span class="entry-title" style="font-size:18px">'+esc(entry.name)+'</span></div><div class="body">'+fmt(entry.description)+'</div></div>';document.getElementById("commentAvatar").src=me?me.avatar_url||"":"";loadComments(uuid)}}
function loadComments(uuid){{fetch("/api/comments?entry_uuid="+uuid).then(function(r){{return r.json()}}).then(function(comments){{var l=document.getElementById("commentList");l.innerHTML="";comments.forEach(function(c){{var d=document.createElement("div");d.className="comment";d.innerHTML='<img src="'+esc(c.user_avatar)+'" onerror="this.style.display=\\'none\\'"><div class="c-body"><div class="c-head"><span class="c-name">'+esc(c.user_name)+'</span><span class="c-time">'+timeAgo(c.created_at)+'</span></div><div class="c-text">'+esc(c.content)+'</div></div>';l.appendChild(d)}});}});}}
function postComment(){{if(!currentEntry||!me||!token)return;var content=document.getElementById("commentInput").value.trim();if(!content)return;var btn=document.getElementById("commentBtn");btn.disabled=true;btn.textContent="发送中...";fetch("/api/comments",{{method:"POST",headers:{{"Content-Type":"application/json","x-token":token}},body:JSON.stringify({{entry_uuid:currentEntry.uuid,content:content}})}}).then(function(r){{btn.disabled=false;btn.textContent="发表";if(r.ok){{document.getElementById("commentInput").value="";loadComments(currentEntry.uuid)}}}});}}
function globalSearch(){{var q=document.getElementById("globalSearch").value.toLowerCase().trim(),r=document.getElementById("searchResults");if(!q){{r.style.display="none";return}}r.style.display="block";r.innerHTML="";var items=ALL_ENTRIES.filter(function(e){{return e.name.toLowerCase().indexOf(q)>=0||e.description.toLowerCase().indexOf(q)>=0}}).slice(0,20);if(!items.length){{r.innerHTML='<div class="item"><span class="name" style="color:var(--muted)">无匹配</span></div>';return}}items.forEach(function(it){{var d=document.createElement("div");d.className="item";d.innerHTML='<span class="name">'+esc(it.name)+'</span><span class="cat">'+esc(it.category)+'</span>';d.onclick=function(){{showEntry(it.uuid);r.style.display="none";document.getElementById("globalSearch").value=""}};r.appendChild(d)}});}}
document.addEventListener("click",function(e){{if(!e.target.closest(".search-bar"))document.getElementById("searchResults").style.display="none"}});
function filterCat(){{var q=document.getElementById("catSearch").value.toLowerCase().trim();renderEntries(!q?allData.lore[currentCat]||[]:(allData.lore[currentCat]||[]).filter(function(e){{return e.name.toLowerCase().indexOf(q)>=0||e.description.toLowerCase().indexOf(q)>=0}}))}}
function badge(d){{if(!d)return"";if(/🟥/.test(d))return'<span class="badge b-red">🟥</span>';if(/🟧/.test(d))return'<span class="badge b-orange">🟧</span>';if(/🟨/.test(d))return'<span class="badge b-yellow">🟨</span>';if(/🟩/.test(d))return'<span class="badge b-green">🟩</span>';if(/⬜/.test(d))return'<span class="badge b-gray">⬜</span>';return""}}
function esc(s){{var d=document.createElement("div");d.textContent=s;return d.innerHTML}}
function fmt(s){{return esc(s).replace(/\\n/g,"<br>").replace(/\*\*(.+?)\*\*/g,"<strong>$1</strong>")}}
function timeAgo(ts){{if(!ts)return"";var d=(Date.now()/1000)-ts;if(d<0)return"在线";if(d<60)return"刚刚在线";if(d<3600)return Math.floor(d/60)+"分钟前";if(d<86400)return Math.floor(d/3600)+"小时前";return Math.floor(d/86400)+"天前"}}
function getComments(){{try{{return JSON.parse(localStorage.getItem("ph_comments")||"{{}}")}}catch(e){{return{{}}}}}}
async function tokenLogin(){{var tk=document.getElementById("tokenInput").value.trim();if(!tk)return;var lm=document.getElementById("loginMsg");lm.textContent="验证中...";lm.style.color="var(--muted)";try{{var ur=await fetch(API_+"/v1/user/",{{headers:{{"x-token":tk}}}});var u=await ur.json();if(!u.uuid)throw new Error("令牌无效");me=u;token=tk;localStorage.setItem("NIETA_ACCESS_TOKEN",tk);await fetch("/api/verify",{{method:"POST",headers:{{"Content-Type":"application/json","x-token":token}},body:JSON.stringify(me)}});var vr=await fetch("/api/members/role?uuid="+me.uuid);myRole=(await vr.json()).role||"member";enterMain()}}catch(e){{lm.textContent="❌ "+e.message;lm.style.color="var(--red)"}}}}
function logout(){{token="";me=null;myRole=null;allData=null;localStorage.removeItem("NIETA_ACCESS_TOKEN");document.getElementById("loginPage").classList.remove("hidden");document.getElementById("mainPage").classList.add("hidden")}}
</script>
</body>
</html>"""

# ═══════════ 后端 API ═══════════
class Server(BaseHTTPRequestHandler):
    def _security_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()")
        self.send_header("Cross-Origin-Resource-Policy", "same-site")
        self.send_header("Content-Security-Policy", "default-src 'self' https: data: blob:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' https: data: blob:; connect-src 'self' https: wss:; frame-src https:; child-src https:; frame-ancestors 'self' https://*.cohub.run https://cohub.run https://*.cohub.ai https://*.cohub.art; base-uri 'self'; form-action 'self'; object-src 'none'")

    def _json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "x-token, content-type")
        self._security_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _serve_file(self, rel_path="index.html"):
        rel_path = rel_path.lstrip("/") or "index.html"
        full = os.path.abspath(os.path.join(DIST_DIR, rel_path))
        root = os.path.abspath(DIST_DIR)
        if not full.startswith(root + os.sep) and full != root:
            self.send_error(403); return
        if not os.path.isfile(full):
            full = os.path.join(root, "index.html")
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if ctype.startswith("text/") or ctype in ("application/javascript", "application/json") else ""))
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self._security_headers()
        self.end_headers()
        with open(full, "rb") as f:
            self.wfile.write(f.read())

    def do_OPTIONS(self):
        self._json({})

    def do_GET(self):
        p = urlparse(self.path)
        if not p.path.startswith("/api/"):
            if os.path.isdir(DIST_DIR) and os.path.isfile(os.path.join(DIST_DIR, "index.html")):
                self._serve_file(p.path)
            else:
                self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self._security_headers(); self.end_headers()
                self.wfile.write(PAGE.encode())
        elif p.path == "/api/members":
            db = get_db()
            now = int(time.time())
            rows = db.execute("SELECT uuid,name,avatar,role,title,avatar_frame,signature,online,last_seen FROM members ORDER BY online DESC, last_seen DESC, CASE role WHEN 'chief' THEN 0 WHEN 'deputy' THEN 1 WHEN 'admin' THEN 2 ELSE 3 END, name").fetchall()
            db.close()
            members = []
            for r in rows:
                online = r["online"] and (now - r["last_seen"] < 600) if r["last_seen"] else False
                members.append({"uuid": r["uuid"], "name": r["name"], "avatar": r["avatar"], "role": r["role"], "title": r["title"] or "", "avatar_frame": r["avatar_frame"] or "none", "signature": r["signature"] or "", "online": online, "last_seen": r["last_seen"]})
            self._json(members)
        elif p.path == "/api/members/role":
            q = parse_qs(p.query); uuid = q.get("uuid", [""])[0]
            db = get_db(); r = db.execute("SELECT role,avatar_frame FROM members WHERE uuid=?", [uuid]).fetchone(); db.close()
            self._json({"role": r["role"] if r else "member", "avatar_frame": r["avatar_frame"] if r else "none"})
        elif p.path == "/api/comments":
            eu = parse_qs(p.query).get("entry_uuid", [None])[0]
            if not eu: self._json([]); return
            db = get_db()
            rows = db.execute("SELECT user_name,user_avatar,content,created_at FROM comments WHERE entry_uuid=? ORDER BY created_at DESC LIMIT 100", [eu]).fetchall()
            db.close()
            self._json([{"user_name": r["user_name"], "user_avatar": r["user_avatar"], "content": r["content"], "created_at": r["created_at"]} for r in rows])
        elif p.path == "/api/forum/posts":
            channel = parse_qs(p.query).get("channel", [""])[0].strip()[:80]
            if not channel: self._json([]); return
            db = get_db()
            rows = db.execute("""SELECT p.id,p.channel,p.user_uuid,p.user_name,p.user_avatar,p.content,p.images_json,p.revoked,p.created_at,
                                      COALESCE(m.avatar_frame,'none') AS avatar_frame
                               FROM forum_posts p LEFT JOIN members m ON p.user_uuid=m.uuid
                               WHERE p.channel=? ORDER BY p.created_at DESC LIMIT 120""", [channel]).fetchall()
            db.close()
            posts = []
            for r in rows:
                try: images = json.loads(r["images_json"] or "[]")
                except Exception: images = []
                posts.append({"id": r["id"], "channel": r["channel"], "user_uuid": r["user_uuid"], "user_name": r["user_name"], "user_avatar": r["user_avatar"], "avatar_frame": r["avatar_frame"] or "none", "content": r["content"], "images": images, "revoked": bool(r["revoked"]), "created_at": r["created_at"]})
            self._json(posts)
        elif p.path == "/api/forum/channels":
            db = get_db()
            rows = db.execute("SELECT id,code,name,description,created_at FROM forum_channels ORDER BY created_at ASC, id ASC").fetchall()
            db.close()
            self._json([{"id": r["id"], "code": r["code"] or "NEW", "name": r["name"], "desc": r["description"] or "自定义地区分支。", "custom": True, "created_at": r["created_at"]} for r in rows])
        elif p.path == "/api/activities":
            db = get_db()
            rows = db.execute("SELECT id,title,status,description,created_at FROM activities ORDER BY created_at DESC, id DESC").fetchall()
            db.close()
            self._json([{"id": r["id"], "title": r["title"], "status": r["status"] or "进行中", "desc": r["description"] or "暂无说明。", "custom": True, "created_at": r["created_at"]} for r in rows])
        elif p.path == "/api/wiki/submissions":
            db = get_db()
            status = parse_qs(p.query).get("status", [""])[0].strip()
            if status in ("pending", "approved", "rejected"):
                rows = db.execute("SELECT id,target,submit_type,content,images_json,user_uuid,user_name,status,reviewed_by,reviewed_at,review_note,created_at FROM wiki_submissions WHERE status=? ORDER BY created_at DESC LIMIT 100", [status]).fetchall()
            else:
                rows = db.execute("SELECT id,target,submit_type,content,images_json,user_uuid,user_name,status,reviewed_by,reviewed_at,review_note,created_at FROM wiki_submissions ORDER BY created_at DESC LIMIT 100").fetchall()
            db.close()
            out = []
            for r in rows:
                payload = parse_wiki_submission(r)
                images = payload.get("images") if isinstance(payload.get("images"), list) else []
                title = payload.get("entry_name") or r["target"]
                text = payload.get("body") or payload.get("content") or r["content"]
                out.append({"id": r["id"], "target": r["target"], "entry_name": title, "type": r["submit_type"], "content": text, "images": images, "author": r["user_name"] or "成员投稿", "status": r["status"], "reviewed_by": r["reviewed_by"] or "", "reviewed_at": r["reviewed_at"], "review_note": r["review_note"] or "", "time": r["created_at"]})
            self._json(out)
        elif p.path == "/api/wiki/archive":
            self._json(ARCHIVE)
        elif p.path == "/api/search":
            q = parse_qs(p.query).get("q", [""])[0].strip()[:80]
            if not q:
                self._json([]); return
            # 参数化 LIKE：保留 SQLite 速度，同时避免 SQL 注入和通配符滥用
            like = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
            db = get_db()
            rows = db.execute("""SELECT uuid,category,name,description FROM entries
                               WHERE name LIKE ? ESCAPE '\\' OR description LIKE ? ESCAPE '\\'
                               ORDER BY CASE WHEN name LIKE ? ESCAPE '\\' THEN 0 ELSE 1 END, category, name
                               LIMIT 30""", (like, like, like)).fetchall()
            db.close()
            self._json([{"uuid": r["uuid"], "category": r["category"], "name": r["name"], "description": r["description"]} for r in rows])
        elif p.path == "/api/stats":
            db = get_db()
            tc = db.execute("SELECT COUNT(*) FROM comments").fetchone()[0]
            tm = db.execute("SELECT COUNT(*) FROM members").fetchone()[0]
            db.close()
            self._json({**ARCHIVE["stats"], "total_comments": tc, "total_members": tm})
        elif p.path == "/api/health":
            self._json({"ok": True, "service": "pseudo-human", "port": PORT})
        elif p.path == "/api/proxy/request-code" or p.path == "/api/proxy/verify-code":
            self.send_error(405)
        else:
            self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length > 0 else {}
        token = self.headers.get("x-token", "")
        p = urlparse(self.path)

        # 代理验证码请求（绕过浏览器 Origin/CORS 限制）
        if p.path == "/api/proxy/request-code":
            try:
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Origin": "https://app.nieta.art",
                    "Referer": "https://app.nieta.art/",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
                }
                r = requests.post(f"{API}/v1/user/request-verification-code", json=body, timeout=15, headers=headers)
                try:
                    data = r.json()
                except Exception:
                    data = {"error": r.text[:500] or r.reason}
                self._json(data, r.status_code)
            except Exception as e:
                self._json({"error": str(e)}, 502)
            return

        if p.path == "/api/proxy/verify-code":
            try:
                headers = {
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Origin": "https://app.nieta.art",
                    "Referer": "https://app.nieta.art/",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
                }
                r = requests.post(f"{API}/v1/user/verify-with-phone-num", json=body, timeout=15, headers=headers)
                try:
                    data = r.json()
                except Exception:
                    data = {"error": r.text[:500] or r.reason}
                self._json(data, r.status_code)
            except Exception as e:
                self._json({"error": str(e)}, 502)
            return

        if p.path == "/api/verify":
            # 验证 token 后注册/更新用户，避免信任前端伪造的用户信息
            if not token: self._json({"error": "未登录"}, 401); return
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10); r.raise_for_status(); user = r.json()
            except Exception:
                self._json({"error": "令牌无效"}, 401); return
            uuid = user.get("uuid", ""); name = user.get("nick_name") or user.get("name", "")
            avatar = user.get("avatar_url", "")
            if not uuid: self._json({"error": "无效用户"}, 400); return
            db = get_db()
            # 注册为普通成员（如果还不存在）
            db.execute("INSERT OR IGNORE INTO members(uuid,name,avatar,role) VALUES(?,?,?,'member')", (uuid, name, avatar))
            db.execute("UPDATE members SET name=?,avatar=?,online=1,last_seen=? WHERE uuid=?", (name, avatar, int(time.time()), uuid))
            db.commit(); db.close()
            self._json({"ok": True})

        elif p.path == "/api/comments":
            if not token: self._json({"error": "未登录"}, 401); return
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10); r.raise_for_status(); user = r.json()
            except: self._json({"error": "令牌无效"}, 401); return
            eu = body.get("entry_uuid", ""); content = body.get("content", "").strip()
            if not eu or not content: self._json({"error": "缺少参数"}, 400); return
            if len(content) > 2000: self._json({"error": "评论过长"}, 400); return
            db = get_db()
            db.execute("INSERT INTO comments(entry_uuid,user_uuid,user_name,user_avatar,content) VALUES(?,?,?,?,?)",
                       [eu, user["uuid"], user.get("nick_name") or user["name"], user.get("avatar_url", ""), content])
            db.execute("UPDATE members SET online=1,last_seen=? WHERE uuid=?", (int(time.time()), user["uuid"]))
            db.commit(); db.close()
            self._json({"ok": True})
        elif p.path == "/api/forum/posts":
            if not token: self._json({"error": "未登录"}, 401); return
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10); r.raise_for_status(); user = r.json()
            except Exception:
                self._json({"error": "令牌无效"}, 401); return
            channel = str(body.get("channel", "")).strip()[:80]
            content = str(body.get("content", "")).strip()
            images = body.get("images", [])
            if not isinstance(images, list): images = []
            images = [str(x) for x in images if str(x).startswith(("http://", "https://"))][:9]
            if not channel or (not content and not images): self._json({"error": "缺少内容"}, 400); return
            if len(content) > 2000: self._json({"error": "发言过长"}, 400); return
            db = get_db()
            db.execute("""INSERT INTO forum_posts(channel,user_uuid,user_name,user_avatar,content,images_json)
                       VALUES(?,?,?,?,?,?)""", [channel, user["uuid"], user.get("nick_name") or user.get("name", ""), user.get("avatar_url", ""), content, json.dumps(images, ensure_ascii=False)])
            db.execute("UPDATE members SET online=1,last_seen=? WHERE uuid=?", (int(time.time()), user["uuid"]))
            db.commit(); db.close()
            self._json({"ok": True})
        elif p.path == "/api/forum/revoke":
            if not token: self._json({"error": "未登录"}, 401); return
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10); r.raise_for_status(); user = r.json()
            except Exception:
                self._json({"error": "令牌无效"}, 401); return
            db = get_db()
            role_row = db.execute("SELECT role FROM members WHERE uuid=?", [user.get("uuid", "")]).fetchone()
            role = role_row["role"] if role_row else "member"
            if role not in ("chief", "deputy", "admin"):
                db.close(); self._json({"error": "权限不足"}, 403); return
            post_id = int(body.get("id", 0) or 0)
            db.execute("UPDATE forum_posts SET revoked=1,revoked_by=? WHERE id=?", [user.get("uuid", ""), post_id])
            db.commit(); db.close()
            self._json({"ok": True})
        elif p.path == "/api/forum/channels":
            if not token: self._json({"error": "未登录"}, 401); return
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10); r.raise_for_status(); user = r.json()
            except Exception:
                self._json({"error": "令牌无效"}, 401); return
            db = get_db()
            role_row = db.execute("SELECT role FROM members WHERE uuid=?", [user.get("uuid", "")]).fetchone()
            role = role_row["role"] if role_row else "member"
            if role not in ("chief", "deputy", "admin"):
                db.close(); self._json({"error": "权限不足"}, 403); return
            name = str(body.get("name", "")).strip()[:30]
            desc = str(body.get("desc", "")).strip()[:120] or "自定义地区分支。"
            code = str(body.get("code", "")).strip()[:8] or "NEW"
            if not name: db.close(); self._json({"error": "缺少分支名称"}, 400); return
            try:
                db.execute("INSERT INTO forum_channels(code,name,description,created_by) VALUES(?,?,?,?)", [code, name, desc, user.get("uuid", "")])
                db.commit()
            except sqlite3.IntegrityError:
                db.close(); self._json({"error": "分支已存在"}, 400); return
            row = db.execute("SELECT id,code,name,description,created_at FROM forum_channels WHERE name=?", [name]).fetchone()
            db.close(); self._json({"id": row["id"], "code": row["code"], "name": row["name"], "desc": row["description"], "custom": True, "created_at": row["created_at"]})
        elif p.path == "/api/forum/channels/delete":
            if not token: self._json({"error": "未登录"}, 401); return
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10); r.raise_for_status(); user = r.json()
            except Exception:
                self._json({"error": "令牌无效"}, 401); return
            db = get_db(); role_row = db.execute("SELECT role FROM members WHERE uuid=?", [user.get("uuid", "")]).fetchone(); role = role_row["role"] if role_row else "member"
            if role not in ("chief", "deputy", "admin"):
                db.close(); self._json({"error": "权限不足"}, 403); return
            name = str(body.get("name", "")).strip()[:30]
            if not name: db.close(); self._json({"error": "缺少分支名称"}, 400); return
            db.execute("DELETE FROM forum_channels WHERE name=?", [name]); db.commit(); db.close(); self._json({"ok": True})
        elif p.path == "/api/wiki/submissions":
            if not token: self._json({"error": "未登录"}, 401); return
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10); r.raise_for_status(); user = r.json()
            except Exception:
                self._json({"error": "令牌无效"}, 401); return
            target = str(body.get("target") or body.get("category") or "").strip()[:80]
            submit_type = str(body.get("type", "新增词条")).strip()[:30]
            content = str(body.get("content", "")).strip()
            images = body.get("images", [])
            if not isinstance(images, list): images = []
            images = [str(x) for x in images if str(x).startswith(("http://", "https://"))][:9]
            payload = {
                "group": str(body.get("group", "世界信息")).strip()[:30],
                "category": target,
                "entry_name": str(body.get("entry_name", "")).strip()[:80],
                "body": content,
                "images": images,
            }
            if not target or not content: self._json({"error": "缺少分类名称或正文内容"}, 400); return
            if submit_type != "新建分类" and not payload["entry_name"]: self._json({"error": "缺少条目名称"}, 400); return
            if len(content) > 5000: self._json({"error": "内容过长"}, 400); return
            db = get_db()
            db.execute("INSERT INTO wiki_submissions(target,submit_type,content,images_json,user_uuid,user_name) VALUES(?,?,?,?,?,?)", [target, submit_type, json.dumps(payload, ensure_ascii=False), json.dumps(images, ensure_ascii=False), user.get("uuid", ""), user.get("nick_name") or user.get("name", "")])
            db.commit(); row = db.execute("SELECT id,target,submit_type,content,created_at FROM wiki_submissions WHERE id=last_insert_rowid()").fetchone(); db.close()
            self._json({"id": row["id"], "target": row["target"], "type": row["submit_type"], "content": content, "status": "pending", "time": row["created_at"]})
        elif p.path == "/api/wiki/review":
            if not token: self._json({"error": "未登录"}, 401); return
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10); r.raise_for_status(); user = r.json()
            except Exception:
                self._json({"error": "令牌无效"}, 401); return
            db = get_db(); role_row = db.execute("SELECT role FROM members WHERE uuid=?", [user.get("uuid", "")]).fetchone(); role = role_row["role"] if role_row else "member"
            if role not in ("chief", "deputy", "admin"):
                db.close(); self._json({"error": "权限不足"}, 403); return
            sid = int(body.get("id", 0) or 0)
            action = str(body.get("action", "approved")).strip()
            row = db.execute("SELECT * FROM wiki_submissions WHERE id=?", [sid]).fetchone()
            if not row:
                db.close(); self._json({"error": "提交不存在"}, 404); return
            if row["status"] != "pending":
                db.close(); self._json({"error": "该提交已经处理过"}, 400); return
            if action == "approved":
                try:
                    apply_wiki_submission(row)
                except Exception as e:
                    db.close(); self._json({"error": str(e)}, 400); return
                db.execute("UPDATE wiki_submissions SET status='approved', reviewed_by=?, reviewed_at=?, review_note=? WHERE id=?", [user.get("nick_name") or user.get("name", "管理员"), int(time.time()), str(body.get("note", "")).strip()[:300], sid])
            else:
                db.execute("UPDATE wiki_submissions SET status='rejected', reviewed_by=?, reviewed_at=?, review_note=? WHERE id=?", [user.get("nick_name") or user.get("name", "管理员"), int(time.time()), str(body.get("note", "")).strip()[:300], sid])
            db.commit(); db.close(); self._json({"ok": True, "status": "approved" if action == "approved" else "rejected"})
        elif p.path == "/api/activities":
            if not token: self._json({"error": "未登录"}, 401); return
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10); r.raise_for_status(); user = r.json()
            except Exception:
                self._json({"error": "令牌无效"}, 401); return
            db = get_db(); role_row = db.execute("SELECT role FROM members WHERE uuid=?", [user.get("uuid", "")]).fetchone(); role = role_row["role"] if role_row else "member"
            if role not in ("chief", "deputy", "admin"):
                db.close(); self._json({"error": "权限不足"}, 403); return
            title = str(body.get("title", "")).strip()[:40]
            status = str(body.get("status", "进行中")).strip()[:12] or "进行中"
            desc = str(body.get("desc", "")).strip()[:300] or "暂无说明。"
            if not title: db.close(); self._json({"error": "缺少活动标题"}, 400); return
            db.execute("INSERT INTO activities(title,status,description,created_by) VALUES(?,?,?,?)", [title, status, desc, user.get("uuid", "")])
            db.commit(); row = db.execute("SELECT id,title,status,description,created_at FROM activities WHERE id=last_insert_rowid()").fetchone(); db.close()
            self._json({"id": row["id"], "title": row["title"], "status": row["status"], "desc": row["description"], "custom": True, "created_at": row["created_at"]})
        elif p.path == "/api/activities/delete":
            if not token: self._json({"error": "未登录"}, 401); return
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10); r.raise_for_status(); user = r.json()
            except Exception:
                self._json({"error": "令牌无效"}, 401); return
            db = get_db(); role_row = db.execute("SELECT role FROM members WHERE uuid=?", [user.get("uuid", "")]).fetchone(); role = role_row["role"] if role_row else "member"
            if role not in ("chief", "deputy", "admin"):
                db.close(); self._json({"error": "权限不足"}, 403); return
            aid = int(body.get("id", 0) or 0)
            db.execute("DELETE FROM activities WHERE id=?", [aid]); db.commit(); db.close(); self._json({"ok": True})
        elif p.path == "/api/members/title":
            if not token: self._json({"error": "未登录"}, 401); return
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10); r.raise_for_status(); user = r.json()
            except Exception:
                self._json({"error": "令牌无效"}, 401); return
            target_uuid = str(body.get("uuid", "")).strip()
            title = str(body.get("title", "")).strip()[:30]
            if not target_uuid: self._json({"error": "缺少成员 uuid"}, 400); return
            db = get_db()
            role_row = db.execute("SELECT role FROM members WHERE uuid=?", [user.get("uuid", "")]).fetchone()
            role = role_row["role"] if role_row else "member"
            if role not in ("chief", "deputy", "admin"):
                db.close(); self._json({"error": "只有管理员可以授权称号"}, 403); return
            exists = db.execute("SELECT uuid FROM members WHERE uuid=?", [target_uuid]).fetchone()
            if not exists:
                db.close(); self._json({"error": "成员不存在"}, 404); return
            db.execute("UPDATE members SET title=? WHERE uuid=?", [title, target_uuid])
            db.commit(); db.close()
            self._json({"ok": True, "uuid": target_uuid, "title": title})
        elif p.path == "/api/members/avatar-frame":
            if not token: self._json({"error": "未登录"}, 401); return
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10); r.raise_for_status(); user = r.json()
            except Exception:
                self._json({"error": "令牌无效"}, 401); return
            frame = str(body.get("avatar_frame", "none")).strip()
            if frame not in ("none", "roach", "moonrise"): frame = "none"
            db = get_db()
            db.execute("UPDATE members SET avatar_frame=? WHERE uuid=?", [frame, user.get("uuid", "")])
            db.commit(); db.close()
            self._json({"ok": True, "avatar_frame": frame})
        elif p.path == "/api/members/signature":
            if not token: self._json({"error": "未登录"}, 401); return
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10); r.raise_for_status(); user = r.json()
            except Exception:
                self._json({"error": "令牌无效"}, 401); return
            signature = str(body.get("signature", "")).strip()[:50]
            db = get_db()
            db.execute("UPDATE members SET signature=?, online=1, last_seen=? WHERE uuid=?", [signature, int(time.time()), user.get("uuid", "")])
            db.commit(); db.close()
            self._json({"ok": True, "signature": signature})
        elif p.path == "/api/private/messages":
            if not token: self._json({"error": "未登录"}, 401); return
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10); r.raise_for_status(); user = r.json()
            except Exception:
                self._json({"error": "令牌无效"}, 401); return
            to_uuid = str(body.get("to_uuid", "")).strip()
            content = str(body.get("content", "")).strip()
            if not to_uuid or not content: self._json({"error": "缺少内容"}, 400); return
            if len(content) > 2000: self._json({"error": "私聊过长"}, 400); return
            db = get_db()
            exists = db.execute("SELECT uuid FROM members WHERE uuid=?", [to_uuid]).fetchone()
            if not exists:
                db.close(); self._json({"error": "成员不存在"}, 404); return
            db.execute("INSERT INTO private_messages(from_uuid,to_uuid,from_name,from_avatar,content) VALUES(?,?,?,?,?)", [user["uuid"], to_uuid, user.get("nick_name") or user.get("name", ""), user.get("avatar_url", ""), content])
            db.execute("UPDATE members SET online=1,last_seen=? WHERE uuid=?", (int(time.time()), user["uuid"]))
            db.commit(); db.close()
            self._json({"ok": True})
        else:
            self.send_error(404)

    def log_message(self, f, *a): pass

if __name__ == "__main__":
    import webbrowser, threading
    db = get_db()
    mc = db.execute("SELECT COUNT(*) FROM members").fetchone()[0]
    db.close()
    print(f"\n  伪人大本营 → http://localhost:{PORT}  |  成员: {mc}  |  档案: {len(ALL_ENTRIES)}\n")
    threading.Timer(0.8, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
    HTTPServer(("0.0.0.0", PORT), Server).serve_forever()
