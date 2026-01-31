import '@/styles/tailwind.css'
import '@/styles/design-system.css'
import '@/styles/gov-components.css'
import '@/styles/military-theme.scss'
import '@/styles/matechat-theme.scss'
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import MateChat from '@matechat/core'
import '@devui-design/icons/icomoon/devui-icon.css'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
// 配置 Element Plus 使用中文语言包
app.use(ElementPlus, {
  locale: zhCn
})
// 使用 MateChat
app.use(MateChat)

app.mount('#app')

