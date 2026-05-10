<template>
<section class="login-card"><h1>伪人大本营</h1><p>token 只保存在浏览器。本后端只接收用户资料并签发本站 session。</p><div class="field"><input v-model.trim="phone" placeholder="手机号" inputmode="numeric"><button :disabled="sending" @click="sendCode">{{ sending?'发送中':'验证码' }}</button></div><div class="field"><input v-model.trim="code" placeholder="验证码" inputmode="numeric"><button :disabled="logging" @click="login">{{ logging?'登录中':'登录' }}</button></div><small>后续站内请求使用本站 session，不把捏Ta token 发给本站后端。</small><p class="msg">{{ msg }}</p></section>
</template>
<script setup>
import { ref } from 'vue'
import { siteApi, TOKEN_KEY, REFRESH_KEY, SITE_SESSION_KEY, USER_CACHE_KEY } from '../lib/api.js'
import { fetchNetaProfile } from '../lib/neta.js'
const emit = defineEmits(['logged-in'])
const phone=ref(''), code=ref(''), msg=ref(''), sending=ref(false), logging=ref(false)
async function sendCode(){sending.value=true; try{await siteApi('/api/proxy/request-code',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone_num:phone.value})}); msg.value='验证码已发送'}catch(e){msg.value=e.message}finally{sending.value=false}}
async function login(){logging.value=true; try{const data=await siteApi('/api/proxy/verify-code',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone_num:phone.value,code:code.value})}); if(!data.token) throw new Error('未获取 token'); localStorage.setItem(TOKEN_KEY,data.token); if(data.refresh_token)localStorage.setItem(REFRESH_KEY,data.refresh_token); const p=await fetchNetaProfile(data.token); const user={uuid:p.uuid,nick_name:p.nick_name||p.name,name:p.name,avatar_url:p.avatar_url,creator_uuid:p.uuid}; const s=await siteApi('/api/session/create',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user})}); localStorage.setItem(SITE_SESSION_KEY,s.session); localStorage.setItem(USER_CACHE_KEY,JSON.stringify(s.me)); emit('logged-in',s)}catch(e){msg.value=e.message}finally{logging.value=false}}
</script>
