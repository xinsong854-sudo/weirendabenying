<template>
  <section class="panel forum-view-rich">
    <header class="forum-head"><div><span class="ritual-label">REVERSE ARCHIVE / 1999</span><h2>{{ channel }}</h2><p>{{ channelDesc }}</p></div><button class="primary" @click="loadAll">刷新</button></header>
    <nav class="forum-channel-tabs"><button v-for="c in channels" :key="c.name" :class="{on:channel===c.name}" @click="switchChannel(c.name)"><b>{{ c.name }}</b><small>{{ c.desc }}</small></button></nav>
    <section v-if="channel !== '主论坛'" class="daily-news"><header><b>{{ news.title || `${channel} 当日新闻` }}</b><button @click="loadNews">换一批</button></header><ul><li v-for="item in news.items||[]" :key="item">{{ item }}</li></ul></section>

    <section v-if="channel==='悬赏栏'" class="bounty-board"><header><b>悬赏栏</b><button class="back-note primary" @click="generateBounty">生成悬赏</button></header><article v-for="b in bounties" :key="b.id" class="bounty-card"><div><strong>{{ b.title }}</strong><small>{{ b.risk }} · {{ b.issuer }} · {{ b.status }}</small><p>{{ b.description }}</p><em>要求：{{ b.requirements || '无' }}</em><em>奖励：{{ b.reward?.benzhen || 0 }} 本真 {{ b.reward?.artifact?' / 伪物':'' }} {{ b.reward?.ability?` / 能力：${b.reward.ability}`:'' }}</em><p v-if="b.submission" class="submission-text">提交：{{ b.submission }}</p></div><div class="bounty-actions"><button v-if="b.status==='open'" @click="claimBounty(b)">领取</button><button v-if="b.status==='claimed'" @click="submitBounty(b)">提交完成</button><button v-if="isAdmin && b.status==='submitted'" @click="settleBounty(b,true)">结算通过</button><button v-if="isAdmin && b.status==='submitted'" @click="settleBounty(b,false)">驳回</button></div></article></section>

    <section class="effect-panel"><div><b>发帖表现层</b><small>能力冷却、灵视文本、残响评论、伪物共鸣</small></div><div class="effect-grid"><label>能力<select v-model="abilityId"><option value="0">不使用能力</option><option v-for="a in abilities" :key="a.id" :value="a.id" :disabled="a.cooldown_until && a.cooldown_until>nowSec">{{ a.name }} {{ a.cooldown_until&&a.cooldown_until>nowSec?`冷却 ${cooldown(a)}`:'' }}</option></select></label><label>伪物特效<select v-model="artifactEffectId"><option value="0">不使用伪物</option><option v-for="i in inventory" :key="i.id" :value="i.id">{{ i.name }}</option></select></label><label>样式<select v-model="effectType"><option value="">普通</option><option value="echo">残响评论</option></select></label></div><textarea v-model.trim="hiddenText" rows="2" placeholder="灵视可见文本：只有具备相关能力的角色应当知道的内容"></textarea></section>

    <div class="compose forum-compose-rich"><textarea v-model.trim="text" rows="4" :placeholder="roleId ? `以 ${activeRoleName} 发言...` : `在「${channel}」说点什么`"></textarea><div class="compose-side"><RolePicker v-model="roleId" :cards="cards"/><button @click="toggleImages">图片</button><button v-if="channel!=='主论坛'" @click="npcComment">刷新人机</button><button class="primary" @click="post">发送</button></div></div>
    <div v-if="pickerOpen" class="image-picker"><input type="file" accept="image/*" multiple @change="onFiles"><button v-for="img in library" :key="img.url" @click="addImage(img.url)"><img :src="img.url"><span>使用</span></button><small v-if="!library.length">暂无本地图库，先选择图片上传。</small></div>
    <div v-if="images.length" class="preview"><span v-for="img in images" :key="img"><img :src="img"><button @click="images=images.filter(x=>x!==img)">×</button></span></div>
    <section class="post-list-rich"><article v-for="p in posts" :key="p.id" class="post rich-post" :class="postClass(p.content)"><header><span class="post-avatar"><img v-if="p.user_avatar" :src="p.user_avatar"><b v-else>{{ initial(p.user_name) }}</b></span><div><b>{{p.user_name}}</b><time>{{ new Date(p.created_at*1000).toLocaleString() }}</time></div></header><p v-html="renderPost(p.content)"></p><div v-if="p.images?.length" class="post-images"><img v-for="img in p.images" :src="img" :key="img"></div></article><p v-if="!posts.length" class="hint">这个频道暂时无人发言。</p></section>
  </section>
</template>
<script setup>
import { computed, onMounted, ref, watch } from 'vue'; import { siteApi, sessionHeaders, USER_CACHE_KEY } from '../lib/api.js'; import RolePicker from '../components/RolePicker.vue'
const props=defineProps({session:String}); const posts=ref([]), text=ref(''), images=ref([]), pickerOpen=ref(false), library=ref(loadLib()), cards=ref([]), roleId=ref(''), channel=ref('主论坛'), news=ref({}), bounties=ref([]), abilities=ref([]), inventory=ref([]), abilityId=ref('0'), artifactEffectId=ref('0'), hiddenText=ref(''), effectType=ref(''), nowSec=ref(Math.floor(Date.now()/1000))
const channels=[{name:'主论坛',desc:'营地闲聊'},{name:'渊',desc:'黎守 / 公寓 / 哨站'},{name:'赤红新星',desc:'工业与边境'},{name:'西陆联盟',desc:'教廷 / 伪神 / 猎魔'},{name:'渊东',desc:'群岛与航运'},{name:'悬赏栏',desc:'委托 / 线索 / 寻物'}]
const activeRoleName=computed(()=>cards.value.find(c=>String(c.id)===String(roleId.value))?.source_name||'角色')
const channelDesc=computed(()=>channels.find(c=>c.name===channel.value)?.desc||'')
const isAdmin=computed(()=>['chief','deputy','admin'].includes(JSON.parse(localStorage.getItem(USER_CACHE_KEY)||'{}')?.role||''))
function initial(s='?'){return String(s||'?').trim().slice(0,1)||'?'}
function esc(s=''){return String(s).replace(/[&<>]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]))}
function renderPost(s=''){return esc(s).replace(/\[灵视可见\]([\s\S]*?)\[\/灵视可见\]/g,'<span class="spirit-text">灵视可见：$1</span>').replace(/\n/g,'<br>')}
function postClass(s=''){return {'echo-post':s.includes('【残响评论】'),'artifact-post':s.includes('【伪物共鸣'),'ability-post':s.includes('【能力：')}}
function cooldown(a){return Math.max(1,Math.ceil((a.cooldown_until-nowSec.value)/3600))+'h'}
function loadLib(){try{return JSON.parse(localStorage.getItem('WEIREN_IMAGE_LIBRARY')||'[]')}catch{return[]}}
function saveLib(){localStorage.setItem('WEIREN_IMAGE_LIBRARY',JSON.stringify(library.value.slice(0,60)))}
async function load(){posts.value=await siteApi(`/api/forum/posts?channel=${encodeURIComponent(channel.value)}`)}
async function loadNews(){if(channel.value==='主论坛'){news.value={};return} news.value=await siteApi(`/api/forum/daily-news?channel=${encodeURIComponent(channel.value)}`).catch(()=>({}))}
async function loadBounties(){bounties.value=await siteApi('/api/bounties',{headers:sessionHeaders(props.session)}).catch(()=>[])}
async function loadCards(){cards.value=await siteApi('/api/identity-cards',{headers:sessionHeaders(props.session)}).catch(()=>[])}
async function loadEffects(){abilities.value=await siteApi(`/api/abilities?card_id=${Number(roleId.value||0)}`,{headers:sessionHeaders(props.session)}).catch(()=>[]); const inv=await siteApi('/api/inventory',{headers:sessionHeaders(props.session)}).catch(()=>({items:[]})); inventory.value=inv.items||[]}
async function loadAll(){nowSec.value=Math.floor(Date.now()/1000); await Promise.all([load(),loadNews(),loadCards(),loadBounties(),loadEffects()])}
async function switchChannel(c){channel.value=c; await loadAll(); if(c!=='主论坛' && Math.random()<0.35) await npcComment(false)}
function toggleImages(){pickerOpen.value=!pickerOpen.value}
function addImage(url){if(!images.value.includes(url))images.value.push(url)}
function onFiles(e){[...e.target.files].forEach(f=>{const r=new FileReader(); r.onload=()=>{const url=r.result; library.value=[{url,name:f.name,time:Date.now()},...library.value.filter(x=>x.url!==url)].slice(0,60); saveLib(); addImage(url)}; r.readAsDataURL(f)}); e.target.value=''}
async function post(){if(!text.value&&!images.value.length&&!hiddenText.value)return; await siteApi('/api/forum/posts',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify({channel:channel.value,content:text.value,images:images.value,role_card_id:roleId.value,ability_id:Number(abilityId.value),artifact_effect_id:Number(artifactEffectId.value),hidden_text:hiddenText.value,effect_type:effectType.value})}); text.value=''; images.value=[]; hiddenText.value=''; abilityId.value='0'; artifactEffectId.value='0'; effectType.value=''; pickerOpen.value=false; await loadAll()}
async function npcComment(show=true){try{await siteApi('/api/forum/npc-comment',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify({channel:channel.value,topic:text.value || news.value?.title || ''})}); await load()}catch(e){if(show) alert(e.message)}}
async function generateBounty(){await siteApi('/api/bounties/generate',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify({channel:'悬赏栏'})}); await loadBounties()}
async function claimBounty(b){const cid=Number(roleId.value||cards.value[0]?.id||0); if(!cid)return alert('需要先导入/选择身份卡'); await siteApi('/api/bounties/claim',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify({id:b.id,card_id:cid})}); await loadBounties()}
async function submitBounty(b){const submission=prompt('提交完成记录：')||''; if(!submission.trim())return; await siteApi('/api/bounties/submit',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify({id:b.id,submission})}); await loadBounties()}
async function settleBounty(b,approved){await siteApi('/api/bounties/settle',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify({id:b.id,approved})}); await loadAll()}
watch(roleId, loadEffects)
onMounted(loadAll)
</script>
