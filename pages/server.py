#!/usr/bin/env python3
"""
伪人大本营 — 捏Ta 登录 + 档案库 + 成员系统
python3 server.py  →  localhost:3000

Privacy / Security Notes:
- This server does not persist Neta tokens.
- This server does not persist phone numbers or verification codes.
- This server does not persist client IP addresses, User-Agent strings, device fingerprints, or location data.
- x-token is used only for per-request authentication and upstream Neta API calls.
- Persisted data is limited to user-submitted site content: profile display data, signatures, forum posts,
  comments, Wiki submissions, identity cards, and private messages.
"""
import json, os, time, sqlite3, hashlib, mimetypes, re, html, base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests

API = "https://api.talesofai.cn"
PORT = int(os.environ.get("PORT", "3000"))
DB = os.path.join(os.path.dirname(__file__) or ".", "pseudo_human.db")
BASE_DIR = os.path.dirname(__file__) or "."
DATA = os.path.join(BASE_DIR, "pseudo-human-data.json")
DIST_DIR = os.path.join(BASE_DIR, "dist")
MAX_BODY_BYTES = 1024 * 1024
RATE_BUCKET = {}
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX_AUTH = 90
RATE_LIMIT_MAX_ANON = 180

def token_user_key(token):
    # Best-effort JWT payload parse for rate limiting only. Does not store token.
    # 仅在内存中按用户标识做短期计数，不记录 IP，不保存 token。
    try:
        parts = str(token or "").split(".")
        if len(parts) < 2:
            return "anon"
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload.encode()).decode("utf-8"))
        uuid = data.get("uuid") or data.get("user_uuid")
        if uuid:
            return "user:" + clean_text(uuid, 80)
        uid = data.get("id")
        if uid:
            return "user-id:" + clean_text(uid, 40)
    except Exception:
        pass
    return "anon"


def rate_limited_key(key, max_count):
    # In-memory bucket by user uuid or anonymous group. No IP, no token persistence.
    now = time.time()
    bucket = RATE_BUCKET.get(key, [])
    bucket = [t for t in bucket if now - t < RATE_LIMIT_WINDOW]
    bucket.append(now)
    RATE_BUCKET[key] = bucket
    return len(bucket) > max_count


def clean_text(value, limit=2000):
    text = str(value or "").replace("\x00", "").strip()
    text = re.sub(r"[\u0000-\u0008\u000b\u000c\u000e-\u001f]", "", text)
    return text[:limit]


def safe_public_url(url):
    s = str(url or "").strip()
    if not re.match(r"^https?://", s, re.I):
        return ""
    if re.search(r"[\s\"'<>]", s):
        return ""
    return s[:1000]


def load_env_file(path):
    if not os.path.isfile(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#") or "=" not in s:
                    continue
                k, v = s.split("=", 1)
                k = k.strip(); v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass

load_env_file(os.path.join(BASE_DIR, ".env"))
load_env_file(os.path.join(os.path.dirname(BASE_DIR), ".env"))
load_env_file(os.path.join(os.path.dirname(BASE_DIR), "dtags-backend", ".env"))

LLM_URL = os.environ.get("LLM_URL", "https://litellm.talesofai.cn/v1/chat/completions")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "qwen3.5-plus-no-think")
LLM_FAST_MODEL = os.environ.get("LLM_FAST_MODEL", "qwen3.5-plus-no-think")
NETA_API_BASE_URL = os.environ.get("NETA_API_BASE_URL", API)

DEFAULT_ALLOWED_ORIGINS = {
    "https://xinsong854-sudo.github.io",
    "https://s-63a86395-de5c-46f9-a54d-0f7d02aa0671-3000.cohub.run",
}
# ═══════════ 数据库 ═══════════
def normalize_origin(value):
    try:
        u = urlparse(str(value or "").strip())
        if u.scheme != "https" or not u.netloc:
            return ""
        return f"{u.scheme}://{u.netloc}".rstrip("/")
    except Exception:
        return ""

def allowed_origins():
    extra = {normalize_origin(o) for o in os.environ.get("ALLOWED_ORIGINS", "").split(",") if o.strip()}
    return DEFAULT_ALLOWED_ORIGINS | {o for o in extra if o}

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
    # 身份卡/车卡为用户主动保存的站内数据，绑定 user_uuid；不包含用户 token。
    db.execute("""CREATE TABLE IF NOT EXISTS identity_cards(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_uuid TEXT NOT NULL,
        user_name TEXT,
        source_uuid TEXT,
        source_name TEXT,
        avatar_img TEXT,
        card_json TEXT NOT NULL,
        profile_json TEXT DEFAULT '{}',
        hp_current INTEGER DEFAULT 0,
        hp_max INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active',
        created_at INTEGER DEFAULT (strftime('%s','now')),
        updated_at INTEGER DEFAULT (strftime('%s','now'))
    )""")
    db.execute("CREATE INDEX IF NOT EXISTS idx_identity_user_status ON identity_cards(user_uuid,status,updated_at DESC)")
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
    images = [safe_public_url(x) for x in images][:9]
    images = [x for x in images if x]
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

# ═══════════ 前端由 dist/ 构建产物提供；不再保留旧版内联页面 fallback ═══════════

# ═══════════ 后端 API ═══════════
class Server(BaseHTTPRequestHandler):
    def _security_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()")
        self.send_header("Cross-Origin-Resource-Policy", "same-site")
        self.send_header("Content-Security-Policy", "default-src 'self' https: data: blob:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' https: data: blob:; connect-src 'self' https: wss:; frame-src https:; child-src https:; frame-ancestors 'self'; base-uri 'self'; form-action 'self'; object-src 'none'")

    def _cors_origin(self):
        origin = normalize_origin(self.headers.get("Origin", ""))
        return origin if origin in allowed_origins() else ""

    def _origin_allowed(self):
        origin = self.headers.get("Origin", "")
        # Non-browser/server-side requests may not include Origin; allow them.
        return not origin or bool(self._cors_origin())

    def _cors_headers(self):
        origin = self._cors_origin()
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "x-token, content-type")
        self.send_header("Access-Control-Max-Age", "600")

    def _json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._cors_headers()
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
        if not self._origin_allowed():
            self._json({"error": "Origin not allowed"}, 403); return
        self._json({})

    def do_GET(self):
        p = urlparse(self.path)
        if p.path.startswith("/api/"):
            token = clean_text(self.headers.get("x-token", ""), 4096)
            rate_key = token_user_key(token)
            max_count = RATE_LIMIT_MAX_AUTH if rate_key != "anon" else RATE_LIMIT_MAX_ANON
            if rate_limited_key(rate_key, max_count):
                self._json({"error": "请求过于频繁，请稍后再试"}, 429); return
        if not p.path.startswith("/api/"):
            if os.path.isdir(DIST_DIR) and os.path.isfile(os.path.join(DIST_DIR, "index.html")):
                self._serve_file(p.path)
            else:
                self.send_response(503); self.send_header("Content-Type", "text/plain; charset=utf-8"); self._security_headers(); self.end_headers()
                self.wfile.write("Frontend build missing. Run npm run build in pages/vue-app.".encode())
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
            db = get_db(); r = db.execute("SELECT role,avatar_frame,signature,title FROM members WHERE uuid=?", [uuid]).fetchone(); db.close()
            self._json({"role": r["role"] if r else "member", "avatar_frame": r["avatar_frame"] if r else "none", "signature": r["signature"] if r else "", "title": r["title"] if r else ""})
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
        elif p.path == "/api/identity-cards":
            token = self.headers.get("x-token", "")
            try:
                user = get_user_by_token(token)
            except Exception:
                self._json({"error": "未登录"}, 401); return
            db = get_db()
            rows = db.execute("SELECT * FROM identity_cards WHERE user_uuid=? AND status='active' ORDER BY updated_at DESC LIMIT 20", [user.get("uuid")]).fetchall()
            db.close()
            self._json([card_summary(r) for r in rows])
        elif p.path == "/api/member/identity-cards":
            uuid = clean_text(parse_qs(p.query).get("uuid", [""])[0], 80)
            if not uuid:
                self._json([], 200); return
            db = get_db()
            rows = db.execute("SELECT * FROM identity_cards WHERE user_uuid=? AND status='active' ORDER BY updated_at DESC LIMIT 3", [uuid]).fetchall()
            db.close()
            self._json([card_summary(r) for r in rows])
        elif p.path == "/api/member/identity-card":
            try:
                card_id = int(parse_qs(p.query).get("id", [0])[0] or 0)
            except Exception:
                self._json({"error": "参数错误"}, 400); return
            db = get_db()
            row = db.execute("SELECT * FROM identity_cards WHERE id=? AND status='active'", [card_id]).fetchone()
            db.close()
            if not row:
                self._json({"error": "车卡不存在"}, 404); return
            try: card = json.loads(row["card_json"] or "{}")
            except Exception: card = {}
            self._json({"summary": card_summary(row), "card": card})
        elif p.path.startswith("/api/identity-cards/"):
            token = self.headers.get("x-token", "")
            try:
                user = get_user_by_token(token)
                card_id = int(p.path.rsplit("/", 1)[-1])
            except Exception:
                self._json({"error": "未登录或参数错误"}, 401); return
            db = get_db()
            row = db.execute("SELECT * FROM identity_cards WHERE id=? AND user_uuid=?", [card_id, user.get("uuid")]).fetchone()
            db.close()
            if not row:
                self._json({"error": "车卡不存在"}, 404); return
            try: card = json.loads(row["card_json"] or "{}")
            except Exception: card = {}
            try: profile = json.loads(row["profile_json"] or "{}")
            except Exception: profile = {}
            self._json({"summary": card_summary(row), "card": card, "profile": profile})
        elif p.path == "/api/health":
            self._json({"ok": True, "service": "pseudo-human", "port": PORT})
        elif p.path == "/api/proxy/request-code" or p.path == "/api/proxy/verify-code":
            self.send_error(405)
        else:
            self.send_error(404)

    def do_POST(self):
        if not self._origin_allowed():
            self._json({"error": "Origin not allowed"}, 403); return
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length > MAX_BODY_BYTES:
            self._json({"error": "请求体过大"}, 413); return
        raw_body = self.rfile.read(length) if length > 0 else b"{}"
        try:
            body = json.loads(raw_body.decode("utf-8")) if raw_body else {}
            if not isinstance(body, dict):
                body = {}
        except Exception:
            self._json({"error": "JSON 格式错误"}, 400); return
        token = clean_text(self.headers.get("x-token", ""), 4096)
        p = urlparse(self.path)
        rate_key = token_user_key(token)
        max_count = RATE_LIMIT_MAX_AUTH if rate_key != "anon" else RATE_LIMIT_MAX_ANON
        if rate_limited_key(rate_key, max_count):
            self._json({"error": "请求过于频繁，请稍后再试"}, 429); return

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
            row = db.execute("SELECT signature,avatar_frame,role,title FROM members WHERE uuid=?", [uuid]).fetchone()
            db.commit(); db.close()
            self._json({"ok": True, "signature": row["signature"] if row else "", "avatar_frame": row["avatar_frame"] if row else "none", "role": row["role"] if row else "member", "title": row["title"] if row else ""})

        elif p.path == "/api/comments":
            if not token: self._json({"error": "未登录"}, 401); return
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10); r.raise_for_status(); user = r.json()
            except: self._json({"error": "令牌无效"}, 401); return
            eu = clean_text(body.get("entry_uuid", ""), 80); content = clean_text(body.get("content", ""), 2000)
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
            channel = clean_text(body.get("channel", ""), 80)
            content = clean_text(body.get("content", ""), 2000)
            images = body.get("images", [])
            if not isinstance(images, list): images = []
            images = [safe_public_url(x) for x in images][:9]
            images = [x for x in images if x]
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
            name = clean_text(body.get("name", ""), 30)
            desc = clean_text(body.get("desc", ""), 120) or "自定义地区分支。"
            code = clean_text(body.get("code", ""), 8) or "NEW"
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
            name = clean_text(body.get("name", ""), 30)
            if not name: db.close(); self._json({"error": "缺少分支名称"}, 400); return
            db.execute("DELETE FROM forum_channels WHERE name=?", [name]); db.commit(); db.close(); self._json({"ok": True})
        elif p.path == "/api/wiki/submissions":
            if not token: self._json({"error": "未登录"}, 401); return
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10); r.raise_for_status(); user = r.json()
            except Exception:
                self._json({"error": "令牌无效"}, 401); return
            target = str(body.get("target") or body.get("category") or "").strip()[:80]
            submit_type = clean_text(body.get("type", "新增词条"), 30)
            content = clean_text(body.get("content", ""), 5000)
            images = body.get("images", [])
            if not isinstance(images, list): images = []
            images = [safe_public_url(x) for x in images][:9]
            images = [x for x in images if x]
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
            title = clean_text(body.get("title", ""), 40)
            status = clean_text(body.get("status", "进行中"), 12) or "进行中"
            desc = clean_text(body.get("desc", ""), 300) or "暂无说明。"
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
            title = clean_text(body.get("title", ""), 30)
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
            signature = clean_text(body.get("signature", ""), 50)
            uuid = user.get("uuid", "")
            name = user.get("nick_name") or user.get("name", "")
            avatar = user.get("avatar_url", "")
            db = get_db()
            db.execute("INSERT OR IGNORE INTO members(uuid,name,avatar,role) VALUES(?,?,?,'member')", [uuid, name, avatar])
            db.execute("UPDATE members SET name=?, avatar=?, signature=?, online=1, last_seen=? WHERE uuid=?", [name, avatar, signature, int(time.time()), uuid])
            db.commit(); db.close()
            self._json({"ok": True, "signature": signature})
        elif p.path == "/api/neta/character-profile":
            user_token = token or str(body.get("token", ""))
            link = body.get("link") or body.get("uuid") or body.get("name") or ""
            try:
                profile = fetch_neta_character_profile(user_token, link)
                self._json({"success": True, "profile": profile})
            except Exception as e:
                self._json({"success": False, "error": str(e)}, 500)
        elif p.path == "/api/coc/character-card":
            user_token = token or str(body.get("token", ""))
            link = body.get("link") or body.get("uuid") or body.get("name") or ""
            try:
                user = get_user_by_token(user_token)
                db = get_db()
                active_count = db.execute("SELECT COUNT(*) FROM identity_cards WHERE user_uuid=? AND status='active'", [user.get("uuid")]).fetchone()[0]
                db.close()
                if active_count >= 3:
                    self._json({"success": False, "error": "每人最多保存三张身份卡，请先删除旧卡"}, 400); return
                profile = body.get("profile") if isinstance(body.get("profile"), dict) else fetch_neta_character_profile(user_token, link)
                card = generate_coc_card(profile)
                saved = save_identity_card_for_user(user, card, profile)
                self._json({"success": True, "profile": profile, "card": card, "saved": saved})
            except Exception as e:
                self._json({"success": False, "error": str(e)}, 500)
        elif p.path == "/api/identity-cards":
            try:
                user = get_user_by_token(token)
                card = body.get("card") if isinstance(body.get("card"), dict) else None
                profile = body.get("profile") if isinstance(body.get("profile"), dict) else {}
                if not card:
                    self._json({"error": "缺少车卡数据"}, 400); return
                saved = save_identity_card_for_user(user, card, profile)
                self._json({"ok": True, "card": saved})
            except Exception as e:
                self._json({"error": str(e)}, 500)
        elif p.path == "/api/identity-cards/delete":
            try:
                user = get_user_by_token(token)
                card_id = int(body.get("id", 0) or 0)
                db = get_db()
                db.execute("UPDATE identity_cards SET status='deleted', updated_at=strftime('%s','now') WHERE id=? AND user_uuid=?", [card_id, user.get("uuid")])
                db.commit(); db.close()
                self._json({"ok": True})
            except Exception as e:
                self._json({"error": str(e)}, 500)
        elif p.path == "/api/identity-cards/state":
            try:
                user = get_user_by_token(token)
                card_id = int(body.get("id", 0) or 0)
                hp_current = int(body.get("hp_current", 0))
                status = "torn" if hp_current <= 0 else "active"
                db = get_db()
                db.execute("UPDATE identity_cards SET hp_current=?, status=?, updated_at=strftime('%s','now') WHERE id=? AND user_uuid=?", [max(0, hp_current), status, card_id, user.get("uuid")])
                db.commit(); db.close()
                self._json({"ok": True, "status": status, "hp_current": max(0, hp_current)})
            except Exception as e:
                self._json({"error": str(e)}, 500)
        elif p.path == "/api/private/messages":
            if not token: self._json({"error": "未登录"}, 401); return
            try:
                r = requests.get(f"{API}/v1/user/", headers={"x-token": token}, timeout=10); r.raise_for_status(); user = r.json()
            except Exception:
                self._json({"error": "令牌无效"}, 401); return
            to_uuid = clean_text(body.get("to_uuid", ""), 80)
            content = clean_text(body.get("content", ""), 2000)
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
