<template><section class="panel inventory-view"><div class="section-head"><div><h2>伪物背包</h2><p>本真：<b>{{ benzhen }}</b> · 收藏那些大多没什么用、但很有意思的里界物品。</p></div><button class="primary" @click="draw">20 本真抽取</button></div><p class="hint">{{ hint }}</p><div class="artifact-shelf"><button v-for="it in items" :key="it.id" :class="['artifact-item',it.rarity]" @click="selected=it"><b>{{ it.name }}</b><small>{{ label(it.risk) }} · {{ rarity(it.rarity) }}</small><em>{{ it.obtained_from }}</em></button></div><div v-if="selected" class="drawer" @click.self="selected=null"><article><button class="close" @click="selected=null">×</button><h3>{{ selected.name }}</h3><b class="pill">{{ label(selected.risk) }} · {{ rarity(selected.rarity) }}</b><p>{{ selected.description }}</p><h4>探索效果</h4><p>{{ selected.effect }}</p></article></div></section></template>
<script setup>
import { onMounted, ref } from 'vue'; import { siteApi, sessionHeaders } from '../lib/api.js'
const props=defineProps({session:String}); const items=ref([]), benzhen=ref(0), hint=ref(''), selected=ref(null)
function label(r){return {safe:'🟩SAFE',caution:'🟨CAUTION',danger:'🟧DANGER',hazard:'🟥HAZARD'}[r]||'⬜UNKNOWN'}
function rarity(r){return {common:'普通',uncommon:'少见',rare:'稀有',legendary:'传说'}[r]||r}
async function load(){const d=await siteApi('/api/inventory',{headers:sessionHeaders(props.session)}); items.value=d.items||[]; benzhen.value=d.benzhen||0}
async function draw(){try{const d=await siteApi('/api/artifacts/draw',{method:'POST',headers:sessionHeaders(props.session),body:'{}'}); hint.value=`抽到了：${d.item.name}`; await load()}catch(e){hint.value=e.message}}
onMounted(load)
</script>