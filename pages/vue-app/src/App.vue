<template>
  <section v-if="!session.me" class="login-wrap">
    <div class="login-card">
      <div class="emblem">⚜️</div>
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

  <section v-else>
    <header class="topbar">
      <button class="logo" @click="showHome">伪人大本营</button>
      <div class="user-grp">
        <img :src="safeUrl(session.me.avatar_url)" alt="avatar" loading="lazy" referrerpolicy="no-referrer">
        <span>{{ session.me.nick_name || session.me.name }}</span>
        <span v-if="session.role === 'chief'" class="badge-chief">⚜️ 营长</span>
        <span v-else-if="session.role === 'deputy'" class="badge-deputy">⚜️ 二营长</span>
        <span v-else-if="session.role === 'admin'" class="badge-admin">管理员</span>
        <button @click="logout">注销</button>
      </div>
    </header>

    <main class="main">
      <section class="hero">
        <h2>伪人大本营</h2>
        <p class="sub">{{ archive.tagline }}</p>
        <div class="stats-row">
          <div class="stat"><div class="val">{{ Math.round(archive.stats.heat / 1e4) }}万</div><div class="lbl">热度</div></div>
          <div class="stat"><div class="val">{{ archive.stats.subscribers }}</div><div class="lbl">订阅</div></div>
          <div class="stat"><div class="val">{{ archive.stats.lore_count }}</div><div class="lbl">条目</div></div>
          <div class="stat"><div class="val">{{ members.length }}</div><div class="lbl">成员</div></div>
        </div>
      </section>

      <div class="search-bar">
        <span class="sicon">🔍</span>
        <input v-model.trim="globalQuery" type="search" placeholder="搜索全部档案..." autocomplete="off">
        <div v-if="globalQuery" class="search-results">
          <button v-for="item in globalResults" :key="item.uuid" class="item" @click="openEntry(item.uuid, true)"><span class="name">{{ item.name }}</span><span class="cat">{{ item.category }}</span></button>
          <div v-if="globalResults.length === 0" class="item muted">无匹配</div>
        </div>
      </div>

      <section v-if="view === 'home'">
        <h3 class="sec-title">大本营成员</h3>
        <div class="member-grid">
          <article v-for="m in members" :key="m.uuid" class="member-card" :class="{ 'm-chief': m.role === 'chief' }">
            <img :src="safeUrl(m.avatar)" alt="" loading="lazy" referrerpolicy="no-referrer">
            <div class="m-info"><div class="m-name">{{ m.name }} <span v-if="m.role === 'chief'" class="badge-chief">营长</span><span v-else-if="m.role === 'deputy'" class="badge-deputy">二营长</span><span v-else-if="m.role === 'admin'" class="badge-admin">管理</span></div><div class="m-time">{{ m.online ? '在线' : timeAgo(m.last_seen) }}</div></div>
            <span class="m-status" :class="m.online ? 'm-online' : 'm-offline'"></span>
          </article>
        </div>
        <h3 class="sec-title">档案分类</h3>
        <div class="cat-grid"><button v-for="cat in categories" :key="cat.name" class="cat-card" @click="openCategory(cat.name)"><span class="name">{{ cat.name }}</span><span class="count">{{ cat.count }} 条档案</span></button></div>
      </section>

      <section v-else-if="view === 'category'">
        <button class="breadcrumb" @click="showHome"><b>←</b> 返回档案分类</button>
        <div class="search-bar"><span class="sicon">🔍</span><input v-model.trim="catQuery" type="search" placeholder="在当前分类中搜索..." autocomplete="off"></div>
        <article v-for="e in categoryEntries" :key="e.uuid" class="entry" role="button" tabindex="0" @click="openEntry(e.uuid)" @keydown.enter="openEntry(e.uuid)">
          <div class="entry-head"><span v-if="badgeMark(e.description)" class="badge" :class="badgeClass(e.description)">{{ badgeMark(e.description) }}</span><span class="entry-title">{{ e.name }}</span></div>
          <div class="body">{{ e.description }}</div>
          <div class="entry-foot">💬 {{ commentCounts[e.uuid] || 0 }} 条评论</div>
        </article>
      </section>

      <section v-else-if="view === 'entry' && currentEntry">
        <button class="breadcrumb" @click="openCategory(currentEntry.category)"><b>←</b> 返回 {{ currentEntry.category }}</button>
        <article class="entry"><div class="entry-head"><span v-if="badgeMark(currentEntry.description)" class="badge" :class="badgeClass(currentEntry.description)">{{ badgeMark(currentEntry.description) }}</span><span class="entry-title big">{{ currentEntry.name }}</span></div><div class="body">{{ currentEntry.description }}</div></article>
        <section class="comments-section"><h3>档案评论</h3><div class="comment-list"><article v-for="c in comments" :key="`${c.created_at}-${c.user_name}-${c.content}`" class="comment"><img :src="safeUrl(c.user_avatar)" alt="" loading="lazy" referrerpolicy="no-referrer"><div class="c-body"><div class="c-head"><span class="c-name">{{ c.user_name }}</span><span class="c-time">{{ timeAgo(c.created_at) }}</span></div><div class="c-text">{{ c.content }}</div></div></article></div><div class="comment-form"><img :src="safeUrl(session.me.avatar_url)" alt="" loading="lazy"><textarea v-model.trim="commentText" maxlength="2000" placeholder="写下你的评论..." rows="2"></textarea><button :disabled="posting || !commentText" @click="postComment">{{ posting ? '发送中...' : '发表' }}</button></div></section>
      </section>
    </main>
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
const session = reactive({ me: null, role: 'member', token: '' })

const allEntries = Object.entries(archive.lore).flatMap(([category, entries]) => entries.map(e => ({ ...e, category })))
const categories = computed(() => Object.entries(archive.lore).map(([name, list]) => ({ name, count: list.length })).sort((a, b) => b.count - a.count))
const globalResults = computed(() => filterEntries(allEntries, globalQuery.value).slice(0, 20))
const categoryEntries = computed(() => filterEntries(archive.lore[currentCat.value] || [], catQuery.value))

function filterEntries(list, q) {
  const needle = String(q || '').toLowerCase()
  if (!needle) return list
  return list.filter(e => `${e.name}\n${e.description}`.toLowerCase().includes(needle))
}
function vp(p) { return /^1[3456789]\d{9}$/.test(p) }
function showMsg(text, type = 'error') { message.value = text; messageType.value = type }
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
