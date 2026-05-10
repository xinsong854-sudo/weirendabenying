<template>
  <section class="panel wiki-view">
    <h2>Wiki</h2>
    <div class="compose"><input v-model.trim="query" placeholder="搜索条目 / 分类"><button @click="query=''">清空</button></div>
    <div class="wiki-grid">
      <article v-for="cat in filteredCategories" :key="cat.name" class="wiki-cat">
        <button class="cat-head" @click="openCat = openCat === cat.name ? '' : cat.name"><b>{{ cat.name }}</b><small>{{ cat.entries.length }} 条</small></button>
        <div v-if="openCat === cat.name || query" class="entry-list">
          <button v-for="e in cat.entries.slice(0, query ? 50 : 12)" :key="e.uuid" @click="selected = e"><b>{{ e.name }}</b><small>{{ short(e.description) }}</small></button>
        </div>
      </article>
    </div>
    <div v-if="selected" class="drawer" @click.self="selected=null"><article><button class="close" @click="selected=null">×</button><h3>{{ selected.name }}</h3><p>{{ selected.description }}</p></article></div>
  </section>
</template>
<script setup>
import { computed, ref } from 'vue'
import archive from '../pseudo-human-data.json'
const query=ref(''), openCat=ref(''), selected=ref(null)
const categories=computed(()=>Object.entries(archive.lore||{}).map(([name,entries])=>({name,entries})))
const filteredCategories=computed(()=>{const q=query.value.toLowerCase(); if(!q)return categories.value; return categories.value.map(c=>({...c,entries:c.entries.filter(e=>`${c.name} ${e.name} ${e.description}`.toLowerCase().includes(q))})).filter(c=>c.entries.length)})
function short(s=''){return String(s).replace(/\s+/g,' ').slice(0,90)}
</script>
