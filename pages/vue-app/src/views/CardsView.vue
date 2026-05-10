<template><section class="panel"><h2>身份卡</h2><div class="compose"><input v-model.trim="input" placeholder="粘贴 t.nieta.art 短链 / UUID"><button @click="importCard">导入</button></div><p class="hint">{{hint}}</p><article v-for="c in cards" :key="c.id" class="card-row"><img v-if="c.avatar_img" :src="c.avatar_img"><div><b>{{c.source_name}}</b><small>{{c.source_uuid}}</small></div><button @click="del(c.id)">删除</button></article></section></template>
<script setup>
import { onMounted, ref } from 'vue'; import { siteApi, sessionHeaders } from '../lib/api.js'
const props=defineProps({session:String}); const cards=ref([]), input=ref(''), hint=ref('')
async function load(){cards.value=await siteApi('/api/identity-cards',{headers:sessionHeaders(props.session)})}
async function importCard(){try{hint.value='解析中...'; const data=await siteApi(`/api/knight/resolve?uuid=${encodeURIComponent(input.value)}`); const profile={...(data.raw||{}), uuid:data.oc.uuid, name:data.oc.name, avatar_img:data.oc.avatar_img, creator_uuid:data.author.uuid, owner_uuid:data.author.uuid, oc_bio:{name:data.oc.name, description:data.oc.bio_summary?.background||'', persona:data.oc.bio_summary?.persona||''}}; const saved=await siteApi('/api/identity-cards',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify({profile})}); hint.value='已导入 '+saved.card.source_name; input.value=''; await load()}catch(e){hint.value=e.message}}
async function del(id){await siteApi('/api/identity-cards/delete',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify({id})}); await load()}
onMounted(load)
</script>
