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
    setTimeout(() => emit('logged-in', {}), 100) // fallback
    return
  }

  window.page_phone_login({
    mount: document.getElementById('app'),
    closeOnMask: false,
    onOpen: (instance) => {
      // login page is now showing
    }
  }).then(async (token) => {
    const t = token || window.page_phone_login.getToken() || localStorage.getItem('NIETA_ACCESS_TOKEN')
    if (!t) { emit('logged-in', {}); return }

    try {
      const p = await fetchNetaProfile(t)
      const user = { uuid: p.uuid, nick_name: p.nick_name || p.name, name: p.name, avatar_url: p.avatar_url, creator_uuid: p.uuid }
      const s = await siteApi('/api/session/create', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ user }) })
      const cached = { ...s.me, role: s.role, title: s.title, signature: s.signature }
      localStorage.setItem(SITE_SESSION_KEY, s.session)
      localStorage.setItem(USER_CACHE_KEY, JSON.stringify(cached))
      emit('logged-in', { ...s, me: cached })
    } catch (e) {
      console.error('session create failed:', e)
      emit('logged-in', {})
    }
  }).catch((err) => {
    console.error('login cancelled:', err)
    emit('logged-in', {})
  })
})
</script>
