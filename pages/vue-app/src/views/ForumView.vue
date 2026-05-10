<template>
  <section class="panel forum-view-rich">
    <header class="forum-head"><div><span class="ritual-label">Artificial Human Base Camp</span><h2>{{ channel }}</h2><p>{{ channelDesc }}</p></div><button class="primary" @click="loadAll">刷新</button></header>
    <nav class="forum-channel-tabs"><button v-for="c in channels" :key="c.name" :class="{on:channel===c.name}" @click="switchChannel(c.name)"><b>{{ c.name }}</b><small>{{ c.desc }}</small></button></nav>
    <section v-if="channel !== '主论坛'" class="daily-news"><header><b>{{ news.title || `${channel} 当日新闻` }}</b><button @click="loadNews">换一批</button></header><ul><li v-for="item in news.items||[]" :key="item">{{ item }}</li></ul></section>
    <div class="compose forum-compose-rich"><textarea v-model.trim="text" rows="4" :placeholder="roleId ? `以 ${activeRoleName} 发言...` : `在「${channel}」说点什么`"></textarea><div class="compose-side"><RolePicker v-model="roleId" :cards="cards"/><button @click="toggleImages">图片</button><button v-if="channel!=='主论坛'" @click="npcComment">刷新人机</button><button class="primary" @click="post">发送</button></div></div>
    <div v-if="pickerOpen" class="image-picker"><input type="file" accept="image/*" multiple @change="onFiles"><button v-for="img in library" :key="img.url" @click="addImage(img.url)"><img :src="img.url"><span>使用</span></button><small v-if="!library.length">暂无本地图库，先选择图片上传。</small></div>
    <div v-if="images.length" class="preview"><span v-for="img in images" :key="img"><img :src="img"><button @click="images=images.filter(x=>x!==img)">×</button></span></div>
    <section class="post-list-rich"><article v-for="p in posts" :key="p.id" class="post rich-post"><header><span class="post-avatar"><img v-if="p.user_avatar" :src="p.user_avatar"><b v-else>{{ initial(p.user_name) }}</b></span><div><b>{{p.user_name}}</b><time>{{ new Date(p.created_at*1000).toLocaleString() }}</time></div></header><p>{{p.content}}</p><div v-if="p.images?.length" class="post-images"><img v-for="img in p.images" :src="img" :key="img"></div></article><p v-if="!posts.length" class="hint">这个频道暂时无人发言。</p></section>
  </section>
</template>
<script setup>
import { computed, onMounted, ref } from 'vue'; import { siteApi, sessionHeaders } from '../lib/api.js'; import RolePicker from '../components/RolePicker.vue'
const props=defineProps({session:String}); const posts=ref([]), text=ref(''), images=ref([]), pickerOpen=ref(false), library=ref(loadLib()), cards=ref([]), roleId=ref(''), channel=ref('主论坛'), news=ref({})
const channels=[{name:'主论坛',desc:'营地闲聊'},{name:'渊',desc:'黎守 / 公寓 / 哨站'},{name:'赤红新星',desc:'工业与边境'},{name:'西陆联盟',desc:'教廷 / 伪神 / 猎魔'},{name:'渊东',desc:'群岛与航运'},{name:'悬赏栏',desc:'委托 / 线索 / 寻物'}]
const activeRoleName=computed(()=>cards.value.find(c=>String(c.id)===String(roleId.value))?.source_name||'角色')
const channelDesc=computed(()=>channels.find(c=>c.name===channel.value)?.desc||'')
function initial(s='?'){return String(s||'?').trim().slice(0,1)||'?'}
function loadLib(){try{return JSON.parse(localStorage.getItem('WEIREN_IMAGE_LIBRARY')||'[]')}catch{return[]}}
function saveLib(){localStorage.setItem('WEIREN_IMAGE_LIBRARY',JSON.stringify(library.value.slice(0,60)))}
async function load(){posts.value=await siteApi(`/api/forum/posts?channel=${encodeURIComponent(channel.value)}`)}
async function loadNews(){if(channel.value==='主论坛'){news.value={};return} news.value=await siteApi(`/api/forum/daily-news?channel=${encodeURIComponent(channel.value)}`).catch(()=>({}))}
async function loadAll(){await Promise.all([load(),loadNews(),loadCards()])}
async function loadCards(){cards.value=await siteApi('/api/identity-cards',{headers:sessionHeaders(props.session)}).catch(()=>[])}
async function switchChannel(c){channel.value=c; await loadAll(); if(c!=='主论坛' && Math.random()<0.35) await npcComment(false)}
function toggleImages(){pickerOpen.value=!pickerOpen.value}
function addImage(url){if(!images.value.includes(url))images.value.push(url)}
function onFiles(e){[...e.target.files].forEach(f=>{const r=new FileReader(); r.onload=()=>{const url=r.result; library.value=[{url,name:f.name,time:Date.now()},...library.value.filter(x=>x.url!==url)].slice(0,60); saveLib(); addImage(url)}; r.readAsDataURL(f)}); e.target.value=''}
async function post(){if(!text.value&&!images.value.length)return; await siteApi('/api/forum/posts',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify({channel:channel.value,content:text.value,images:images.value,role_card_id:roleId.value})}); text.value=''; images.value=[]; pickerOpen.value=false; await load()}
async function npcComment(show=true){try{await siteApi('/api/forum/npc-comment',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify({channel:channel.value,topic:text.value || news.value?.title || ''})}); await load()}catch(e){if(show) alert(e.message)}}
onMounted(loadAll)
</script>
