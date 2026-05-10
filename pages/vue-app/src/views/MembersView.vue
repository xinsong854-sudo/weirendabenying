<template><section class="panel"><h2>成员</h2><article v-for="m in members" :key="m.uuid" class="member"><img v-if="m.avatar" :src="m.avatar"><div><b>{{m.name}}</b><small>{{m.uuid}}</small></div></article></section></template>
<script setup>
import { onMounted, ref } from 'vue'; import { siteApi } from '../lib/api.js'
const members=ref([]); onMounted(async()=>{members.value=await siteApi('/api/members')})
</script>
