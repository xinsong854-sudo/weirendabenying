<template>
  <section class="panel codex-view">
    <h2>伪物图鉴</h2>
    <div class="risk-tabs"><button v-for="r in risks" :key="r.v" :class="{on:risk===r.v}" @click="risk=r.v">{{ r.t }} <small>{{ count(r.v) }}</small></button></div>
    <div class="codex-grid">
      <button v-for="e in entries" :key="e.uuid" class="codex-card" @click="selected=e">
        <img v-if="e.image" :src="e.image"><i>{{ riskOf(e).icon }}</i><b>{{ e.name }}</b><small>{{ short(e.description) }}</small>
      </button>
    </div>
    <div v-if="selected" class="drawer detail-page" @click.self="selected=null"><article><button class="close" @click="selected=null">×</button><img v-if="selected.image" class="detail-img" :src="selected.image"><h3>{{ selected.name }}</h3><b class="pill">{{ riskOf(selected).t }}</b><p>{{ selected.description }}</p></article></div>
  </section>
</template>
<script setup>
import { computed, ref } from 'vue'
import archive from '../pseudo-human-data.json'
const risk=ref('all'), selected=ref(null)
const risks=[{v:'all',t:'全部',icon:'◆'},{v:'safe',t:'安全级',icon:'🟩'},{v:'caution',t:'注意级',icon:'🟨'},{v:'danger',t:'危险级',icon:'🟧'},{v:'hazard',t:'危害级',icon:'🟥'},{v:'unknown',t:'待定',icon:'⬜'}]
const all=computed(()=>((archive.lore||{})['伪物档案']||[]))
const entries=computed(()=>risk.value==='all'?all.value:all.value.filter(e=>riskOf(e).v===risk.value))
function riskOf(e){const txt=`${e.risk||''} ${e.name||''} ${e.description||''}`.toLowerCase(); if(/🟥|hazard|危害|禁忌|高危/.test(txt))return risks[4]; if(/🟧|danger|危险/.test(txt))return risks[3]; if(/🟨|caution|注意|谨慎/.test(txt))return risks[2]; if(/🟩|safe|安全|无害/.test(txt))return risks[1]; return risks[5]}
function count(v){return v==='all'?all.value.length:all.value.filter(e=>riskOf(e).v===v).length}
function short(s=''){return String(s).replace(/\s+/g,' ').slice(0,80)}
</script>
