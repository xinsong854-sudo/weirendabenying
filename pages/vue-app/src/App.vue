<template>
  <main class="app">
    <LoginView v-if="!session" @logged-in="onLoggedIn" />
    <section v-else class="shell">
      <TopBar :user="me" @logout="logout" />
      <nav class="tabs">
        <button :class="{on:view==='forum'}" @click="view='forum'">论坛</button>
        <button :class="{on:view==='cards'}" @click="view='cards'">身份卡</button>
        <button :class="{on:view==='members'}" @click="view='members'">成员</button>
        <button :class="{on:view==='wiki'}" @click="view='wiki'">Wiki</button>
        <button :class="{on:view==='codex'}" @click="view='codex'">图鉴</button>
        <button :class="{on:view==='profile'}" @click="view='profile'">个人</button>
      </nav>
      <ForumView v-if="view==='forum'" :session="session" />
      <CardsView v-else-if="view==='cards'" :session="session" />
      <MembersView v-else-if="view==='members'" />
      <WikiView v-else-if="view==='wiki'" :session="session" />
      <CodexView v-else-if="view==='codex'" />
      <ProfileView v-else :session="session" :user="me" @updated="onProfileUpdated" />
    </section>
  </main>
</template>
<script setup>
import { ref } from 'vue'
import { SITE_SESSION_KEY, USER_CACHE_KEY } from './lib/api.js'
import LoginView from './views/LoginView.vue'
import ForumView from './views/ForumView.vue'
import CardsView from './views/CardsView.vue'
import MembersView from './views/MembersView.vue'
import WikiView from './views/WikiView.vue'
import CodexView from './views/CodexView.vue'
import ProfileView from './views/ProfileView.vue'
import TopBar from './components/TopBar.vue'
const session=ref(localStorage.getItem(SITE_SESSION_KEY)||'')
const me=ref(JSON.parse(localStorage.getItem(USER_CACHE_KEY)||'null'))
const view=ref('forum')
function onLoggedIn(data){session.value=data.session; me.value=data.me; view.value='forum'}
function onProfileUpdated(data){ if(data?.me){ me.value={...me.value,...data.me}; localStorage.setItem(USER_CACHE_KEY,JSON.stringify(me.value)) } }
function logout(){localStorage.removeItem(SITE_SESSION_KEY);localStorage.removeItem(USER_CACHE_KEY);session.value='';me.value=null;view.value='forum'}
</script>
