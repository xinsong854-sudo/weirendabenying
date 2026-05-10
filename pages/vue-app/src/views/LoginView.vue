<template>
  <div class="login-placeholder"></div>
</template>
<script setup>
import { onMounted } from 'vue'
import { siteApi, SITE_SESSION_KEY, USER_CACHE_KEY } from '../lib/api.js'
import { fetchNetaProfile } from '../lib/neta.js'
const emit = defineEmits(['logged-in'])

onMounted(() => {
  if (typeof window.page_phone_login !== 'function') {
    tryResume()
    return
  }

  window.page_phone_login({
    mount: document.getElementById('app'),
    closeOnMask: false
  }).then(async (token) => {
    const t = token || window.page_phone_login.getToken() || localStorage.getItem('NIETA_ACCESS_TOKEN')
    if (!t) { tryResume(); return }
    await doSession(t)
  }).catch(() => tryResume())
})

async function doSession(token) {
  const p = await fetchNetaProfile(token)
  const user = { uuid: p.uuid, nick_name: p.nick_name || p.name, name: p.name, avatar_url: p.avatar_url, creator_uuid: p.uuid }
  const s = await siteApi('/api/session/create', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user })
  })
  const cached = { ...s.me, role: s.role, title: s.title, signature: s.signature }
  localStorage.setItem(SITE_SESSION_KEY, s.session)
  localStorage.setItem(USER_CACHE_KEY, JSON.stringify(cached))
  emit('logged-in', { session: s.session, me: cached })
}

function tryResume() {
  const session = localStorage.getItem(SITE_SESSION_KEY)
  const me = JSON.parse(localStorage.getItem(USER_CACHE_KEY) || 'null')
  if (session && me) {
    emit('logged-in', { session, me })
    return
  }
  const token = localStorage.getItem('NIETA_ACCESS_TOKEN')
  if (token) {
    doSession(token).catch(() => alert('登录失败，请刷新重试'))
    return
  }
  alert('登录组件加载失败，请刷新页面')
}
</script>
