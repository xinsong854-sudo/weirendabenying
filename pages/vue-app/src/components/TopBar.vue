<template><header class="topbar"><div><b>{{ user?.nick_name || user?.name }}</b><span>{{ user?.uuid }}</span></div><button @click="$emit('logout')">退出</button></header></template>
<script setup>defineProps({ user: Object }); defineEmits(['logout'])</script>
