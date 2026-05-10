<template>
  <section class="legacy-archive wiki-view">
    <div class="page-actions"><button class="back-note primary" @click="editorOpen=!editorOpen">{{ editorOpen?'收起投稿':'改 Wiki / 新增词条' }}</button></div>
    <header class="archive-marquee wiki-marquee"><span class="ritual-label">WEIREN ARCHIVE</span><h1>Wiki 档案馆</h1><p>这里不是百科首页，而是伪人大本营的卷宗柜：表界、里界、伪人、哨站、伪物和活动记录会按层级归档。投稿审核通过后，伪物类条目会进入图鉴数据库并返还背包奖励。</p></header>

    <form v-if="editorOpen" class="wiki-submit-panel wiki-editor-panel" @submit.prevent="submit">
      <div class="wiki-form-grid"><label>分类名称<input v-model.trim="draft.target" list="wiki-cats" placeholder="世界观 / 里界 / 伪物档案"><datalist id="wiki-cats"><option v-for="c in categories" :key="c.name" :value="c.name" /></datalist></label><label>编辑类型<select v-model="draft.submit_type"><option>新增词条</option><option>修订词条</option><option>新建分类</option><option>图鉴投稿</option></select></label><label>条目名称<input v-model.trim="draft.title" placeholder="档案标题"></label></div>
      <label>正文内容<textarea v-model.trim="draft.content" rows="6" placeholder="写条目正文、修订内容、设定说明。伪物档案建议写：发现地点、等级、收容措施、特殊效果、副作用。"></textarea></label>
      <div class="editor-actions"><button class="back-note primary" :disabled="submitting">{{ submitting?'提交中':'提交审核' }}</button><span class="hint">{{ submitHint }}</span></div>
    </form>

    <section v-if="isAdmin" class="review-box"><div class="section-head small"><h3>待审核队列</h3><button class="back-note" @click="loadReviews">刷新</button></div><article v-for="r in reviews" :key="r.id" class="review-item"><b>{{ r.submit_type }} · {{ r.target }}</b><small>{{ r.user_name }} · {{ new Date(r.created_at*1000).toLocaleString() }}</small><p>{{ r.content }}</p><div><button @click="review(r.id,'approved')">通过并归档</button><button @click="review(r.id,'rejected')">驳回</button></div></article><p v-if="!reviews.length" class="wiki-empty-tip">暂无待审核。</p></section>

    <div class="search-bar"><span class="sicon">⌕</span><input v-model.trim="query" placeholder="搜索档案 / 分类 / 词条"></div>
    <div class="wiki-hierarchy" :class="{'is-root':!openCat && !query}">
      <aside class="wiki-major">
        <button v-for="cat in filteredCategories" :key="cat.name" :class="{active:openCat===cat.name}" @click="openCat=openCat===cat.name?'':cat.name"><b>{{ cat.name }}</b><small>{{ cat.entries.length }} 条 · {{ categoryHint(cat.name) }}</small></button>
      </aside>
      <section class="wiki-drill-panel">
        <header class="drill-head"><div><span class="ritual-label">SELECT ARCHIVE VOLUME</span><h2>{{ openCat || (query ? '搜索结果' : '选择档案卷宗') }}</h2><p>{{ openCat ? categoryHint(openCat) + ' / 当前栏目记录' : '从左侧选择卷宗；移动端可直接向下浏览分类。' }}</p></div><button v-if="openCat" class="back-note" @click="openCat=''">返回卷宗</button></header>
        <div v-if="!visibleCategories.length" class="wiki-empty-tip">没有匹配到档案。</div>
        <template v-for="cat in visibleCategories" :key="cat.name">
          <div v-if="!openCat && query" class="artifact-warning"><b>{{ cat.name }}</b><span>{{ cat.entries.length }} 条匹配记录</span></div>
          <div class="drill-grid">
            <button v-for="e in cat.entries.slice(0, query ? 60 : 24)" :key="e.uuid || e.name" @click="selected={...e,category:cat.name}"><b>{{ e.name }}</b><small>{{ short(e.description,115) }}</small><i>{{ entryMark(cat.name,e) }} / OPEN</i></button>
          </div>
        </template>
      </section>
    </div>

    <div v-if="selected" class="drawer" @click.self="selected=null"><article><button class="close" @click="selected=null">×</button><span class="ritual-label">{{ selected.category }}</span><h3>{{ selected.name }}</h3><b class="pill">{{ categoryHint(selected.category) }}</b><p>{{ selected.description }}</p></article></div>
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
const visibleCategories=computed(()=>query.value?filteredCategories.value:(openCat.value?filteredCategories.value.filter(c=>c.name===openCat.value):filteredCategories.value.slice(0,2)))
const isAdmin=computed(()=>['chief','deputy','admin'].includes(JSON.parse(localStorage.getItem(USER_CACHE_KEY)||'{}')?.role||''))
function short(s='',n=90){return String(s).replace(/\s+/g,' ').slice(0,n)}
function categoryHint(n){if(n.includes('伪物'))return '伪物、异常物件与收容记录'; if(n.includes('伪人'))return '伪人、种群与登记档案'; if(n.includes('里界'))return '门后空间与探索记录'; if(n.includes('表界'))return '现实侧势力与地点'; if(n.includes('哨站'))return '两界交流与委托节点'; if(n.includes('公寓'))return '伪人社区住户登记'; if(n.includes('人类'))return '人类调查员与组织'; return '世界观卷宗'}
function entryMark(cat,e){const t=`${cat} ${e?.description||''}`; if(/🟥|HAZARD|危害/.test(t))return '🟥'; if(/🟧|DANGER|危险/.test(t))return '🟧'; if(/🟨|CAUTION|注意/.test(t))return '🟨'; if(/🟩|SAFE|安全/.test(t))return '🟩'; if(cat.includes('里界'))return '門'; if(cat.includes('伪物'))return '物'; if(cat.includes('哨站'))return '站'; return '档'}
async function submit(){submitting.value=true; try{await siteApi('/api/wiki/submissions',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify(draft)}); submitHint.value='已进入审核队列'; draft.title=''; draft.content=''; await loadReviews()}catch(e){submitHint.value=e.message}finally{submitting.value=false}}
async function loadReviews(){if(!isAdmin.value)return; reviews.value=await siteApi('/api/wiki/submissions?status=pending',{headers:sessionHeaders(props.session)}).catch(()=>[])}
async function review(id,action){await siteApi('/api/wiki/review',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify({id,action})}); await loadReviews()}
onMounted(loadReviews)
</script>
