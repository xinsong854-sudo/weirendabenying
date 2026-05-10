<template>
  <section class="panel wiki-view">
    <div class="section-head"><div><h2>Wiki 档案馆</h2><p>浏览设定、提交新条目，管理员可在审核队列里一键归档。</p></div><button class="primary" @click="editorOpen=!editorOpen">{{ editorOpen?'收起投稿':'提交 Wiki' }}</button></div>

    <form v-if="editorOpen" class="wiki-editor" @submit.prevent="submit">
      <div class="form-grid"><label>分类<input v-model.trim="draft.target" list="wiki-cats" placeholder="例如：世界观 / 伪物档案"><datalist id="wiki-cats"><option v-for="c in categories" :key="c.name" :value="c.name" /></datalist></label><label>类型<select v-model="draft.submit_type"><option>新增词条</option><option>修订词条</option><option>新建分类</option></select></label></div>
      <label>条目名<input v-model.trim="draft.title" placeholder="条目标题"></label>
      <label>正文<textarea v-model.trim="draft.content" rows="6" placeholder="写设定、档案、修订说明……"></textarea></label>
      <button class="primary" :disabled="submitting">{{ submitting?'提交中':'提交审核' }}</button><span class="hint">{{ submitHint }}</span>
    </form>

    <section v-if="isAdmin" class="review-box"><div class="section-head small"><h3>待审核队列</h3><button @click="loadReviews">刷新</button></div><article v-for="r in reviews" :key="r.id" class="review-item"><b>{{ r.submit_type }} · {{ r.target }}</b><small>{{ r.user_name }} · {{ new Date(r.created_at*1000).toLocaleString() }}</small><h4>{{ r.title }}</h4><p>{{ r.content }}</p><div><button @click="review(r.id,'approved')">通过</button><button @click="review(r.id,'rejected')">驳回</button></div></article><p v-if="!reviews.length" class="hint">暂无待审核。</p></section>

    <div class="compose"><input v-model.trim="query" placeholder="搜索条目 / 分类"><button @click="query=''">清空</button></div>
    <div class="wiki-grid"><article v-for="cat in filteredCategories" :key="cat.name" class="wiki-cat"><button class="cat-head" @click="openCat=openCat===cat.name?'':cat.name"><b>{{ cat.name }}</b><small>{{ cat.entries.length }} 条</small></button><div v-if="openCat===cat.name || query" class="entry-list"><button v-for="e in cat.entries.slice(0, query ? 50 : 12)" :key="e.uuid" @click="selected=e"><b>{{ e.name }}</b><small>{{ short(e.description) }}</small></button></div></article></div>
    <div v-if="selected" class="drawer" @click.self="selected=null"><article><button class="close" @click="selected=null">×</button><h3>{{ selected.name }}</h3><p>{{ selected.description }}</p></article></div>
  </section>
</template>
<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import archive from '../pseudo-human-data.json'
import { siteApi, sessionHeaders } from '../lib/api.js'
const props=defineProps({session:String})
const query=ref(''), openCat=ref(''), selected=ref(null), editorOpen=ref(false), submitting=ref(false), submitHint=ref(''), reviews=ref([])
const draft=reactive({target:'',submit_type:'新增词条',title:'',content:''})
const categories=computed(()=>Object.entries(archive.lore||{}).map(([name,entries])=>({name,entries})))
const filteredCategories=computed(()=>{const q=query.value.toLowerCase(); if(!q)return categories.value; return categories.value.map(c=>({...c,entries:c.entries.filter(e=>`${c.name} ${e.name} ${e.description}`.toLowerCase().includes(q))})).filter(c=>c.entries.length)})
const isAdmin=computed(()=>['chief','deputy','admin'].includes(JSON.parse(localStorage.getItem('WEIREN_USER')||'{}')?.role||''))
function short(s=''){return String(s).replace(/\s+/g,' ').slice(0,90)}
async function submit(){submitting.value=true; try{await siteApi('/api/wiki/submissions',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify(draft)}); submitHint.value='已进入审核队列'; draft.title=''; draft.content=''; await loadReviews()}catch(e){submitHint.value=e.message}finally{submitting.value=false}}
async function loadReviews(){if(!isAdmin.value)return; reviews.value=await siteApi('/api/wiki/submissions?status=pending',{headers:sessionHeaders(props.session)}).catch(()=>[])}
async function review(id,action){await siteApi('/api/wiki/review',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify({id,action})}); await loadReviews()}
onMounted(loadReviews)
</script>
