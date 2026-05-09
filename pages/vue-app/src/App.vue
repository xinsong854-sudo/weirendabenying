<template>
  <section v-if="!session.me" class="login-scene">
    <div class="login-orbit" aria-hidden="true">
      <img src="/cutouts/snakeoil-bottle.svg" alt="">
      <img src="/cutouts/syringe.svg" alt="">
      <img src="/cutouts/candy.svg" alt="">
    </div>
    <div class="login-card labyrinth-window">
      <div class="window-title">IDENTITY RITUAL</div>
      <div class="emblem">✦</div>
      <h1>伪人大本营</h1>
      <p class="tagline">机密档案库 · 身份核验</p>
      <div class="field"><span class="prefix">+86</span><input v-model.trim="phone" type="tel" inputmode="numeric" maxlength="11" placeholder="请输入手机号" autocomplete="tel"></div>
      <div class="field"><input v-model.trim="code" type="text" inputmode="numeric" maxlength="4" placeholder="验证码" autocomplete="one-time-code"><button class="code-btn" :disabled="sending || timer > 0" @click="sendCode">{{ timer > 0 ? `${timer}s` : '获取验证码' }}</button></div>
      <label class="agree"><input v-model="agree" type="checkbox"><span>我已阅读并同意 <a href="https://oss.talesofai.cn/static/blackboard/protocol-page/user-agreement.html" target="_blank" rel="noopener noreferrer">用户协议</a> 和 <a href="https://oss.talesofai.cn/static/blackboard/protocol-page/privacy-policy.html" target="_blank" rel="noopener noreferrer">隐私政策</a></span></label>
      <button class="submit" :disabled="logging" @click="login">{{ logging ? '登录中...' : '登 录' }}</button>
      <div class="msg" :class="messageType">{{ message }}</div>
      <div class="foot">未注册手机号验证后将自动登录 · t.nieta.art/UTLCFvWs</div>
    </div>
  </section>

  <section v-else class="labyrinth-app">
    <header class="stage-top">
      <button class="brand-ticket" @click="showHome">伪人大本营</button>
      <nav class="stage-nav" aria-label="主导航">
        <button :class="{ active: view === 'home' }" @click="showHome">结界入口</button>
        <button :class="{ active: ['archive','category','entry'].includes(view) }" @click="openArchive">档案馆</button>
        <button @click="showMsg('讨论区即将开放', 'muted')">讨论幕布</button>
        <button @click="openSettings">设置</button>
      </nav>
      <div class="identity-tag">
        <div class="mini-avatar framed-avatar" :class="avatarFrameClass">
          <img class="avatar-base" :src="safeUrl(session.me.avatar_url)" alt="avatar" loading="lazy" referrerpolicy="no-referrer">
          <img v-if="currentAvatarFrame?.type === 'frame'" class="avatar-frame" :src="currentAvatarFrame.url" alt="">
          <span v-if="currentAvatarFrame?.type === 'roach'" class="roach-orbit" aria-hidden="true"><img :src="currentAvatarFrame.url" alt=""></span>
        </div>
        <span>{{ session.me.nick_name || session.me.name }}</span>
        <button @click="logout">退出</button>
      </div>
    </header>

    <main class="stage-main">
      <Transition name="page-shift" mode="out-in">
      <section v-if="view === 'home'" key="home" class="game-home">
        <aside class="profile-panel">
          <div class="avatar-ring framed-avatar" :class="avatarFrameClass">
            <img class="avatar-base" :src="safeUrl(session.me.avatar_url)" alt="avatar" loading="lazy" referrerpolicy="no-referrer">
            <img v-if="currentAvatarFrame?.type === 'frame'" class="avatar-frame" :src="currentAvatarFrame.url" alt="">
            <span v-if="currentAvatarFrame?.type === 'roach'" class="roach-orbit" aria-hidden="true"><img :src="currentAvatarFrame.url" alt=""></span>
          </div>
          <span class="profile-name">{{ session.me.nick_name || session.me.name }}</span>
          <h2>一席界面</h2>
          <p>深夜的玻璃教堂里，论坛入口、档案索引和成员活动被收纳在同一座异空间大厅。</p>
          <h2>梦梦局</h2>
          <p>从这里进入档案馆、悬挂新讨论，或打开后续预留的功能入口。</p>
          <div class="profile-gems"><i></i><i></i><i></i></div>
        </aside>

        <section class="main-gate">
          <h1>伪人大本营</h1>
          <p>{{ archive.tagline }}</p>
          <div class="gate-actions">
            <button class="start-btn" @click="openArchive">进入档案馆</button>
            <button class="sub-btn" @click="showMsg('发帖功能预留中', 'muted')">发布讨论</button>
          </div>
        </section>

        <aside class="route-panel">
          <div class="route-head">迁回</div>
          <button v-for="board in boards" :key="board.title" class="route-card" @click="board.action">
            <span>{{ board.icon }}</span>
            <b>{{ board.title }}</b>
            <small>{{ board.count }} {{ board.label }}</small>
          </button>
        </aside>

        <div class="quick-orbs" aria-label="快捷入口">
          <button @click="openArchive">✦</button>
          <button @click="showMsg('成员中心即将开放', 'muted')">◈</button>
          <button @click="showMsg('工具箱即将开放', 'muted')">☰</button>
        </div>

        <footer class="bottom-dock">
          <button @click="openArchive">档案馆</button>
          <button @click="showMsg('讨论区即将开放', 'muted')">讨论</button>
          <button @click="showMsg('任务板即将开放', 'muted')">任务</button>
          <button @click="openSettings">设置</button>
        </footer>
      </section>

      <section v-else-if="view === 'archive'" key="archive" class="archive-theater">
        <div class="page-actions"><button class="back-note primary" @click="showHome">← 返回主页</button></div>
        <header class="archive-marquee">
          <div>
            <span class="ritual-label">ARCHIVE CABINET / PAPER INDEX</span>
            <h1>档案馆</h1>
            <p>词条集中收纳于此，像贴在结界墙面的索引牌。</p>
          </div>
          <img src="/cutouts/snakeoil-bottle.svg" alt="" aria-hidden="true">
        </header>
        <div class="search-bar"><span class="sicon">⌕</span><input v-model.trim="globalQuery" type="search" placeholder="搜索档案馆词条..." autocomplete="off"><div v-if="globalQuery" class="search-results"><button v-for="item in globalResults" :key="item.uuid" class="item" @click="openEntry(item.uuid, true)"><span class="name">{{ item.name }}</span><span class="cat">{{ item.category }}</span></button><div v-if="globalResults.length === 0" class="item muted">无匹配</div></div></div>
        <div class="specimen-grid">
          <button v-for="cat in categories" :key="cat.name" class="specimen-card" @click="openCategory(cat.name)">
            <span class="specimen-no">{{ cat.count }}</span>
            <b>{{ cat.name }}</b>
            <small>{{ cat.preview }}</small>
          </button>
        </div>
      </section>

      <section v-else-if="view === 'category'" key="category" class="category-theater">
        <div class="page-actions"><button class="back-note primary" @click="showHome">← 返回主页</button><button class="back-note" @click="openArchive">返回档案馆</button></div>
        <div class="search-bar"><span class="sicon">⌕</span><input v-model.trim="catQuery" type="search" placeholder="在当前分类中搜索..." autocomplete="off"></div>
        <article v-for="e in categoryEntries" :key="e.uuid" class="entry-note" role="button" tabindex="0" @click="openEntry(e.uuid)" @keydown.enter="openEntry(e.uuid)">
          <span v-if="badgeMark(e.description)" class="badge" :class="badgeClass(e.description)">{{ badgeMark(e.description) }}</span>
          <h2>{{ e.name }}</h2>
          <p>{{ e.description }}</p>
          <footer>💬 {{ commentCounts[e.uuid] || 0 }} 条评论</footer>
        </article>
      </section>

      <section v-else-if="view === 'entry' && currentEntry" key="entry" class="entry-theater">
        <div class="page-actions"><button class="back-note primary" @click="showHome">← 返回主页</button><button class="back-note" @click="openCategory(currentEntry.category)">返回 {{ currentEntry.category }}</button></div>
        <article class="entry-full">
          <span v-if="badgeMark(currentEntry.description)" class="badge" :class="badgeClass(currentEntry.description)">{{ badgeMark(currentEntry.description) }}</span>
          <h1>{{ currentEntry.name }}</h1>
          <p>{{ currentEntry.description }}</p>
        </article>
        <section class="comment-stage">
          <h3>档案评论</h3>
          <article v-for="c in comments" :key="`${c.created_at}-${c.user_name}-${c.content}`" class="comment">
            <img :src="safeUrl(c.user_avatar)" alt="" loading="lazy" referrerpolicy="no-referrer">
            <div><b>{{ c.user_name }}</b><time>{{ timeAgo(c.created_at) }}</time><p>{{ c.content }}</p></div>
          </article>
          <div class="comment-form"><img :src="safeUrl(session.me.avatar_url)" alt="" loading="lazy"><textarea v-model.trim="commentText" maxlength="2000" placeholder="写下你的评论..." rows="2"></textarea><button :disabled="posting || !commentText" @click="postComment">{{ posting ? '发送中...' : '发表' }}</button></div>
        </section>
      </section>
      </Transition>
    </main>

    <div v-if="settingsOpen" class="settings-mask" @click.self="settingsOpen = false">
      <section class="settings-panel" role="dialog" aria-modal="true" aria-label="设置">
        <header>
          <div>
            <span>SETTINGS</span>
            <h2>设置</h2>
          </div>
          <button class="settings-close" @click="settingsOpen = false">×</button>
        </header>
        <div class="setting-block">
          <h3>头像框</h3>
          <p>选择一个头像框，会保存在本机，下次打开仍然生效。</p>
          <div class="frame-grid">
            <button v-for="frame in avatarFrames" :key="frame.id" class="frame-option" :class="{ active: avatarFrame === frame.id }" @click="setAvatarFrame(frame.id)">
              <span class="frame-preview framed-avatar" :class="frame.type === 'roach' ? 'has-roach-frame' : ''">
                <img class="avatar-base" :src="safeUrl(session.me.avatar_url)" alt="">
                <img v-if="frame.type === 'frame'" class="avatar-frame" :src="frame.url" alt="">
                <span v-if="frame.type === 'roach'" class="roach-orbit" aria-hidden="true"><img :src="frame.url" alt=""></span>
              </span>
              <b>{{ frame.name }}</b>
            </button>
          </div>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import archive from './pseudo-human-data.json'

const API = 'https://api.talesofai.cn'
const TOKEN_KEY = 'NIETA_ACCESS_TOKEN'
const phone = ref('')
const code = ref('')
const agree = ref(false)
const message = ref('')
const messageType = ref('')
const sending = ref(false)
const logging = ref(false)
const timer = ref(0)
const view = ref('home')
const currentCat = ref('')
const currentEntry = ref(null)
const globalQuery = ref('')
const catQuery = ref('')
const members = ref([])
const comments = ref([])
const commentText = ref('')
const posting = ref(false)
const commentCounts = ref({})
const settingsOpen = ref(false)
const savedFrame = localStorage.getItem('NIETA_AVATAR_FRAME')
const avatarFrame = ref(['none', 'roach', 'moonrise'].includes(savedFrame) ? savedFrame : 'roach')
const session = reactive({ me: null, role: 'member', token: '' })
const avatarFrames = [
  { id: 'none', name: '无头像框', url: '', type: 'none' },
  { id: 'roach', name: '乱爬蟑螂', url: 'https://oss.talesofai.cn/sts/49c915e649254f55a7ea399ad3b6efd1/53710f82-1ad8-4863-98ee-4d7bed45f215.png', type: 'roach' },
  { id: 'moonrise', name: '月升', url: 'https://oss.talesofai.cn/sts/49c915e649254f55a7ea399ad3b6efd1/65785b12-302c-4953-bf6b-8efb37adbdae.png', type: 'frame' }
]

const allEntries = Object.entries(archive.lore).flatMap(([category, entries]) => entries.map(e => ({ ...e, category })))
const categories = computed(() => Object.entries(archive.lore).map(([name, list]) => ({
  name,
  count: list.length,
  preview: (list || []).slice(0, 3).map(e => e.name).join(' · ') || '暂无档案'
})).sort((a, b) => b.count - a.count))
const memberPreview = computed(() => [...members.value].sort((a, b) => Number(b.online) - Number(a.online)).slice(0, 12))
const onlineCount = computed(() => members.value.filter(m => m.online).length)
const boards = computed(() => [
  { icon: '📌', title: '公告与规则', desc: '置顶公告、营地规则、更新记录', count: 3, label: '置顶', action: () => showMsg('公告板预留中', 'muted') },
  { icon: '💬', title: '日常讨论', desc: '成员交流、脑洞、提问与闲聊', count: members.value.length, label: '成员', action: () => showMsg('讨论区即将开放', 'muted') },
  { icon: '📚', title: '档案馆', desc: '词条索引、分类浏览、档案评论', count: archive.stats.lore_count, label: '词条', action: () => openArchive() },
  { icon: '🧪', title: '功能实验室', desc: '后续功能、投稿、活动、管理工具入口', count: 4, label: '模块', action: () => showMsg('功能实验室即将开放', 'muted') }
])
const globalResults = computed(() => filterEntries(allEntries, globalQuery.value).slice(0, 20))
const categoryEntries = computed(() => filterEntries(archive.lore[currentCat.value] || [], catQuery.value))
const currentAvatarFrame = computed(() => avatarFrames.find(f => f.id === avatarFrame.value && f.url) || null)
const avatarFrameClass = computed(() => currentAvatarFrame.value?.type === 'roach' ? 'has-roach-frame' : '')

function filterEntries(list, q) {
  const needle = String(q || '').toLowerCase()
  if (!needle) return list
  return list.filter(e => `${e.name}\n${e.description}`.toLowerCase().includes(needle))
}
function vp(p) { return /^1[3456789]\d{9}$/.test(p) }
function showMsg(text, type = 'error') { message.value = text; messageType.value = type }
function openSettings() { settingsOpen.value = true }
function setAvatarFrame(id) { avatarFrame.value = id; localStorage.setItem('NIETA_AVATAR_FRAME', id); showMsg(id === 'none' ? '已取消头像框' : '头像框已更换', 'muted') }
function safeUrl(url) { const s = String(url || '').trim(); return /^(https?:)?\/\//i.test(s) ? s : '' }
async function readJson(res) { const text = await res.text(); try { return text ? JSON.parse(text) : null } catch { return { error: text.slice(0, 500) } } }
async function api(path, options) { const res = await fetch(path, options); const data = await readJson(res); if (!res.ok) throw new Error(data?.message || data?.msg || data?.error || data?.detail || res.statusText); return data }

function initCaptcha() {
  return new Promise((resolve, reject) => {
    if (!window.initGeetest4) { reject(new Error('验证码组件加载失败，请刷新页面')); return }
    let done = false
    const timeout = setTimeout(() => { if (!done) { done = true; reject(new Error('验证码加载超时（网络问题），请稍后重试')) } }, 10000)
    window.initGeetest4({ captchaId: 'e000881b946cad6dcc39aa1eb40c80b0', product: 'popup', protocol: 'https://', hideSuccess: true, mask: { outside: false } }, (obj) => {
      clearTimeout(timeout)
      if (done) return
      obj.onSuccess(() => { const v = obj.getValidate(); obj.destroy(); resolve(v) })
      obj.onError(() => { obj.destroy(); reject(new Error('安全验证出错，请重试')) })
      obj.onClose(() => { obj.destroy(); reject(new Error('验证已取消')) })
      obj.onReady(() => obj.showCaptcha())
    })
  })
}
async function loadCaptchaScript() {
  if (window.initGeetest4) return
  await new Promise((resolve, reject) => {
    const s = document.createElement('script')
    s.src = 'https://oss.talesofai.cn/fe_assets/libs/gt4.js'
    s.async = true
    s.onload = resolve
    s.onerror = () => reject(new Error('验证码脚本加载失败'))
    document.head.appendChild(s)
  })
}
async function sendCode() {
  const p = phone.value
  if (!vp(p)) return showMsg('请输入正确的手机号')
  sending.value = true
  try {
    showMsg('加载验证码...', 'muted')
    await loadCaptchaScript()
    const captcha_validate = await initCaptcha()
    showMsg('发送中...', 'muted')
    const data = await api('/api/proxy/request-code', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone_num: p, captcha_validate }) })
    showMsg(data?.duration ? `验证码已发送，${data.duration}s 内有效` : '验证码已发送', 'ok')
    timer.value = 60
    const id = setInterval(() => { timer.value -= 1; if (timer.value <= 0) clearInterval(id) }, 1000)
  } catch (e) { showMsg(`发送失败：${e.message}`) } finally { sending.value = false }
}
async function login() {
  const p = phone.value, c = code.value
  if (!vp(p)) return showMsg('请输入正确的手机号')
  if (!/^\d{4}$/.test(c)) return showMsg('请输入4位验证码')
  if (!agree.value) return showMsg('请先阅读并同意协议')
  logging.value = true
  try {
    const data = await api('/api/proxy/verify-code', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone_num: p, code: c }) })
    if (!data?.token) throw new Error('未获取到令牌')
    await useToken(data.token)
  } catch (e) { showMsg(`登录失败：${e.message}`) } finally { logging.value = false }
}
async function useToken(token) {
  const me = await api(`${API}/v1/user/`, { headers: { 'x-token': token } })
  if (!me?.uuid) throw new Error('令牌无效')
  session.me = me; session.token = token; localStorage.setItem(TOKEN_KEY, token)
  await fetch('/api/verify', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': token }, body: JSON.stringify(me) }).catch(() => {})
  const role = await api(`/api/members/role?uuid=${encodeURIComponent(me.uuid)}`)
  session.role = role?.role || 'member'
  await loadMembers()
}
async function loadMembers() { members.value = await api('/api/members').catch(() => []) }
function showHome() { view.value = 'home'; currentEntry.value = null; globalQuery.value = ''; loadMembers() }
function openArchive() { view.value = 'archive'; currentEntry.value = null; currentCat.value = ''; catQuery.value = ''; window.scrollTo(0, 0); loadMembers() }
function openCategory(cat) { currentCat.value = cat; catQuery.value = ''; currentEntry.value = null; view.value = 'category'; window.scrollTo(0, 0) }
async function openEntry(uuid, fromGlobal = false) { const entry = allEntries.find(e => e.uuid === uuid); if (!entry) return; currentEntry.value = entry; currentCat.value = entry.category; view.value = 'entry'; if (fromGlobal) globalQuery.value = ''; window.scrollTo(0, 0); await loadComments(uuid) }
async function loadComments(uuid) { comments.value = await api(`/api/comments?entry_uuid=${encodeURIComponent(uuid)}`).catch(() => []); commentCounts.value = { ...commentCounts.value, [uuid]: comments.value.length } }
async function postComment() { if (!currentEntry.value || !commentText.value) return; posting.value = true; try { await api('/api/comments', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-token': session.token }, body: JSON.stringify({ entry_uuid: currentEntry.value.uuid, content: commentText.value }) }); commentText.value = ''; await loadComments(currentEntry.value.uuid) } finally { posting.value = false } }
function logout() { localStorage.removeItem(TOKEN_KEY); session.me = null; session.token = ''; session.role = 'member'; view.value = 'home' }
function badgeMark(d = '') { return ['🟥', '🟧', '🟨', '🟩', '⬜'].find(x => d.includes(x)) || '' }
function badgeClass(d = '') { const m = badgeMark(d); return { '🟥': 'b-red', '🟧': 'b-orange', '🟨': 'b-yellow', '🟩': 'b-green', '⬜': 'b-gray' }[m] || 'b-gray' }
function timeAgo(ts) { if (!ts) return ''; const d = Date.now() / 1000 - Number(ts); if (d < 0) return '在线'; if (d < 60) return '刚刚在线'; if (d < 3600) return `${Math.floor(d / 60)}分钟前`; if (d < 86400) return `${Math.floor(d / 3600)}小时前`; return `${Math.floor(d / 86400)}天前` }

onMounted(async () => {
  const saved = localStorage.getItem(TOKEN_KEY)
  if (saved) { logging.value = true; showMsg('检测到已保存的登录状态', 'muted'); try { await useToken(saved) } catch { localStorage.removeItem(TOKEN_KEY); showMsg('登录状态已过期，请重新登录') } finally { logging.value = false } }
})
</script>
