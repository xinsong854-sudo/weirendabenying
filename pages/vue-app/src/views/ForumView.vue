<template><section class="panel"><h2>主论坛</h2><div class="compose"><input v-model.trim="text" placeholder="说点什么"><button @click="toggleImages">图片</button><button @click="post">发送</button></div><div v-if="pickerOpen" class="image-picker"><input type="file" accept="image/*" multiple @change="onFiles"><button v-for="img in library" :key="img.url" @click="addImage(img.url)"><img :src="img.url"><span>使用</span></button><small v-if="!library.length">暂无本地图库，先选择图片上传。</small></div><div v-if="images.length" class="preview"><span v-for="img in images" :key="img"><img :src="img"><button @click="images=images.filter(x=>x!==img)">×</button></span></div><article v-for="p in posts" :key="p.id" class="post"><b>{{p.user_name}}</b><p>{{p.content}}</p><div v-if="p.images?.length" class="post-images"><img v-for="img in p.images" :src="img" :key="img"></div><time>{{ new Date(p.created_at*1000).toLocaleString() }}</time></article></section></template>
<script setup>
import { onMounted, ref } from 'vue'; import { siteApi, sessionHeaders } from '../lib/api.js'
const props=defineProps({session:String}); const posts=ref([]), text=ref(''), images=ref([]), pickerOpen=ref(false), library=ref(loadLib())
function loadLib(){try{return JSON.parse(localStorage.getItem('WEIREN_IMAGE_LIBRARY')||'[]')}catch{return[]}}
function saveLib(){localStorage.setItem('WEIREN_IMAGE_LIBRARY',JSON.stringify(library.value.slice(0,60)))}
async function load(){posts.value=await siteApi('/api/forum/posts?channel=主论坛')}
function toggleImages(){pickerOpen.value=!pickerOpen.value}
function addImage(url){if(!images.value.includes(url))images.value.push(url)}
function onFiles(e){[...e.target.files].forEach(f=>{const r=new FileReader(); r.onload=()=>{const url=r.result; library.value=[{url,name:f.name,time:Date.now()},...library.value.filter(x=>x.url!==url)].slice(0,60); saveLib(); addImage(url)}; r.readAsDataURL(f)}); e.target.value=''}
async function post(){if(!text.value&&!images.value.length)return; await siteApi('/api/forum/posts',{method:'POST',headers:sessionHeaders(props.session),body:JSON.stringify({channel:'主论坛',content:text.value,images:images.value})}); text.value=''; images.value=[]; pickerOpen.value=false; await load()}
onMounted(load)
</script>
