<template><section class="panel"><h2>主论坛</h2><div class="compose"><input v-model.trim="text" placeholder="说点什么"><button @click="post">发送</button></div><article v-for="p in posts" :key="p.id" class="post"><b>{{p.user_name}}</b><p>{{p.content}}</p><time>{{ new Date(p.created_at*1000).toLocaleString() }}</time></article></section></template>
<script setup>
import { onMounted, ref } from 'vue'; import { siteApi, sessionHeaders } from '../lib/api.js'
const props=defineProps({session:String}); const posts=ref([]), text=ref('')
async function load(){posts.value=await siteApi('/api/forum/posts?channel=主论坛')}
async function post(){if(!text.value)return; await siteApi('/api/forum/posts',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify({channel:'主论坛',content:text.value})}); text.value=''; await load()}
onMounted(load)
</script>
