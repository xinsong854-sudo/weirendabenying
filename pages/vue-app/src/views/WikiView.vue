<template>
  <section class="panel wiki-view wiki-archive">
    <header class="archive-hero">
      <div>
        <span class="eyebrow">PSEUDO-HUMAN FIELD ARCHIVE</span>
        <h2>伪人大本营 · Wiki 档案馆</h2>
        <p>表界、里界、伪人、哨站与伪物在这里交叉归档。档案不是静态百科，而是跑团、投稿、图鉴和论坛共同写出来的异常履历。</p>
      </div>
      <button class="primary ghost-primary" @click="editorOpen=!editorOpen">{{ editorOpen?'收起投稿':'提交档案' }}</button>
    </header>

    <section class="world-brief">
      <article v-for="b in worldBrief" :key="b.k" :class="['brief-card',b.tone]">
        <small>{{ b.k }}</small><b>{{ b.v }}</b><p>{{ b.d }}</p>
      </article>
    </section>

    <form v-if="editorOpen" class="wiki-editor elevated-editor" @submit.prevent="submit">
      <div class="form-grid"><label>归档分类<input v-model.trim="draft.target" list="wiki-cats" placeholder="例如：世界观 / 伪物档案 / 表界——哨站"><datalist id="wiki-cats"><option v-for="c in categories" :key="c.name" :value="c.name" /></datalist></label><label>提交类型<select v-model="draft.submit_type"><option>新增词条</option><option>修订词条</option><option>新建分类</option><option>图鉴投稿</option></select></label></div>
      <label>条目名<input v-model.trim="draft.title" placeholder="档案标题 / 伪物编号 / 事件代号"></label>
      <label>正文<textarea v-model.trim="draft.content" rows="7" placeholder="建议格式：发现地点、风险等级、观测记录、收容措施、特殊效果、论坛/跑团可触发内容……"></textarea></label>
      <div class="editor-actions"><button class="primary" :disabled="submitting">{{ submitting?'提交中':'提交审核' }}</button><span class="hint">{{ submitHint }}</span></div>
    </form>

    <section v-if="isAdmin" class="review-box archive-review"><div class="section-head small"><h3>待审核队列</h3><button @click="loadReviews">刷新</button></div><article v-for="r in reviews" :key="r.id" class="review-item"><b>{{ r.submit_type }} · {{ r.target }}</b><small>{{ r.user_name }} · {{ new Date(r.created_at*1000).toLocaleString() }}</small><p>{{ r.content }}</p><div><button @click="review(r.id,'approved')">通过并归档</button><button @click="review(r.id,'rejected')">驳回</button></div></article><p v-if="!reviews.length" class="hint">暂无待审核。</p></section>

    <div class="archive-toolbar"><div class="archive-search"><span>⌕</span><input v-model.trim="query" placeholder="搜索世界观、伪人、里界、伪物、哨站……"></div><button @click="query=''">清空</button></div>

    <div class="archive-layout">
      <aside class="archive-nav">
        <button v-for="cat in filteredCategories" :key="cat.name" :class="{on:openCat===cat.name}" @click="openCat=openCat===cat.name?'':cat.name">
          <b>{{ cat.name }}</b><small>{{ cat.entries.length }} 条 · {{ categoryHint(cat.name) }}</small>
        </button>
      </aside>
      <section class="archive-cards">
        <article v-for="cat in visibleCategories" :key="cat.name" :class="['archive-category',categoryTone(cat.name)]">
          <header><div><span>{{ categoryHint(cat.name) }}</span><h3>{{ cat.name }}</h3></div><small>{{ cat.entries.length }} 条记录</small></header>
          <div class="archive-entry-grid">
            <button v-for="e in cat.entries.slice(0, query ? 80 : 18)" :key="e.uuid || e.name" class="archive-entry" @click="selected={...e,category:cat.name}">
              <i>{{ entryMark(cat.name,e) }}</i><b>{{ e.name }}</b><small>{{ short(e.description, 132) }}</small>
            </button>
          </div>
        </article>
      </section>
    </div>

    <div v-if="selected" class="drawer archive-drawer" @click.self="selected=null"><article><button class="close" @click="selected=null">×</button><span class="eyebrow">{{ selected.category }}</span><h3>{{ selected.name }}</h3><div class="entry-meta"><b>{{ categoryHint(selected.category) }}</b><small>{{ selected.uuid || '未登记 UUID' }}</small></div><p>{{ selected.description }}</p></article></div>
  </section>
</template>
<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import archive from '../pseudo-human-data.json'
import { siteApi, sessionHeaders, USER_CACHE_KEY } from '../lib/api.js'
const props=defineProps({session:String})
const query=ref(''), openCat=ref('世界观'), selected=ref(null), editorOpen=ref(false), submitting=ref(false), submitHint=ref(''), reviews=ref([])
const draft=reactive({target:'伪物档案',submit_type:'新增词条',title:'',content:'',images:[]})
const categories=computed(()=>Object.entries(archive.lore||{}).map(([name,entries])=>({name,entries})))
const filteredCategories=computed(()=>{const q=query.value.toLowerCase(); if(!q)return categories.value; return categories.value.map(c=>({...c,entries:c.entries.filter(e=>`${c.name} ${e.name} ${e.description}`.toLowerCase().includes(q))})).filter(c=>c.entries.length)})
const visibleCategories=computed(()=>query.value?filteredCategories.value:(openCat.value?filteredCategories.value.filter(c=>c.name===openCat.value):filteredCategories.value.slice(0,4)))
const isAdmin=computed(()=>['chief','deputy','admin'].includes(JSON.parse(localStorage.getItem(USER_CACHE_KEY)||'{}')?.role||''))
const worldBrief=computed(()=>[
  {k:'核心异常',v:'里界 / 门 / 伪物',tone:'inner',d:'门通常出现在空间交界；伪物来自里界，效果伴随侵蚀与副作用。'},
  {k:'秩序机构',v:'黎守 · 对伪课',tone:'order',d:'不以消灭伪人为目标，而是维持人伪平衡，收容登记危险异常。'},
  {k:'社区网络',v:'公寓 · 哨站 · 灯塔',tone:'home',d:'伪人生活、学习、委托和两界交流的基础设施。'},
  {k:'玩法闭环',v:'跑团 → 履历 → 图鉴',tone:'loop',d:'探索改变身份卡，投稿写入图鉴，伪物与能力再反馈论坛。'}
])
function short(s='',n=90){return String(s).replace(/\s+/g,' ').slice(0,n)}
function categoryHint(n){if(n.includes('伪物'))return 'Pseudo-Artifact'; if(n.includes('伪人'))return 'Pseudo-Human'; if(n.includes('里界'))return 'Inner Side'; if(n.includes('表界'))return 'Surface'; if(n.includes('哨站'))return 'Outpost'; if(n.includes('公寓'))return 'Apartment'; if(n.includes('人类'))return 'Human'; return 'Archive'}
function categoryTone(n){if(n.includes('伪物'))return 'tone-artifact'; if(n.includes('里界'))return 'tone-inner'; if(n.includes('伪人'))return 'tone-being'; if(n.includes('哨站')||n.includes('公寓'))return 'tone-home'; return 'tone-plain'}
function entryMark(cat,e){const t=`${cat} ${e?.description||''}`; if(/🟥|HAZARD|危害/.test(t))return '🟥'; if(/🟧|DANGER|危险/.test(t))return '🟧'; if(/🟨|CAUTION|注意/.test(t))return '🟨'; if(/🟩|SAFE|安全/.test(t))return '🟩'; if(cat.includes('里界'))return '門'; if(cat.includes('伪物'))return '物'; if(cat.includes('哨站'))return '站'; return '档'}
async function submit(){submitting.value=true; try{await siteApi('/api/wiki/submissions',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify(draft)}); submitHint.value='已进入审核队列；伪物档案通过后会写入图鉴并返还奖励'; draft.title=''; draft.content=''; await loadReviews()}catch(e){submitHint.value=e.message}finally{submitting.value=false}}
async function loadReviews(){if(!isAdmin.value)return; reviews.value=await siteApi('/api/wiki/submissions?status=pending',{headers:sessionHeaders(props.session)}).catch(()=>[])}
async function review(id,action){await siteApi('/api/wiki/review',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify({id,action})}); await loadReviews()}
onMounted(loadReviews)
</script>
