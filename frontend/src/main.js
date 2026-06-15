import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

const applyThemeSettings = () => {
  const savedTheme = localStorage.getItem('theme_settings')
  if (savedTheme) {
    const theme = JSON.parse(savedTheme)
    const root = document.documentElement
    
    root.style.setProperty('--el-color-primary', theme.primaryColor)
    root.style.setProperty('--el-color-primary-light-3', theme.primaryColor + '40')
    root.style.setProperty('--el-color-primary-light-5', theme.primaryColor + '80')
    root.style.setProperty('--el-color-primary-light-7', theme.primaryColor + 'A0')
    root.style.setProperty('--el-color-primary-light-8', theme.primaryColor + 'C0')
    root.style.setProperty('--el-color-primary-light-9', theme.primaryColor + 'E0')
    root.style.setProperty('--el-color-primary-dark-2', theme.primaryColor + '20')
    
    if (theme.darkMode) {
      root.classList.add('dark')
      root.style.setProperty('--bg-color', '#1a1a1a')
      root.style.setProperty('--bg-color-page', '#121212')
      root.style.setProperty('--bg-color-overlay', '#1d1d1d')
      root.style.setProperty('--text-color-primary', '#ffffff')
      root.style.setProperty('--text-color-regular', '#e5e5e5')
      root.style.setProperty('--border-color', '#333333')
      root.style.setProperty('--border-color-light', '#444444')
      root.style.setProperty('--sidebar-bg', '#1e293b')
      root.style.setProperty('--sidebar-text', '#ffffff')
      root.style.setProperty('--sidebar-text-secondary', '#94a3b8')
    } else {
      root.classList.remove('dark')
      root.style.setProperty('--bg-color', '#f5f7fa')
      root.style.setProperty('--bg-color-page', '#ffffff')
      root.style.setProperty('--bg-color-overlay', '#ffffff')
      root.style.setProperty('--text-color-primary', '#303133')
      root.style.setProperty('--text-color-regular', '#606266')
      root.style.setProperty('--border-color', '#dcdfe6')
      root.style.setProperty('--border-color-light', '#e4e7ed')
      root.style.setProperty('--sidebar-bg', '#1e293b')
      root.style.setProperty('--sidebar-text', '#ffffff')
      root.style.setProperty('--sidebar-text-secondary', '#94a3b8')
    }
  }
}

applyThemeSettings()

app.use(pinia)
app.use(router)
app.use(ElementPlus)

app.mount('#app')
