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
        ('benzhen', "ALTER TABLE members ADD COLUMN benzhen INTEGER DEFAULT 0"),
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
    con.execute('''CREATE TABLE IF NOT EXISTS inventory_artifacts(
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_uuid TEXT, artifact_key TEXT, name TEXT, risk TEXT, rarity TEXT,
        description TEXT, effect TEXT, uses INTEGER DEFAULT -1, obtained_from TEXT, created_at INTEGER DEFAULT (strftime('%s','now')),
        card_id INTEGER DEFAULT 0, status TEXT DEFAULT 'owned', metadata_json TEXT DEFAULT '{}'
    )''')
    for ddl in [
        "ALTER TABLE inventory_artifacts ADD COLUMN card_id INTEGER DEFAULT 0",
        "ALTER TABLE inventory_artifacts ADD COLUMN status TEXT DEFAULT 'owned'",
        "ALTER TABLE inventory_artifacts ADD COLUMN metadata_json TEXT DEFAULT '{}'",
    ]:
        try: con.execute(ddl)
        except sqlite3.OperationalError: pass
    con.execute('''CREATE TABLE IF NOT EXISTS codex_entries(
        uuid TEXT PRIMARY KEY, category TEXT DEFAULT '伪物档案', name TEXT, risk TEXT DEFAULT 'unknown', artifact_code TEXT DEFAULT '',
        description TEXT, image TEXT DEFAULT '', source TEXT DEFAULT 'submission', status TEXT DEFAULT 'approved',
        user_uuid TEXT DEFAULT '', user_name TEXT DEFAULT '', tags_json TEXT DEFAULT '[]', created_at INTEGER DEFAULT (strftime('%s','now')),
        approved_at INTEGER DEFAULT 0
    )''')
    con.execute('''CREATE TABLE IF NOT EXISTS identity_card_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT, card_id INTEGER, user_uuid TEXT, event_type TEXT, content TEXT,
        delta_json TEXT DEFAULT '{}', created_at INTEGER DEFAULT (strftime('%s','now'))
    )''')
    con.execute('''CREATE TABLE IF NOT EXISTS character_abilities(
        id INTEGER PRIMARY KEY AUTOINCREMENT, card_id INTEGER, user_uuid TEXT, name TEXT, source TEXT, scope TEXT,
        effect TEXT, cost TEXT DEFAULT '', status TEXT DEFAULT 'active', created_at INTEGER DEFAULT (strftime('%s','now'))
    )''')
    con.execute('''CREATE TABLE IF NOT EXISTS explore_runs(
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_uuid TEXT, card_id INTEGER, card_name TEXT, artifact_id INTEGER,
        area TEXT, danger TEXT, dice INTEGER, result TEXT, reward INTEGER, artifact_json TEXT DEFAULT '{}', created_at INTEGER DEFAULT (strftime('%s','now'))
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


ARTIFACT_POOL = [
    {'key':'tap-tv','name':'拍一拍才能用的电视机','risk':'safe','rarity':'common','description':'一台必须被轻拍三次才会亮起的老电视。只会播放用户三秒前错过的画面。','effect':'探索中可获得一次轻微信息提示。'},
    {'key':'shy-key','name':'害羞钥匙','risk':'safe','rarity':'common','description':'当有人盯着它看时就打不开门。闭眼时反而很配合。','effect':'探索中遇到门类事件时 +5。'},
    {'key':'warm-receipt','name':'会发热的小票','risk':'caution','rarity':'uncommon','description':'记录着你尚未购买的东西。越接近对应物品，小票越烫。','effect':'探索结束本真奖励 +2。'},
    {'key':'wrong-map','name':'差一条街地图','risk':'caution','rarity':'uncommon','description':'永远能把你带到目的地旁边一条街。安全，但非常气人。','effect':'降低迷路惩罚。'},
    {'key':'polite-stone','name':'很有礼貌的石头','risk':'safe','rarity':'rare','description':'每次被捡起都会说谢谢。放下时会道歉。偶尔替你回答危险问题。','effect':'探索中一次社交检定 +10。'},
    {'key':'borrowed-shadow','name':'借来的影子','risk':'danger','rarity':'rare','description':'它比你慢半拍，但在你害怕时会先一步逃跑。','effect':'危险事件可抵消一次伤害，但可能带来怪异记录。'},
    {'key':'eye-thread','name':'眼线残丝','risk':'hazard','rarity':'legendary','description':'一缕像视线一样的丝线。握住时，你会知道某处也正在看你。','effect':'高危探索中大幅提高发现稀有伪物概率。'},
]
AREAS = ['槐安公寓夹层','电子屏门后','旧哨站走廊','误入的纸盒里界','风暴海岸边缘','错位花园温室','无人层 03:18','非常电影院后台']
DANGERS = ['🟩SAFE','🟨CAUTION','🟧DANGER','🟥HAZARD']

def rarity_weight(item):
    return {'common':55,'uncommon':28,'rare':13,'legendary':4}.get(item.get('rarity'),20)

def choose_artifact(boost=0):
    import random
    weights=[]
    for it in ARTIFACT_POOL:
        w=rarity_weight(it)
        if boost and it['rarity'] in ('rare','legendary'):
            w += boost
        weights.append(w)
    return random.choices(ARTIFACT_POOL, weights=weights, k=1)[0]

def add_artifact(con, user_uuid, item, source, card_id=0):
    meta = {k:item.get(k) for k in ('forum_usage','origin','usage_condition','side_effect') if item.get(k)}
    con.execute("""INSERT INTO inventory_artifacts(user_uuid,artifact_key,name,risk,rarity,description,effect,obtained_from,card_id,metadata_json)
                   VALUES(?,?,?,?,?,?,?,?,?,?)""", [user_uuid,item['key'],item['name'],item['risk'],item['rarity'],item['description'],item['effect'],source,int(card_id or 0),json.dumps(meta,ensure_ascii=False)])
    return con.execute('SELECT * FROM inventory_artifacts WHERE id=last_insert_rowid()').fetchone()

def artifact_row(r):
    d = dict(r)
    if d.get('metadata_json'):
        try: d['metadata'] = json.loads(d['metadata_json'] or '{}')
        except Exception: d['metadata'] = {}
    return d

def parse_submission_title(content):
    text = str(content or '').strip()
    m = re.match(r'【(.{1,120}?)】\n?', text)
    if m:
        return clean(m.group(1), 120), clean(text[m.end():], 6000)
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    return clean(lines[0] if lines else '未命名条目', 120), clean(text, 6000)

def infer_risk(text):
    t = str(text or '').lower()
    if re.search(r'🟥|hazard|危害|高危|禁忌|白墟', t): return 'hazard'
    if re.search(r'🟧|danger|危险|致命|猎人|对伪课', t): return 'danger'
    if re.search(r'🟨|caution|注意|谨慎|污染|侵蚀|副作用', t): return 'caution'
    if re.search(r'🟩|safe|安全|无害|正常保管', t): return 'safe'
    return 'unknown'

def codex_row(r):
    d = dict(r)
    try: d['tags'] = json.loads(d.get('tags_json') or '[]')
    except Exception: d['tags'] = []
    d.pop('tags_json', None)
    return d

def generated_artifact(context=None):
    import random
    context = context or {}
    areas = ['槐安公寓夹层','非常电影院后台','桃花堂暗柜','天风阁封门楼层','旧哨站走廊','风暴海雨幕','错位花园温室','白墟边境','渡鱼二手图书馆']
    forms = ['小票','钥匙','旧相机','纽扣','玻璃杯','纸伞','耳机','打火机','门牌','折纸鸟','空白证件','发条鱼']
    quirks = ['总是慢三秒','只在雨声里说话','会记住上一个持有者的体温','照不出正面','把影子折成两半','闻起来像旧书','写下不存在的地址','会替你礼貌道歉','在谎言附近发热','看久了会眨眼']
    effects = ['揭示一次被遮蔽的线索','让一次危险检定获得加值','为论坛发帖添加一段仅灵视可见的残文','抵消一次轻微伤害','把一条探索记录转写成图鉴线索','短暂稳定濒临污染的身份卡']
    side = ['使用后失去 1 点 SAN','下一次发帖时间显示错误','角色履历增加一条异常注视','24 小时内无法再次使用','有小概率令伪物绑定到当前身份卡','会把一句普通话改写成反文']
    rarity = random.choices(['common','uncommon','rare','legendary'], [52,30,14,4], k=1)[0]
    risk = {'common':'safe','uncommon':'caution','rare':'danger','legendary':'hazard'}[rarity]
    form=random.choice(forms); place=random.choice(areas)
    name = random.choice(['不肯闭眼的','迟到的','半透明的','温热的','借来的','回声里的','写错名字的','没有主人的']) + form
    return {
        'key': 'llm-' + secrets.token_hex(6), 'name': name, 'risk': risk, 'rarity': rarity,
        'description': f'发现地点：{place}\n外观：一件{form}，{random.choice(quirks)}。它不像被制造出来的，更像是从某段未归档的论坛记录里掉出来的。\n来源传闻：{context.get("card_name") or "某位探索者"}在门的另一侧听见有人呼唤自己的网名后，于返回时发现它已经在口袋里。',
        'effect': f'{random.choice(effects)}。副作用：{random.choice(side)}。',
        'forum_usage': random.choice(['发帖时可插入一段“异常旁白”','评论时可尝试解读一条隐藏残文','使本帖获得一次轻微污染视觉效果','让角色名旁短暂显示伪物共鸣标记']),
        'origin': place,
    }


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
            if p.path == '/api/codex/entries':
                risk=clean(parse_qs(p.query).get('risk',[''])[0],20); con=db()
                if risk: rows=con.execute("SELECT * FROM codex_entries WHERE status='approved' AND risk=? ORDER BY approved_at DESC,created_at DESC",[risk]).fetchall()
                else: rows=con.execute("SELECT * FROM codex_entries WHERE status='approved' ORDER BY approved_at DESC,created_at DESC").fetchall()
                con.close(); return self.send_json([codex_row(r) for r in rows])
            if p.path == '/api/inventory':
                u=self.user(); con=db(); rows=con.execute('SELECT * FROM inventory_artifacts WHERE user_uuid=? ORDER BY created_at DESC,id DESC',[u['uuid']]).fetchall(); bal=con.execute('SELECT COALESCE(benzhen,0) AS benzhen FROM members WHERE uuid=?',[u['uuid']]).fetchone(); con.close(); return self.send_json({'benzhen':int(bal['benzhen'] if bal else 0),'items':[artifact_row(r) for r in rows]})
            if p.path == '/api/explore/runs':
                u=self.user(); con=db(); rows=con.execute('SELECT * FROM explore_runs WHERE user_uuid=? ORDER BY created_at DESC LIMIT 30',[u['uuid']]).fetchall(); con.close(); return self.send_json([dict(r) for r in rows])
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
            if p.path == '/api/proxy/request-code':
                import requests
                r=requests.post('https://api.talesofai.cn/v1/user/request-verification-code', json=body, timeout=15, headers={'Accept':'application/json','Content-Type':'application/json','Origin':'https://app.nieta.art','Referer':'https://app.nieta.art/','User-Agent':'Mozilla/5.0'})
                return self.send_json(r.json() if r.text else {}, r.status_code)
            if p.path == '/api/proxy/verify-code':
                import requests
                r=requests.post('https://api.talesofai.cn/v1/user/verify-with-phone-num', json=body, timeout=15, headers={'Accept':'application/json','Content-Type':'application/json','Origin':'https://app.nieta.art','Referer':'https://app.nieta.art/','User-Agent':'Mozilla/5.0'})
                return self.send_json(r.json() if r.text else {}, r.status_code)
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
                images=body.get('images') if isinstance(body.get('images'),list) else []
                if not target or not content: return self.send_json({'error':'缺少分类或正文'},400)
                con=db(); con.execute('INSERT INTO wiki_submissions(target,submit_type,content,images_json,user_uuid,user_name) VALUES(?,?,?,?,?,?)',[target,submit_type,(f'【{title}】\n' if title else '')+content,json.dumps(images[:6],ensure_ascii=False),u['uuid'],u['nick_name']]); con.commit(); con.close(); return self.send_json({'ok':True})
            if p.path == '/api/codex/submit':
                u=self.user(); name=clean(body.get('name'),120); risk=clean(body.get('risk') or 'unknown',20); desc=clean(body.get('description'),6000); image=clean(body.get('image'),500)
                if not name or not desc: return self.send_json({'error':'缺少名称或档案正文'},400)
                con=db(); con.execute('INSERT INTO wiki_submissions(target,submit_type,content,images_json,user_uuid,user_name) VALUES(?,?,?,?,?,?)',['伪物档案','图鉴投稿',f'【{name}】\n风险等级：{risk}\n'+desc,json.dumps([image] if image else [],ensure_ascii=False),u['uuid'],u['nick_name']]); con.commit(); con.close(); return self.send_json({'ok':True})
            if p.path == '/api/wiki/review':
                u=self.user(); con=db(); role=con.execute('SELECT role FROM members WHERE uuid=?',[u['uuid']]).fetchone()
                if not role or role['role'] not in ('chief','deputy','admin'): con.close(); return self.send_json({'error':'权限不足'},403)
                sid=int(body.get('id') or 0); action='approved' if body.get('action')=='approved' else 'rejected'
                sub=con.execute('SELECT * FROM wiki_submissions WHERE id=?',[sid]).fetchone()
                con.execute('UPDATE wiki_submissions SET status=? WHERE id=?',[action,sid])
                if action=='approved' and sub and sub['target'] in ('伪物档案','图鉴','伪物图鉴'):
                    name, desc = parse_submission_title(sub['content'])
                    try: imgs=json.loads(sub['images_json'] or '[]')
                    except Exception: imgs=[]
                    risk=infer_risk(desc); m=re.search(r'(SA|CA|DA|HA|UN)-?\d{1,4}', desc, re.I); code=m.group(0).upper() if m else ''
                    con.execute('''INSERT OR REPLACE INTO codex_entries(uuid,category,name,risk,artifact_code,description,image,source,status,user_uuid,user_name,approved_at)
                                   VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''',[f'sub-{sid}','伪物档案',name,risk,code,desc,imgs[0] if imgs else '','submission','approved',sub['user_uuid'],sub['user_name'],int(time.time())])
                    item=generated_artifact({'card_name':sub['user_name']}); item['name']=name if len(name)<=40 else item['name']; item['risk']=risk if risk!='unknown' else item['risk']; item['description']=desc[:1800] or item['description']
                    add_artifact(con, sub['user_uuid'], item, '图鉴投稿收录')
                    con.execute('UPDATE members SET benzhen=COALESCE(benzhen,0)+30 WHERE uuid=?',[sub['user_uuid']])
                con.commit(); con.close(); return self.send_json({'ok':True,'status':action})
            if p.path == '/api/artifacts/draw':
                u=self.user(); con=db(); bal=con.execute('SELECT COALESCE(benzhen,0) AS benzhen FROM members WHERE uuid=?',[u['uuid']]).fetchone(); benzhen=int(bal['benzhen'] if bal else 0)
                if benzhen < 20: con.close(); return self.send_json({'error':'本真不足，需要 20'},400)
                item=generated_artifact({'card_name':u.get('nick_name')}); row=add_artifact(con,u['uuid'],item,'本真抽取'); con.execute('UPDATE members SET benzhen=COALESCE(benzhen,0)-20 WHERE uuid=?',[u['uuid']]); bal=con.execute('SELECT COALESCE(benzhen,0) AS benzhen FROM members WHERE uuid=?',[u['uuid']]).fetchone(); con.commit(); con.close(); return self.send_json({'ok':True,'item':artifact_row(row),'benzhen':int(bal['benzhen'] if bal else 0)})
            if p.path == '/api/explore/run':
                import random
                u=self.user(); card_id=int(body.get('card_id') or 0); artifact_id=int(body.get('artifact_id') or 0); con=db(); card=None; art=None
                if card_id: card=con.execute("SELECT source_name FROM identity_cards WHERE id=? AND user_uuid=? AND status='active'",[card_id,u['uuid']]).fetchone()
                if artifact_id: art=con.execute('SELECT * FROM inventory_artifacts WHERE id=? AND user_uuid=?',[artifact_id,u['uuid']]).fetchone()
                dice=random.randint(1,100); area=random.choice(AREAS); danger=random.choice(DANGERS); bonus=8 if art else 0; score=dice+bonus
                reward=max(4, score//10 + (4 if 'DANGER' in danger or 'HAZARD' in danger else 0)); drop=None
                if score>=72 or random.random()<0.18:
                    drop=generated_artifact({'card_name':card['source_name'] if card else u.get('nick_name'), 'area':area}); drop_row=add_artifact(con,u['uuid'],drop,'里界探索',card_id); drop=artifact_row(drop_row)
                result=f"{card['source_name'] if card else '你'}进入{area}，遭遇{danger}事件，掷骰 {dice}" + (f"，借助「{art['name']}」获得 +{bonus}" if art else '') + f"。{'你带回了一件伪物。' if drop else '你只带回了若干本真和一身灰。'}"
                if card_id:
                    dmg = 2 if 'HAZARD' in danger else (1 if 'DANGER' in danger and dice < 55 else 0)
                    if dmg:
                        cr=con.execute('SELECT hp_current,hp_max FROM identity_cards WHERE id=? AND user_uuid=?',[card_id,u['uuid']]).fetchone(); hp=max(0,int(cr['hp_current'])-dmg) if cr else 0
                        status='deleted' if hp<=0 else 'active'
                        con.execute('UPDATE identity_cards SET hp_current=?,status=?,updated_at=? WHERE id=? AND user_uuid=?',[hp,status,int(time.time()),card_id,u['uuid']])
                        con.execute('INSERT INTO identity_card_logs(card_id,user_uuid,event_type,content,delta_json) VALUES(?,?,?,?,?)',[card_id,u['uuid'],'explore_damage',f'{danger} 探索损失 {dmg} HP' + ('，身份卡撕裂归档。' if hp<=0 else ''),json.dumps({'hp':-dmg,'status':status},ensure_ascii=False)])
                    if score>=88:
                        an=random.choice(['门缝听觉','反文阅读','危险预感','伪物共鸣'])
                        con.execute('INSERT INTO character_abilities(card_id,user_uuid,name,source,scope,effect,cost) VALUES(?,?,?,?,?,?,?)',[card_id,u['uuid'],an,'里界探索','forum,rpg,codex','可在论坛发言中体现异常感知，并在探索中获得一次轻微加值。','冷却 24h / 可能增加污染'])
                con.execute('UPDATE members SET benzhen=COALESCE(benzhen,0)+? WHERE uuid=?',[reward,u['uuid']]); con.execute('INSERT INTO explore_runs(user_uuid,card_id,card_name,artifact_id,area,danger,dice,result,reward,artifact_json) VALUES(?,?,?,?,?,?,?,?,?,?)',[u['uuid'],card_id,card['source_name'] if card else '',artifact_id,area,danger,dice,result,reward,json.dumps(drop or {},ensure_ascii=False)]); bal=con.execute('SELECT COALESCE(benzhen,0) AS benzhen FROM members WHERE uuid=?',[u['uuid']]).fetchone(); con.commit(); con.close(); return self.send_json({'ok':True,'result':result,'reward':reward,'artifact':drop,'benzhen':int(bal['benzhen'] if bal else 0)})
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
