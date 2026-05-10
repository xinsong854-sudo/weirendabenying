<template>
  <main class="login-stage">
    <header class="login-brand">
      <h1 class="login-brand-name">伪人大本营</h1>
      <p class="login-brand-sub">Artificial Human Base Camp</p>
    </header>
    <section class="login-panel">
      <div class="field"><span class="prefix">+86</span><input v-model.trim="phone" type="tel" inputmode="numeric" maxlength="11" placeholder="请输入手机号" autocomplete="tel"></div>
      <div class="field"><input v-model.trim="code" type="text" inputmode="numeric" maxlength="6" placeholder="请输入验证码" autocomplete="one-time-code"><button class="code-btn" :disabled="sending || timer>0" @click="sendCode">{{ timer>0?`${timer}s`:'获取验证码' }}</button></div>
      <label class="agree"><input v-model="agree" type="checkbox"><span>我已阅读并同意 <a href="https://oss.talesofai.cn/static/blackboard/protocol-page/user-agreement.html" target="_blank">用户协议</a> 和 <a href="https://oss.talesofai.cn/static/blackboard/protocol-page/privacy-policy.html" target="_blank">隐私政策</a></span></label>
      <button class="login-btn" :disabled="logging" @click="login">{{ logging?'登录中...':'踏入世间' }}</button>
      <div v-if="msg" class="msg" :class="messageType">{{ msg }}</div>
    </section>
    <p class="login-foot">未注册手机号验证后将自动登录</p>
    <div v-if="humanCaptchaOpen" class="captcha-mask" @click.self="humanCaptchaOpen=false"><section class="captcha-card"><h2>确定你是伪人</h2><p>找出不是土豆的图片</p><div class="captcha-grid"><button v-for="cell in captchaCells" :key="cell.id" :class="{selected:captchaSelected.includes(cell.id)}" @click="toggleCaptchaCell(cell.id)"><img :src="cell.src" alt="验证图块"></button></div><p v-if="captchaError" class="captcha-error">{{ captchaError }}</p><button class="login-btn" style="margin-top:14px" @click="submitHumanCaptcha">提交识别结果</button></section></div>
    <div v-if="welcomeLoading" class="captcha-mask"><section class="captcha-card loading"><span class="login-brand-sub">Artificial Human Base Camp</span><h2>{{ welcomeText }}</h2><div class="progress-track"><i></i></div></section></div>
  </main>
</template>
<script setup>
import { ref } from 'vue'
import { TOKEN_KEY, REFRESH_KEY, SITE_SESSION_KEY, USER_CACHE_KEY, siteApi } from '../lib/api.js'
import { fetchNetaProfile } from '../lib/neta.js'
const emit = defineEmits(['logged-in'])
const phone=ref(''), code=ref(''), msg=ref(''), messageType=ref(''), sending=ref(false), logging=ref(false), agree=ref(false), timer=ref(0), pendingLogin=ref(null)
const humanCaptchaOpen=ref(false), captchaCells=ref([]), captchaSelected=ref([]), captchaError=ref(''), welcomeLoading=ref(false), welcomeText=ref('')
const NETA_API = 'https://api.talesofai.cn'
const captchaNietaUrl='https://oss.talesofai.cn/sts/49c915e649254f55a7ea399ad3b6efd1/2ee7bcbe-7fa3-41ba-beeb-294f1f23f3b9.jpg'
const captchaPotatoUrl='https://oss.talesofai.cn/picture/db88fc7a-71fc-4b91-991d-7ec97e4ea94c.webp'

function setMsg(t,type=''){msg.value=t; messageType.value=type}
function startTimer(){timer.value=60; const h=setInterval(()=>{timer.value-=1; if(timer.value<=0)clearInterval(h)},1000)}

async function netaPost(path, body) {
  const res = await fetch(NETA_API + path, {method:'POST',mode:'cors',credentials:'include',headers:{'content-type':'application/json'},body:JSON.stringify(body)})
  const text = await res.text()
  let data = null; try{data=text?JSON.parse(text):null}catch{data=text}
  if(!res.ok) throw new Error((data&&typeof data==='object'?(data.message||data.msg||data.error):null)||data||res.statusText)
  return data
}

async function sendCode(){
  if(!/^1[3456789]\d{9}$/.test(phone.value)) return setMsg('请输入正确的手机号','error')
  if(!agree.value) return setMsg('请先同意用户协议和隐私政策','error')
  sending.value=true
  try{
    await netaPost('/v1/user/request-verification-code',{phone_num:phone.value})
    setMsg('验证码已发送','success'); startTimer()
  }catch(e){setMsg(e.message,'error')}
  finally{sending.value=false}
}

async function login(){
  if(!agree.value) return setMsg('请先同意用户协议和隐私政策','error')
  if(!/^\d{4,6}$/.test(code.value)) return setMsg('请输入验证码','error')
  logging.value=true
  try{
    const data = await netaPost('/v1/user/verify-with-phone-num',{phone_num:phone.value,code:code.value})
    if(!data.token) throw new Error('未获取 token')
    localStorage.setItem(TOKEN_KEY,data.token)
    if(data.refresh_token) localStorage.setItem(REFRESH_KEY,data.refresh_token)
    const p = await fetchNetaProfile(data.token)
    const user = {uuid:p.uuid,nick_name:p.nick_name||p.name,name:p.name,avatar_url:p.avatar_url,creator_uuid:p.uuid}
    const s = await siteApi('/api/session/create',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user})})
    const cached = {...s.me,role:s.role,title:s.title,signature:s.signature}
    localStorage.setItem(SITE_SESSION_KEY,s.session)
    localStorage.setItem(USER_CACHE_KEY,JSON.stringify(cached))
    pendingLogin.value = {...s,me:cached}
    prepareHumanCaptcha()
  }catch(e){setMsg(e.message,'error')}
  finally{logging.value=false}
}

function shuffleList(list){return [...list].sort(()=>Math.random()-0.5)}
function prepareHumanCaptcha(){const cells=Array.from({length:8},(_,i)=>({id:`p-${Date.now()}-${i}`,type:'potato',src:captchaPotatoUrl})); cells.push({id:`n-${Date.now()}`,type:'nieta',src:captchaNietaUrl}); captchaCells.value=shuffleList(cells); captchaSelected.value=[]; captchaError.value=''; humanCaptchaOpen.value=true}
function toggleCaptchaCell(id){captchaSelected.value=captchaSelected.value.includes(id)?captchaSelected.value.filter(x=>x!==id):[...captchaSelected.value,id]}
function submitHumanCaptcha(){const selected=captchaCells.value.filter(c=>captchaSelected.value.includes(c.id)); if(selected.length===1&&selected[0].type==='nieta'){captchaError.value='';setTimeout(finishHumanCaptcha,650)}else{prepareHumanCaptcha();captchaError.value='再试一次，只点小捏'}}
function startWelcomeDecode(){const me=pendingLogin.value?.me||{};const finalText=`欢迎你，${me.nick_name||me.name||'伪人'}`;welcomeText.value='■'.repeat(finalText.length);let i=0;const h=setInterval(()=>{i++;welcomeText.value=finalText.slice(0,i)+'■'.repeat(Math.max(0,finalText.length-i));if(i>=finalText.length)clearInterval(h)},55)}
function finishHumanCaptcha(){humanCaptchaOpen.value=false;welcomeLoading.value=true;startWelcomeDecode();setTimeout(()=>{welcomeLoading.value=false;emit('logged-in',pendingLogin.value)},1700)}
</script>
