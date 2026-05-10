<template>
  <div class="role-picker">
    <button class="role-trigger" :class="{empty:!modelValue}" @click="open=!open">
      <img v-if="active?.avatar_img" :src="active.avatar_img"><span v-else>{{ active ? initial(active.source_name) : '＋' }}</span><i>{{ active ? 'RP' : '角色' }}</i>
    </button>
    <div v-if="open" class="role-pop">
      <header><b>选择发言角色</b><button @click="open=false">×</button></header>
      <button class="role-item none" @click="pick('')">不用角色</button>
      <button v-for="c in cards" :key="c.id" class="role-item" :class="{on:String(c.id)===String(modelValue)}" @click="pick(String(c.id))">
        <img v-if="c.avatar_img" :src="c.avatar_img"><span v-else>{{ initial(c.source_name) }}</span><b>{{ c.source_name }}</b><small>HP {{ c.hp_current }}/{{ c.hp_max }}</small>
      </button>
      <p v-if="!cards.length">还没有身份卡，先去“身份卡”导入。</p>
    </div>
  </div>
</template>
<script setup>
import { computed, ref } from 'vue'
const props=defineProps({cards:Array,modelValue:String}); const emit=defineEmits(['update:modelValue'])
const open=ref(false); const active=computed(()=>props.cards?.find(c=>String(c.id)===String(props.modelValue)))
function initial(s='?'){return String(s||'?').slice(0,1)}
function pick(id){emit('update:modelValue',id); open.value=false}
</script>
