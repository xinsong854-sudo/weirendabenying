<template>
  <section class="legacy-archive codex-view">
    <div class="page-actions"><button class="back-note primary" @click="submitOpen=!submitOpen">{{ submitOpen?'收起投稿':'改 Wiki / 新增图鉴' }}</button></div>
    <header class="archive-marquee"><span class="ritual-label">REVERSE ARCHIVE / 1999</span><h1>伪物图鉴</h1><p>伪物资料需管理员审核后公开。审核通过的投稿会写入图鉴数据库，并给投稿者返还一件固化后的伪物实例。</p></header>

    <form v-if="submitOpen" class="wiki-submit-panel wiki-editor-panel" @submit.prevent="submitCodex">
      <div class="wiki-form-grid"><label>伪物名称<input v-model.trim="draft.name" placeholder="例如：迟到的门牌"></label><label>风险等级<select v-model="draft.risk"><option value="safe">🟩 SAFE</option><option value="caution">🟨 CAUTION</option><option value="danger">🟧 DANGER</option><option value="hazard">🟥 HAZARD</option><option value="unknown">⬜ UNKNOWN</option></select></label><label>图片 URL<input v-model.trim="draft.image" placeholder="可选"></label></div>
      <label>档案正文<textarea v-model.trim="draft.description" rows="6" placeholder="发现地点、收容措施、特殊效果、使用代价、坊间传闻……"></textarea></label>
      <div class="editor-actions"><button class="back-note primary" :disabled="submitting">{{ submitting?'提交中':'提交审核' }}</button><span class="hint">{{ hint }}</span></div>
    </form>

    <section class="wiki-drill-panel artifact-drill">
      <header class="drill-head artifact"><div><span class="ritual-label">REVERSE ARCHIVE / 1999</span><h2>内部图鉴</h2><p>按危险等级查看伪物。静态 Wiki 与数据库收录条目会合并显示。</p></div></header>
      <div class="risk-tabs"><button v-for="r in risks" :key="r.v" :class="{on:risk===r.v}" @click="risk=r.v">{{ r.t }} <small>{{ count(r.v) }}</small></button></div>
      <div class="artifact-files">
        <button v-for="e in entries" :key="e.uuid || e.name" class="artifact-file" @click="selected=e">
          <span v-if="!e.image" class="artifact-no">{{ riskOf(e).icon }}</span><img v-else class="artifact-no" :src="e.image" alt="">
          <span><h3>{{ e.name }}</h3><small>{{ e.artifact_id || e.artifact_code || riskOf(e).t }} · {{ e.source==='database'?'数据库收录':'静态档案' }}</small><p>{{ short(e.description) }}</p></span>
        </button>
      </div>
    </section>

    <div v-if="selected" class="drawer" @click.self="selected=null"><article><button class="close" @click="selected=null">×</button><img v-if="selected.image" class="detail-img" :src="selected.image"><span class="ritual-label">REVERSE ARCHIVE / 1999</span><h3>{{ selected.name }}</h3><b class="pill">{{ riskOf(selected).t }} · {{ selected.artifact_id || selected.artifact_code || '未编号' }}</b><p>{{ selected.description }}</p></article></div>
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
const staticEntries=computed(()=>(((archive.lore||{})['伪物图鉴']||[]).map(e=>({...e,source:e.source||'static'}))))
const all=computed(()=>[...dbEntries.value.map(e=>({...e,source:'database'})),...staticEntries.value])
const entries=computed(()=>risk.value==='all'?all.value:all.value.filter(e=>riskOf(e).v===risk.value))
function riskOf(e){const txt=`${e.risk||''} ${e.name||''} ${e.description||''}`.toLowerCase(); if(/🟥|hazard|危害|禁忌|高危/.test(txt))return risks[4]; if(/🟧|danger|危险/.test(txt))return risks[3]; if(/🟨|caution|注意|谨慎|污染/.test(txt))return risks[2]; if(/🟩|safe|安全|无害/.test(txt))return risks[1]; return risks[5]}
function count(v){return v==='all'?all.value.length:all.value.filter(e=>riskOf(e).v===v).length}
function short(s=''){return String(s).replace(/\s+/g,' ').slice(0,150)}
async function loadDb(){dbEntries.value=await siteApi('/api/codex/entries',{headers:sessionHeaders(props.session)}).catch(()=>[])}
async function submitCodex(){submitting.value=true; try{await siteApi('/api/codex/submit',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify(draft)}); hint.value='已提交审核'; draft.name=''; draft.image=''; draft.description=''}catch(e){hint.value=e.message}finally{submitting.value=false}}
onMounted(loadDb)
</script>
