<template>
  <section class="login-scene login-1999">
    <div class="login-ornament left">1999</div>
    <div class="login-ornament right">FILE</div>
    <div class="login-disclaimer"><span>隐私说明：手机号用于身份验证、安全防护与关联捏Ta已有资产；不会用于营销或分享给第三方，验证码验证完成后即时失效。</span><span aria-hidden="true">隐私说明：手机号用于身份验证、安全防护与关联捏Ta已有资产；不会用于营销或分享给第三方，验证码验证完成后即时失效。</span></div>
    <div class="login-stage-copy"><span>REVERSE ARCHIVE / 1999</span><h1>伪人大本营</h1><p>和我们一起，成为入吧</p><div class="stage-rule"><i></i><b>THE PSEUDO HUMAN DOSSIER</b><i></i></div></div>
    <div class="login-card labyrinth-window login-card-refined">
      <div class="window-title">IDENTITY RITUAL</div><div class="login-file-tab"><span>ACCESS FILE</span><b>404</b></div>
      <h1>捏Ta账号登录</h1><p class="tagline">使用捏Ta官方验证码登录，仅用于确认成员身份</p>
      <details class="login-why"><summary>我们为何需要你的手机号？</summary><ul><li><b>身份验证：</b>仅用于验证你是“捏Ta”平台的用户，以关联你的已有资产。</li><li><b>安全防护：</b>防止恶意注册与机器人攻击。</li><li><b>数据保护：</b>你的手机号仅作为登录凭证，本站后端不保存捏Ta token。</li></ul></details>
      <div class="field"><span class="prefix">+86</span><input v-model.trim="phone" type="tel" inputmode="numeric" maxlength="11" placeholder="输入捏Ta绑定手机号" autocomplete="tel"></div>
      <div class="field"><input v-model.trim="code" type="text" inputmode="numeric" maxlength="6" placeholder="验证码" autocomplete="one-time-code"><button class="code-btn" :disabled="sending || timer>0" @click="sendCode">{{ timer>0?`${timer}s`:'获取验证码' }}</button></div>
      <label class="agree"><input v-model="agree" type="checkbox"><span>我已阅读并同意 <a href="https://oss.talesofai.cn/static/blackboard/protocol-page/user-agreement.html" target="_blank" rel="noopener noreferrer">用户协议</a> 和 <a href="https://oss.talesofai.cn/static/blackboard/protocol-page/privacy-policy.html" target="_blank" rel="noopener noreferrer">隐私政策</a></span></label>
      <button class="submit" :disabled="logging" @click="login">{{ logging?'登录中...':'踏入世间' }}</button><div class="msg" :class="messageType">{{ msg }}</div><div class="foot">未注册手机号完成捏Ta官方验证码验证后，将进入捏Ta账号登录/注册流程。</div>
    </div>
    <div v-if="humanCaptchaOpen" class="captcha-mask"><section class="pseudo-captcha-card labyrinth-window"><div class="window-title">IDENTITY RITUAL</div><h2>我们需要确定你是伪人</h2><p>请从九宫格中找出不是土豆的图片。</p><div class="captcha-grid"><button v-for="cell in captchaCells" :key="cell.id" :class="{selected:captchaSelected.includes(cell.id),target:cell.type==='nieta'}" @click="toggleCaptchaCell(cell.id)"><img :src="cell.src" alt="验证图块"></button></div><p v-if="captchaError" class="captcha-error">{{ captchaError }}</p><button class="back-note primary" @click="submitHumanCaptcha">提交识别结果</button></section></div>
    <div v-if="welcomeLoading" class="welcome-loading-mask"><section class="welcome-loading-card"><span>REVERSE ARCHIVE / 1999</span><h2>{{ welcomeText }}</h2><div class="progress-track"><i></i></div><p>正在将■■切换为可读身份数据……</p></section></div>
  </section>
</template>
<script setup>
import { ref } from 'vue'
import { siteApi, TOKEN_KEY, REFRESH_KEY, SITE_SESSION_KEY, USER_CACHE_KEY } from '../lib/api.js'
import { fetchNetaProfile } from '../lib/neta.js'
const emit = defineEmits(['logged-in'])
const phone=ref(''), code=ref(''), msg=ref(''), messageType=ref(''), sending=ref(false), logging=ref(false), agree=ref(false), timer=ref(0), pendingLogin=ref(null)
const humanCaptchaOpen=ref(false), captchaCells=ref([]), captchaSelected=ref([]), captchaError=ref(''), welcomeLoading=ref(false), welcomeText=ref('■■■■■■■■■■■■')
const captchaNietaUrl='https://oss.talesofai.cn/sts/49c915e649254f55a7ea399ad3b6efd1/2ee7bcbe-7fa3-41ba-beeb-294f1f23f3b9.jpg'
const captchaPotatoUrl='https://oss.talesofai.cn/picture/db88fc7a-71fc-4b91-991d-7ec97e4ea94c.webp'
function setMsg(t,type=''){msg.value=t; messageType.value=type}
function startTimer(){timer.value=60; const h=setInterval(()=>{timer.value-=1; if(timer.value<=0)clearInterval(h)},1000)}
async function sendCode(){if(!/^1\d{10}$/.test(phone.value))return setMsg('请输入 11 位手机号','error'); if(!agree.value)return setMsg('请先同意用户协议和隐私政策','error'); sending.value=true; try{await siteApi('/api/proxy/request-code',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone_num:phone.value})}); setMsg('验证码已发送','success'); startTimer()}catch(e){setMsg(e.message,'error')}finally{sending.value=false}}
async function login(){if(!agree.value)return setMsg('请先同意用户协议和隐私政策','error'); logging.value=true; try{const data=await siteApi('/api/proxy/verify-code',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({phone_num:phone.value,code:code.value})}); if(!data.token) throw new Error('未获取 token'); localStorage.setItem(TOKEN_KEY,data.token); if(data.refresh_token)localStorage.setItem(REFRESH_KEY,data.refresh_token); const p=await fetchNetaProfile(data.token); const user={uuid:p.uuid,nick_name:p.nick_name||p.name,name:p.name,avatar_url:p.avatar_url,creator_uuid:p.uuid}; const s=await siteApi('/api/session/create',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user})}); const cached={...s.me,role:s.role,title:s.title,signature:s.signature}; localStorage.setItem(SITE_SESSION_KEY,s.session); localStorage.setItem(USER_CACHE_KEY,JSON.stringify(cached)); pendingLogin.value={...s,me:cached}; prepareHumanCaptcha()}catch(e){setMsg(e.message,'error')}finally{logging.value=false}}
function shuffleList(list){return [...list].sort(()=>Math.random()-0.5)}
function prepareHumanCaptcha(){const cells=Array.from({length:8},(_,i)=>({id:`p-${Date.now()}-${i}`,type:'potato',src:captchaPotatoUrl})); cells.push({id:`n-${Date.now()}`,type:'nieta',src:captchaNietaUrl}); captchaCells.value=shuffleList(cells); captchaSelected.value=[]; captchaError.value=''; humanCaptchaOpen.value=true}
function toggleCaptchaCell(id){captchaSelected.value=captchaSelected.value.includes(id)?captchaSelected.value.filter(x=>x!==id):[...captchaSelected.value,id]}
function submitHumanCaptcha(){const selected=captchaCells.value.filter(c=>captchaSelected.value.includes(c.id)); if(selected.length===1 && selected[0].type==='nieta'){captchaError.value='不要打地鼠捏'; setTimeout(finishHumanCaptcha,650)}else{prepareHumanCaptcha(); captchaError.value='识别结果不稳定，请再试一次。只点一个小捏，不要点土豆。'}}
function startWelcomeDecode(){const me=pendingLogin.value?.me||{}; const finalText=`欢迎你，入门伪人的${me.nick_name||me.name||'伪人'}`; welcomeText.value='■'.repeat(finalText.length); let i=0; const h=setInterval(()=>{i++; welcomeText.value=finalText.slice(0,i)+'■'.repeat(Math.max(0,finalText.length-i)); if(i>=finalText.length)clearInterval(h)},55); return finalText}
function finishHumanCaptcha(){humanCaptchaOpen.value=false; welcomeLoading.value=true; const finalText=startWelcomeDecode(); setTimeout(()=>{welcomeLoading.value=false; setMsg(finalText,'success'); emit('logged-in',pendingLogin.value)},1700)}
</script>
