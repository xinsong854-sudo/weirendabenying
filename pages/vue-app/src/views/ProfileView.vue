<template>
  <section class="panel profile-view">
    <h2>个人中心</h2>
    <div class="profile-head">
      <span class="profile-avatar" :class="frame"><img v-if="user?.avatar_url" :src="user.avatar_url"><b v-else>{{ initial(user?.nick_name || user?.name) }}</b></span>
      <div><b>{{ user?.nick_name || user?.name }}</b><small>{{ user?.uuid }}</small></div>
    </div>
    <label class="form-block"><b>个人签名</b><textarea v-model.trim="signature" maxlength="80" rows="3" placeholder="留下一句签名..."></textarea><small>{{ signature.length }}/80</small></label>
    <div class="frame-section"><b>头像框</b><div class="frame-grid"><button v-for="f in frames" :key="f.id" :class="['frame-option',{on:frame===f.id}]" @click="frame=f.id"><span class="frame-preview" :class="f.id"><img v-if="user?.avatar_url" :src="user.avatar_url"><b v-else>{{ initial(user?.nick_name || user?.name) }}</b></span><em>{{ f.name }}</em></button></div></div>
    <button class="primary" :disabled="saving" @click="save">{{ saving?'保存中':'保存资料' }}</button>
    <p class="hint">{{ hint }}</p>
  </section>
</template>
<script setup>
import { onMounted, ref } from 'vue'; import { siteApi, sessionHeaders } from '../lib/api.js'
const props=defineProps({session:String,user:Object}); const emit=defineEmits(['updated'])
const signature=ref(''), frame=ref('none'), saving=ref(false), hint=ref('')
const frames=[{id:'none',name:'无'}, {id:'gold',name:'金档案'}, {id:'wine',name:'红月'}, {id:'eye',name:'凝视'}]
function initial(s='?'){return String(s||'?').slice(0,1)}
async function load(){try{const r=await siteApi('/api/profile',{headers:sessionHeaders(props.session)}); signature.value=r.signature||''; frame.value=r.avatar_frame||'none'}catch{}}
async function save(){saving.value=true; try{const r=await siteApi('/api/profile',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify({signature:signature.value,avatar_frame:frame.value})}); hint.value='已保存'; emit('updated',r)}catch(e){hint.value=e.message}finally{saving.value=false}}
onMounted(load)
</script>
