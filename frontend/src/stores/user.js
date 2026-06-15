import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, userApi } from '@/api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  
  const userRole = computed(() => {
    if (!userInfo.value) return 'guest'
    if (userInfo.value.roles && userInfo.value.roles.length > 0) {
      return userInfo.value.roles[0]
    }
    return userInfo.value.role || 'guest'
  })

  async function login(username, password) {
    const formData = new URLSearchParams()
    formData.append('grant_type', 'password')
    formData.append('username', username)
    formData.append('password', password)

    const res = await authApi.login(formData)
    
    if (res.requires_2fa) {
      return res
    }
    
    token.value = res.access_token
    localStorage.setItem('token', res.access_token)
    
    try {
      const users = await userApi.list()
      const currentUser = users.find(u => u.username === username)
      if (currentUser) {
        userInfo.value = { 
          id: currentUser.id,
          username: currentUser.username, 
          roles: currentUser.roles || [],
          phone: currentUser.phone || ''
        }
      } else {
        const payload = JSON.parse(atob(res.access_token.split('.')[1]))
        userInfo.value = { username: payload.sub, roles: ['guest'], phone: '' }
      }
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    } catch (e) {
      console.error('Failed to fetch user info:', e)
      const payload = JSON.parse(atob(res.access_token.split('.')[1]))
      userInfo.value = { username: payload.sub, roles: ['guest'], phone: '' }
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    }
    
    return res
  }

  async function getUserInfo() {
    try {
      const users = await userApi.list()
      const storedToken = localStorage.getItem('token')
      if (!storedToken) return
      
      const payload = JSON.parse(atob(storedToken.split('.')[1]))
      const username = payload.sub
      
      const currentUser = users.find(u => u.username === username)
      if (currentUser) {
        userInfo.value = { 
          id: currentUser.id,
          username: currentUser.username, 
          roles: currentUser.roles || [],
          phone: currentUser.phone || ''
        }
      } else {
        userInfo.value = { username: username, roles: ['guest'], phone: '' }
      }
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    } catch (e) {
      console.error('Failed to fetch user info:', e)
    }
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  return {
    token,
    userInfo,
    userRole,
    isLoggedIn,
    login,
    getUserInfo,
    logout
  }
})
