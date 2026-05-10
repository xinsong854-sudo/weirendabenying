<template>
  <section class="panel codex-view codex-archive">
    <header class="archive-hero codex-hero"><div><span class="eyebrow">PSEUDO-ARTIFACT CODEX</span><h2>伪物图鉴</h2><p>伪物不再只是固定素材表：跑团、投稿、审核会持续把新伪物固化进数据库，并可能返还到投稿者背包。</p></div><button class="primary ghost-primary" @click="submitOpen=!submitOpen">{{ submitOpen?'收起投稿':'图鉴投稿' }}</button></header>
    <form v-if="submitOpen" class="wiki-editor elevated-editor" @submit.prevent="submitCodex"><div class="form-grid"><label>伪物名称<input v-model.trim="draft.name" placeholder="例如：不会走完的钟"></label><label>风险<select v-model="draft.risk"><option value="safe">🟩 SAFE</option><option value="caution">🟨 CAUTION</option><option value="danger">🟧 DANGER</option><option value="hazard">🟥 HAZARD</option><option value="unknown">⬜ UNKNOWN</option></select></label></div><label>图片 URL<input v-model.trim="draft.image" placeholder="可选：观测图 / 收容照片"></label><label>档案正文<textarea v-model.trim="draft.description" rows="7" placeholder="发现地点、收容措施、特殊效果、使用代价、坊间传闻……"></textarea></label><div class="editor-actions"><button class="primary" :disabled="submitting">{{ submitting?'提交中':'提交审核' }}</button><span class="hint">{{ hint }}</span></div></form>
    <div class="risk-tabs codex-tabs"><button v-for="r in risks" :key="r.v" :class="{on:risk===r.v}" @click="risk=r.v">{{ r.t }} <small>{{ count(r.v) }}</small></button></div>
    <div class="codex-grid elevated-codex-grid"><button v-for="e in entries" :key="e.uuid" :class="['codex-card',riskOf(e).v]" @click="selected=e"><img v-if="e.image" :src="e.image"><div v-else class="codex-placeholder">{{ riskOf(e).icon }}</div><i>{{ riskOf(e).icon }}</i><b>{{ e.name }}</b><em>{{ e.artifact_id || e.artifact_code || '未编号' }}</em><small>{{ short(e.description) }}</small></button></div>
    <div v-if="selected" class="drawer detail-page codex-drawer" @click.self="selected=null"><article><button class="close" @click="selected=null">×</button><img v-if="selected.image" class="detail-img" :src="selected.image"><span class="eyebrow">{{ selected.source==='database'?'DATABASE ENTRY':'STATIC ARCHIVE' }}</span><h3>{{ selected.name }}</h3><b class="pill">{{ riskOf(selected).t }} · {{ selected.artifact_id || selected.artifact_code || '未编号' }}</b><p>{{ selected.description }}</p></article></div>
  </section>
</template>
<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import archive from '../pseudo-human-data.json'
import { siteApi, sessionHeaders } from '../lib/api.js'
const props=defineProps({session:String})
const risk=ref('all'), selected=ref(null), submitOpen=ref(false), submitting=ref(false), hint=ref(''), dbEntries=ref([])
const draft=reactive({name:'',risk:'safe',image:'',description:''})
const risks=[{v:'all',t:'全部',icon:'◆'},{v:'safe',t:'安全级',icon:'🟩'},{v:'caution',t:'注意级',icon:'🟨'},{v:'danger',t:'危险级',icon:'🟧'},{v:'hazard',t:'危害级',icon:'🟥'},{v:'unknown',t:'待定',icon:'⬜'}]
const staticEntries=computed(()=>(((archive.lore||{})['伪物档案']||[]).map(e=>({...e,source:e.source||'static'}))))
const all=computed(()=>[...dbEntries.value.map(e=>({...e,source:'database'})),...staticEntries.value])
const entries=computed(()=>risk.value==='all'?all.value:all.value.filter(e=>riskOf(e).v===risk.value))
function riskOf(e){const txt=`${e.risk||''} ${e.name||''} ${e.description||''}`.toLowerCase(); if(/🟥|hazard|危害|禁忌|高危/.test(txt))return risks[4]; if(/🟧|danger|危险/.test(txt))return risks[3]; if(/🟨|caution|注意|谨慎|污染/.test(txt))return risks[2]; if(/🟩|safe|安全|无害/.test(txt))return risks[1]; return risks[5]}
function count(v){return v==='all'?all.value.length:all.value.filter(e=>riskOf(e).v===v).length}
function short(s=''){return String(s).replace(/\s+/g,' ').slice(0,96)}
async function loadDb(){dbEntries.value=await siteApi('/api/codex/entries',{headers:sessionHeaders(props.session)}).catch(()=>[])}
async function submitCodex(){submitting.value=true; try{await siteApi('/api/codex/submit',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify(draft)}); hint.value='已提交审核；通过后会进入图鉴数据库并返还伪物奖励'; draft.name=''; draft.image=''; draft.description=''}catch(e){hint.value=e.message}finally{submitting.value=false}}
onMounted(loadDb)
</script>
