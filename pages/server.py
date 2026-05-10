#!/usr/bin/env python3
"""伪人大本营 minimal backend — site sessions only, never stores Neta tokens."""
import base64, json, os, re, secrets, sqlite3, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote

PORT = int(os.environ.get('PORT', '3000'))
BASE_DIR = os.path.dirname(__file__) or '.'
DIST_DIR = os.path.join(BASE_DIR, 'dist')
DB = os.path.join(BASE_DIR, 'pseudo_human.db')
MAX_BODY_BYTES = 1024 * 1024
SESSION_TTL = 7 * 24 * 3600
SESSIONS = {}


def clean(v, limit=2000):
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', str(v or '')).strip()[:limit]


def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA journal_mode=WAL')
    return con


def init_db():
    con = db()
    con.execute('''CREATE TABLE IF NOT EXISTS members(
        uuid TEXT PRIMARY KEY, name TEXT, avatar TEXT, role TEXT DEFAULT 'member', title TEXT DEFAULT '',
        signature TEXT DEFAULT '', avatar_frame TEXT DEFAULT 'none', creator_uuid TEXT DEFAULT '', exp INTEGER DEFAULT 0,
        online INTEGER DEFAULT 0, last_seen INTEGER, joined_at INTEGER DEFAULT (strftime('%s','now'))
    )''')
    for col, ddl in [
        ('title', "ALTER TABLE members ADD COLUMN title TEXT DEFAULT ''"),
        ('signature', "ALTER TABLE members ADD COLUMN signature TEXT DEFAULT ''"),
        ('avatar_frame', "ALTER TABLE members ADD COLUMN avatar_frame TEXT DEFAULT 'none'"),
        ('creator_uuid', "ALTER TABLE members ADD COLUMN creator_uuid TEXT DEFAULT ''"),
        ('exp', "ALTER TABLE members ADD COLUMN exp INTEGER DEFAULT 0"),
    ]:
        try: con.execute(ddl)
        except sqlite3.OperationalError: pass
    con.execute('''CREATE TABLE IF NOT EXISTS forum_posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT, channel TEXT, user_uuid TEXT, user_name TEXT, user_avatar TEXT,
        content TEXT, images_json TEXT DEFAULT '[]', revoked INTEGER DEFAULT 0, created_at INTEGER DEFAULT (strftime('%s','now'))
    )''')
    con.execute('''CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT, entry_uuid TEXT, user_uuid TEXT, user_name TEXT, user_avatar TEXT,
        content TEXT, created_at INTEGER DEFAULT (strftime('%s','now'))
    )''')
    con.execute('''CREATE TABLE IF NOT EXISTS identity_cards(
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_uuid TEXT, user_name TEXT, source_uuid TEXT, source_name TEXT,
        avatar_img TEXT, card_json TEXT, profile_json TEXT, hp_current INTEGER DEFAULT 10, hp_max INTEGER DEFAULT 10,
        status TEXT DEFAULT 'active', created_at INTEGER DEFAULT (strftime('%s','now')), updated_at INTEGER DEFAULT (strftime('%s','now'))
    )''')
    con.execute('CREATE INDEX IF NOT EXISTS idx_identity_user_status ON identity_cards(user_uuid,status,updated_at DESC)')
    con.execute('''CREATE TABLE IF NOT EXISTS wiki_submissions(
        id INTEGER PRIMARY KEY AUTOINCREMENT, target TEXT, submit_type TEXT, content TEXT, images_json TEXT DEFAULT '[]',
        user_uuid TEXT, user_name TEXT, status TEXT DEFAULT 'pending', created_at INTEGER DEFAULT (strftime('%s','now'))
    )''')
    con.execute('''CREATE TABLE IF NOT EXISTS private_messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT, from_uuid TEXT, to_uuid TEXT, from_name TEXT, from_avatar TEXT,
        content TEXT, created_at INTEGER DEFAULT (strftime('%s','now'))
    )''')
    con.commit(); con.close()


def session_create(user):
    sid = secrets.token_urlsafe(32)
    safe_user = {
        'uuid': clean(user.get('uuid'), 80),
        'name': clean(user.get('name') or user.get('nick_name'), 120),
        'nick_name': clean(user.get('nick_name') or user.get('name'), 120),
        'avatar_url': clean(user.get('avatar_url') or user.get('avatar'), 500),
        'creator_uuid': clean(user.get('creator_uuid') or user.get('uuid'), 80),
    }
    SESSIONS[sid] = {'user': safe_user, 'exp': time.time() + SESSION_TTL}
    return 'sess_' + sid


def session_user(token):
    if not str(token or '').startswith('sess_'):
        raise ValueError('未登录')
    sid = token[5:]
    data = SESSIONS.get(sid)
    if not data or data.get('exp', 0) < time.time():
        SESSIONS.pop(sid, None)
        raise ValueError('登录已过期')
    return dict(data['user'])



def extract_uuid(text):
    m = re.search(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', str(text or ''))
    return m.group(0) if m else ''

def extract_short_url(text):
    m = re.search(r'https?://t\.nieta\.art/[a-zA-Z0-9]+', str(text or ''))
    return m.group(0) if m else ''

def resolve_original_url(text):
    short = extract_short_url(text)
    if not short:
        return str(text or '')
    import requests
    r = requests.get('https://api.talesofai.cn/v1/util/original-url', params={'short_url': short}, timeout=10)
    data = r.json()
    if not r.ok:
        raise ValueError((data or {}).get('detail') or '短链解析失败')
    return data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)

def resolve_knight(raw):
    import requests
    text = resolve_original_url(raw)
    uuid = extract_uuid(text)
    if not uuid:
        raise ValueError('未找到角色 UUID')
    r = requests.get(f'https://api.talesofai.cn/v2/travel/parent/{uuid}/profile', headers={
        'x-platform': 'nieta-app/web',
        'x-nieta-app-version': '6.8.9',
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0'
    }, timeout=10)
    data = r.json()
    if not r.ok:
        raise ValueError(data.get('detail') or data.get('error') or '角色查询失败')
    author = data.get('owner_profile') or data.get('creator') or {}
    cfg = data.get('config') or {}
    bio = cfg.get('char_info') or data.get('oc_bio') or {}
    return {
        'oc': {
            'uuid': data.get('uuid') or uuid,
            'name': data.get('name') or data.get('short_name') or '',
            'short_name': data.get('short_name') or '',
            'gender': data.get('gender') or '',
            'status': data.get('status') or '',
            'accessibility': data.get('accessibility') or '',
            'heat_score': data.get('heat_score') or 0,
            'hashtags': data.get('hashtags') or data.get('tags') or [],
            'avatar_img': cfg.get('avatar_img') or data.get('avatar_img') or '',
            'header_img': cfg.get('header_img') or '',
            'bio_summary': {
                'age': bio.get('age') or '',
                'persona': bio.get('tone') if bio.get('tone') != 'not_available' else '',
                'background': bio.get('background') if bio.get('background') != 'not_available' else (cfg.get('travel_preview') or data.get('description') or '')
            }
        },
        'author': {
            'uuid': author.get('uuid') or '',
            'nick_name': author.get('nick_name') or author.get('name') or '未知用户',
            'avatar_url': author.get('avatar_url') or author.get('avatar') or '',
            'subscriber_count': author.get('subscriber_count') or 0,
            'story_count': author.get('story_count') or 0
        },
        'raw': data
    }

def make_card(profile):
    name = clean(profile.get('name') or profile.get('oc_bio', {}).get('name') or '未命名角色', 120)
    desc = clean(profile.get('description') or profile.get('oc_bio', {}).get('description') or profile.get('persona') or '', 4000)
    avatar = clean(profile.get('avatar_img') or profile.get('avatar') or profile.get('config', {}).get('avatar_img') or '', 500)
    return {
        'source_character': {'uuid': clean(profile.get('uuid'), 80), 'name': name, 'avatar_img': avatar},
        'investigator': {'name': name, 'occupation': clean(profile.get('occupation') or '伪人', 80), 'age': clean(profile.get('age') or '未知', 40)},
        'portrait': {'avatar_img': avatar, 'visual_summary': desc[:160]},
        'derived': {'HP': 10, 'SAN': 50, 'MP': 10, 'MOV': 8},
        'roleplay': {'description': desc, 'persona': clean(profile.get('persona') or desc, 2000), 'interests': clean(profile.get('interests'), 1000)}
    }


def json_response(handler, data, status=200):
    raw = json.dumps(data, ensure_ascii=False).encode()
    handler.send_response(status)
    handler.security_headers()
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Content-Length', str(len(raw)))
    handler.end_headers(); handler.wfile.write(raw)


class Server(BaseHTTPRequestHandler):
    def security_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'x-session, content-type')
        self.send_header('Access-Control-Max-Age', '600')
        self.send_header('Content-Security-Policy', "default-src 'self' https: data: blob:; script-src 'self' 'unsafe-inline' https:; style-src 'self' 'unsafe-inline' https:; img-src 'self' https: data: blob:; connect-src 'self' https:; frame-src https:; object-src 'none'")

    def send_json(self, data, status=200): json_response(self, data, status)

    def do_OPTIONS(self): self.send_json({})

    def read_body(self):
        n = int(self.headers.get('Content-Length', '0') or 0)
        if n > MAX_BODY_BYTES: raise ValueError('请求体过大')
        if not n: return {}
        data = json.loads(self.rfile.read(n).decode('utf-8'))
        return data if isinstance(data, dict) else {}

    def user(self): return session_user(clean(self.headers.get('x-session') or self.headers.get('x-token'), 4096))

    def serve_file(self, path):
        rel = unquote(urlparse(path).path).lstrip('/') or 'index.html'
        rel = 'index.html' if rel in ('', '/') else rel
        full = os.path.abspath(os.path.join(DIST_DIR, rel))
        root = os.path.abspath(DIST_DIR)
        if not full.startswith(root) or not os.path.isfile(full):
            full = os.path.join(root, 'index.html')
        ctype = 'text/html; charset=utf-8'
        if full.endswith('.js'): ctype = 'application/javascript; charset=utf-8'
        elif full.endswith('.css'): ctype = 'text/css; charset=utf-8'
        elif full.endswith('.png'): ctype = 'image/png'
        raw = open(full, 'rb').read()
        self.send_response(200); self.security_headers(); self.send_header('Content-Type', ctype); self.send_header('Content-Length', str(len(raw))); self.end_headers(); self.wfile.write(raw)

    def do_GET(self):
        p = urlparse(self.path)
        if not p.path.startswith('/api/'):
            return self.serve_file(self.path)
        try:
            if p.path == '/api/health': return self.send_json({'ok': True})
            if p.path == '/api/session': return self.send_json({'ok': True, 'me': self.user()})
            if p.path == '/api/knight/resolve':
                q = parse_qs(p.query).get('uuid', [''])[0] or parse_qs(p.query).get('url', [''])[0]
                return self.send_json(resolve_knight(q))
            if p.path == '/api/profile':
                u=self.user(); con=db(); r=con.execute("SELECT signature,avatar_frame,role,title FROM members WHERE uuid=?",[u['uuid']]).fetchone(); con.close(); return self.send_json({'signature':r['signature'] if r else '', 'avatar_frame':r['avatar_frame'] if r else 'none', 'role':r['role'] if r else 'member', 'title':r['title'] if r else ''})
            if p.path == '/api/members':
                con = db(); rows = con.execute('SELECT uuid,name,avatar,role,title,signature,creator_uuid,avatar_frame,COALESCE(exp,0) exp,online,last_seen FROM members ORDER BY online DESC,last_seen DESC,name').fetchall(); con.close()
                return self.send_json([dict(r) for r in rows])
            if p.path == '/api/forum/posts':
                channel = clean(parse_qs(p.query).get('channel', ['主论坛'])[0], 80)
                con = db(); rows = con.execute('SELECT * FROM forum_posts WHERE channel=? AND revoked=0 ORDER BY created_at DESC LIMIT 120', [channel]).fetchall(); con.close()
                out=[]
                for r in rows:
                    d=dict(r)
                    try: d['images']=json.loads(d.pop('images_json') or '[]')
                    except Exception: d['images']=[]
                    out.append(d)
                return self.send_json(out)
            if p.path == '/api/wiki/submissions':
                u=self.user(); con=db(); role=con.execute('SELECT role FROM members WHERE uuid=?',[u['uuid']]).fetchone(); status=clean(parse_qs(p.query).get('status',['pending'])[0],20)
                if not role or role['role'] not in ('chief','deputy','admin'): con.close(); return self.send_json([])
                rows=con.execute('SELECT * FROM wiki_submissions WHERE status=? ORDER BY created_at DESC LIMIT 100',[status]).fetchall(); con.close(); return self.send_json([dict(r) for r in rows])
            if p.path == '/api/identity-cards':
                u = self.user(); con = db(); rows = con.execute("SELECT * FROM identity_cards WHERE user_uuid=? AND status='active' ORDER BY updated_at DESC", [u['uuid']]).fetchall(); con.close()
                return self.send_json([self.card_summary(r) for r in rows])
            if p.path.startswith('/api/identity-cards/'):
                u = self.user(); cid = int(p.path.rsplit('/',1)[-1]); con = db(); r = con.execute('SELECT * FROM identity_cards WHERE id=? AND user_uuid=?', [cid, u['uuid']]).fetchone(); con.close()
                if not r: return self.send_json({'error':'不存在'},404)
                return self.send_json({'summary': self.card_summary(r), 'card': json.loads(r['card_json'] or '{}'), 'profile': json.loads(r['profile_json'] or '{}')})
            return self.send_json({'error': 'Not Found'}, 404)
        except Exception as e:
            return self.send_json({'error': str(e)}, 401)

    def card_summary(self, r):
        card = json.loads(r['card_json'] or '{}')
        return {'id': r['id'], 'source_uuid': r['source_uuid'], 'source_name': r['source_name'], 'avatar_img': r['avatar_img'], 'investigator': card.get('investigator') or {}, 'hp_current': r['hp_current'], 'hp_max': r['hp_max'], 'created_at': r['created_at'], 'updated_at': r['updated_at']}

    def do_POST(self):
        try: body = self.read_body()
        except Exception as e: return self.send_json({'error': str(e)}, 400)
        p = urlparse(self.path)
        try:
            if p.path == '/api/session/create':
                user = body.get('user') if isinstance(body.get('user'), dict) else {}
                if not user.get('uuid'): return self.send_json({'error':'缺少用户 UUID'},400)
                sess = session_create(user)
                u = SESSIONS[sess[5:]]['user']
                con = db(); con.execute("INSERT OR IGNORE INTO members(uuid,name,avatar,role,creator_uuid) VALUES(?,?,?,'member',?)", [u['uuid'], u['nick_name'], u['avatar_url'], u['creator_uuid']]); con.execute('UPDATE members SET name=?,avatar=?,creator_uuid=COALESCE(NULLIF(creator_uuid,\'\'),?),online=1,last_seen=? WHERE uuid=?', [u['nick_name'], u['avatar_url'], u['creator_uuid'], int(time.time()), u['uuid']]); row = con.execute('SELECT role,title,signature FROM members WHERE uuid=?',[u['uuid']]).fetchone(); con.commit(); con.close()
                return self.send_json({'ok': True, 'session': sess, 'me': u, 'role': row['role'] if row else 'member', 'title': row['title'] if row else '', 'signature': row['signature'] if row else ''})
            if p.path == '/api/profile':
                u=self.user(); sig=clean(body.get('signature'),80); frame=clean(body.get('avatar_frame') or 'none',20); con=db(); con.execute('UPDATE members SET signature=?,avatar_frame=? WHERE uuid=?',[sig,frame,u['uuid']]); con.commit(); con.close(); return self.send_json({'ok':True,'signature':sig,'avatar_frame':frame,'me':{'signature':sig,'avatar_frame':frame}})
            if p.path == '/api/wiki/submissions':
                u=self.user(); target=clean(body.get('target'),80); submit_type=clean(body.get('submit_type') or '新增词条',20); title=clean(body.get('title'),120); content=clean(body.get('content'),5000)
                if not target or not content: return self.send_json({'error':'缺少分类或正文'},400)
                con=db(); con.execute('INSERT INTO wiki_submissions(target,submit_type,content,user_uuid,user_name) VALUES(?,?,?,?,?)',[target,submit_type,(f'【{title}】\n' if title else '')+content,u['uuid'],u['nick_name']]); con.commit(); con.close(); return self.send_json({'ok':True})
            if p.path == '/api/wiki/review':
                u=self.user(); con=db(); role=con.execute('SELECT role FROM members WHERE uuid=?',[u['uuid']]).fetchone()
                if not role or role['role'] not in ('chief','deputy','admin'): con.close(); return self.send_json({'error':'权限不足'},403)
                sid=int(body.get('id') or 0); action='approved' if body.get('action')=='approved' else 'rejected'; con.execute('UPDATE wiki_submissions SET status=? WHERE id=?',[action,sid]); con.commit(); con.close(); return self.send_json({'ok':True,'status':action})
            if p.path == '/api/forum/posts':
                u = self.user(); channel=clean(body.get('channel') or '主论坛',80); content=clean(body.get('content'),2000); images=body.get('images') if isinstance(body.get('images'),list) else []
                role_id = int(body.get('role_card_id') or 0)
                post_name, post_avatar = u['nick_name'], u['avatar_url']
                con=db()
                if role_id:
                    rr=con.execute("SELECT source_name,avatar_img FROM identity_cards WHERE id=? AND user_uuid=? AND status='active'",[role_id,u['uuid']]).fetchone()
                    if not rr: con.close(); return self.send_json({'error':'角色卡不存在或不属于当前用户'},403)
                    post_name, post_avatar = rr['source_name'], rr['avatar_img']
                if not content and not images: con.close(); return self.send_json({'error':'缺少内容'},400)
                con.execute('INSERT INTO forum_posts(channel,user_uuid,user_name,user_avatar,content,images_json) VALUES(?,?,?,?,?,?)',[channel,u['uuid'],post_name,post_avatar,content,json.dumps(images[:9],ensure_ascii=False)]); con.execute('UPDATE members SET online=1,last_seen=? WHERE uuid=?',[int(time.time()),u['uuid']]); con.commit(); con.close(); return self.send_json({'ok':True})
            if p.path == '/api/identity-cards':
                u=self.user(); profile=body.get('profile') if isinstance(body.get('profile'),dict) else {}; creator=clean(profile.get('creator_uuid') or profile.get('owner_uuid') or profile.get('from_user'),80)
                if creator and creator != clean(u.get('creator_uuid') or u.get('uuid'),80): return self.send_json({'error':'你不是Ta，你扮演不了Ta'},403)
                card=body.get('card') if isinstance(body.get('card'),dict) else make_card(profile)
                hp=int(card.get('derived',{}).get('HP') or 10); src=card.get('source_character') or {}
                con=db(); con.execute('INSERT INTO identity_cards(user_uuid,user_name,source_uuid,source_name,avatar_img,card_json,profile_json,hp_current,hp_max) VALUES(?,?,?,?,?,?,?,?,?)',[u['uuid'],u['nick_name'],clean(profile.get('uuid') or src.get('uuid'),80),clean(profile.get('name') or card.get('investigator',{}).get('name') or '未命名角色',120),clean(profile.get('avatar_img') or card.get('portrait',{}).get('avatar_img'),500),json.dumps(card,ensure_ascii=False),json.dumps(profile,ensure_ascii=False),hp,hp]); r=con.execute('SELECT * FROM identity_cards WHERE id=last_insert_rowid()').fetchone(); con.commit(); con.close(); return self.send_json({'ok':True,'card':self.card_summary(r)})
            if p.path == '/api/identity-cards/delete':
                u=self.user(); cid=int(body.get('id') or 0); con=db(); con.execute("UPDATE identity_cards SET status='deleted' WHERE id=? AND user_uuid=?",[cid,u['uuid']]); con.commit(); con.close(); return self.send_json({'ok':True})
            if p.path == '/api/comments':
                u=self.user(); eu=clean(body.get('entry_uuid'),80); content=clean(body.get('content'),2000); con=db(); con.execute('INSERT INTO comments(entry_uuid,user_uuid,user_name,user_avatar,content) VALUES(?,?,?,?,?)',[eu,u['uuid'],u['nick_name'],u['avatar_url'],content]); con.commit(); con.close(); return self.send_json({'ok':True})
            return self.send_json({'error':'Not Found'},404)
        except Exception as e:
            return self.send_json({'error': str(e)}, 500)

    def log_message(self, *a): pass


if __name__ == '__main__':
    init_db(); print(f'http://0.0.0.0:{PORT}'); HTTPServer(('0.0.0.0', PORT), Server).serve_forever()
