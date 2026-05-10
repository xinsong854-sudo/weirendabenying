<template>
  <main class="app">
    <section v-if="!session" class="login-card">
      <h1>伪人大本营</h1>
      <p>方案 D：捏Ta token 只保存在你的浏览器。本后端只接收用户资料并签发本站 session，不接收、不落库 token。</p>
      <div class="field"><input v-model.trim="phone" placeholder="手机号" inputmode="numeric" maxlength="11"><button :disabled="sending" @click="sendCode">{{ sending ? '发送中' : '验证码' }}</button></div>
      <div class="field"><input v-model.trim="code" placeholder="验证码" inputmode="numeric" maxlength="6"><button :disabled="logging" @click="login">{{ logging ? '登录中' : '登录' }}</button></div>
      <small>登录后前端直连捏Ta获取用户资料，再只把 uuid/昵称/头像发给本站创建 session。</small>
      <p class="msg">{{ msg }}</p>
    </section>

    <section v-else class="shell">
      <header class="topbar">
        <div><b>{{ me?.nick_name || me?.name }}</b><span>{{ me?.uuid }}</span></div>
        <button @click="logout">退出</button>
      </header>
      <nav class="tabs"><button :class="{on:view==='forum'}" @click="view='forum'">论坛</button><button :class="{on:view==='cards'}" @click="view='cards'; loadCards()">身份卡</button><button :class="{on:view==='members'}" @click="view='members'; loadMembers()">成员</button></nav>

      <section v-if="view==='forum'" class="panel">
        <h2>主论坛</h2>
        <div class="compose"><input v-model.trim="postText" placeholder="说点什么"><button @click="postForum">发送</button></div>
        <article v-for="p in posts" :key="p.id" class="post"><b>{{ p.user_name }}</b><p>{{ p.content }}</p><time>{{ new Date(p.created_at*1000).toLocaleString() }}</time></article>
      </section>

      <section v-else-if="view==='cards'" class="panel">
        <h2>身份卡</h2>
        <div class="compose"><input v-model.trim="cardInput" placeholder="粘贴 t.nieta.art 短链 / UUID"><button @click="importCard">导入</button></div>
        <p class="hint">{{ cardHint }}</p>
        <article v-for="c in cards" :key="c.id" class="card-row"><img v-if="c.avatar_img" :src="c.avatar_img"><div><b>{{ c.source_name }}</b><small>{{ c.source_uuid }}</small></div><button @click="deleteCard(c.id)">删除</button></article>
      </section>

      <section v-else class="panel"><h2>成员</h2><article v-for="m in members" :key="m.uuid" class="member"><img v-if="m.avatar" :src="m.avatar"><div><b>{{ m.name }}</b><small>{{ m.uuid }}</small></div></article></section>
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from 'vue'
const API='https://api.talesofai.cn'
const TOKEN='NIETA_ACCESS_TOKEN', REFRESH='NIETA_REFRESH_TOKEN', SITE='WEIREN_SITE_SESSION', USER='WEIREN_USER'
const phone=ref(''), code=ref(''), msg=ref(''), sending=ref(false), logging=ref(false)
const session=ref(localStorage.getItem(SITE)||''), me=ref(JSON.parse(localStorage.getItem(USER)||'null'))
const view=ref('forum'), posts=ref([]), postText=ref(''), members=ref([]), cards=ref([]), cardInput=ref(''), cardHint=ref('')
function headers(){return {'Content-Type':'application/json','x-session':session.value}}
async function api(path,opt={}){const r=await fetch(path.startsWith('/api')?path:path,opt); const d=await r.json().catch(()=>({})); if(!r.ok) throw new Error(d.error||'请求失败'); return d}
async function sendCode(){sending.value=true; try{await api('/api/proxy/request-code',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone_num:phone.value})}); msg.value='验证码已发送'}catch(e){msg.value=e.message}finally{sending.value=false}}
async function login(){logging.value=true; try{const data=await api('/api/proxy/verify-code',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone_num:phone.value,code:code.value})}); if(!data.token) throw new Error('未获取 token'); localStorage.setItem(TOKEN,data.token); if(data.refresh_token)localStorage.setItem(REFRESH,data.refresh_token); const profile=await fetch(`${API}/v1/user/`,{headers:{'x-token':data.token}}).then(r=>r.json()); const s=await api('/api/session/create',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user:{uuid:profile.uuid,nick_name:profile.nick_name||profile.name,name:profile.name,avatar_url:profile.avatar_url,creator_uuid:profile.uuid}})}); session.value=s.session; me.value=s.me; localStorage.setItem(SITE,s.session); localStorage.setItem(USER,JSON.stringify(s.me)); await loadForum(); msg.value=''}catch(e){msg.value=e.message}finally{logging.value=false}}
function logout(){localStorage.removeItem(SITE);localStorage.removeItem(USER);session.value='';me.value=null}
async function loadForum(){posts.value=await api('/api/forum/posts?channel=主论坛')}
async function postForum(){if(!postText.value)return; await api('/api/forum/posts',{method:'POST',headers:headers(),body:JSON.stringify({channel:'主论坛',content:postText.value})}); postText.value=''; await loadForum()}
async function loadMembers(){members.value=await api('/api/members')}
async function loadCards(){cards.value=await api('/api/identity-cards',{headers:headers()})}
function shortUrl(t){return (String(t).match(/https?:\/\/t\.nieta\.art\/[a-zA-Z0-9]+/)||[])[0]||''}
function uuidOf(t){return (String(t).match(/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/)||[])[0]||''}
function creatorOf(t){return (String(t).match(/[?&#](?:from_user|creator_uuid|owner_uuid|user_uuid)=([0-9a-fA-F-]{32,36})/)||[])[1]||''}
async function resolveInput(raw){let text=raw; const su=shortUrl(raw); if(su){const u=await fetch(`${API}/v1/util/original-url?short_url=${encodeURIComponent(su)}`).then(r=>r.json()); text=typeof u==='string'?u:JSON.stringify(u)} return {uuid:uuidOf(text),creator_uuid:creatorOf(text),url:text}}
async function importCard(){try{cardHint.value='解析中...'; const r=await resolveInput(cardInput.value); if(!r.uuid) throw new Error('短链已解析，但没有 UUID'); const token=localStorage.getItem(TOKEN); const profile=await fetch(`${API}/v2/travel/parent/${r.uuid}/profile`,{headers:{Authorization:'Bearer '+token}}).then(x=>x.json()); const merged={...profile,uuid:r.uuid,creator_uuid:r.creator_uuid||profile.creator_uuid||profile.owner_uuid||profile?.creator?.uuid}; const saved=await api('/api/identity-cards',{method:'POST',headers:headers(),body:JSON.stringify({profile:merged})}); cardHint.value='已导入 '+saved.card.source_name; cardInput.value=''; await loadCards()}catch(e){cardHint.value=e.message}}
async function deleteCard(id){await api('/api/identity-cards/delete',{method:'POST',headers:headers(),body:JSON.stringify({id})}); await loadCards()}
onMounted(()=>{if(session.value) loadForum().catch(()=>{})})
</script>
