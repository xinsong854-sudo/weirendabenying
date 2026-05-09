import { createApp, computed, onMounted, ref } from 'vue'
import App from './App.vue'
import './style.css'

if (import.meta.env.PROD) {
  const block = (event) => {
    event.preventDefault()
    event.stopPropagation()
    return false
  }
  window.addEventListener('contextmenu', block, { capture: true })
  window.addEventListener('keydown', (event) => {
    const key = String(event.key).toLowerCase()
    if (
      key === 'f12' ||
      (event.ctrlKey && event.shiftKey && ['i', 'j', 'c'].includes(key)) ||
      (event.metaKey && event.altKey && ['i', 'j', 'c'].includes(key)) ||
      (event.ctrlKey && key === 'u')
    ) block(event)
  }, { capture: true })
}

createApp(App).mount('#app')

export { computed, onMounted, ref }
