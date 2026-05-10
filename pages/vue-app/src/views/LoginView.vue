<template>
  <div class="login-placeholder"></div>
</template>
<script setup>
import { onMounted } from 'vue'
import { siteApi, SITE_SESSION_KEY, USER_CACHE_KEY, TOKEN_KEY, REFRESH_KEY } from '../lib/api.js'
import { fetchNetaProfile } from '../lib/neta.js'
const emit = defineEmits(['logged-in'])

onMounted(() => {
  // 已有本站 session → 直接进入
  const saved = localStorage.getItem(SITE_SESSION_KEY)
  const savedMe = localStorage.getItem(USER_CACHE_KEY)
  if (saved && savedMe) {
    emit('logged-in', { session: saved, me: JSON.parse(savedMe) })
    return
  }

  // 有捏Ta token → 跳过登录直接用
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    doSession(token)
    return
  }

  // 都没有 → page_phone_login
  if (typeof window.page_phone_login === 'function') {
    window.page_phone_login({
      mount: document.getElementById('app'),
      closeOnMask: false
    }).then(t => doSession(t || window.page_phone_login.getToken() || localStorage.getItem(TOKEN_KEY)))
      .catch(fallback)
  } else {
    fallback()
  }
})

async function doSession(token) {
  if (!token) return fallback()
  const p = await fetchNetaProfile(token)

  // 存 Neta 登录数据到本地
  localStorage.setItem(TOKEN_KEY, token)
  const rt = localStorage.getItem(REFRESH_KEY) || window.page_phone_login?.getToken?.()
  if (rt && rt !== token) try { localStorage.setItem(REFRESH_KEY, rt) } catch {}

  const user = {
    uuid: p.uuid,
    nick_name: p.nick_name || p.name,
    name: p.name,
    avatar_url: p.avatar_url,
    creator_uuid: p.uuid
  }

  try {
    const s = await siteApi('/api/session/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user })
    })
    const cached = { ...s.me, role: s.role, title: s.title, signature: s.signature }
    localStorage.setItem(SITE_SESSION_KEY, s.session)
    localStorage.setItem(USER_CACHE_KEY, JSON.stringify(cached))
    emit('logged-in', { session: s.session, me: cached })
  } catch {
    // 后端不可用 → 本地 session 兜底
    const localSession = 'local-' + Date.now()
    const me = { ...user, role: 'member', title: '', signature: '' }
    localStorage.setItem(SITE_SESSION_KEY, localSession)
    localStorage.setItem(USER_CACHE_KEY, JSON.stringify(me))
    emit('logged-in', { session: localSession, me })
  }
}

function fallback() {
  alert('登录失败，请刷新重试')
}
</script>
