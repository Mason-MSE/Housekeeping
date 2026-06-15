import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000
})

request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        const url = error.config?.url || ''
        const isAuthCredentialAttempt =
          url.includes('/auth/login') ||
          url.includes('/auth/login-with-2fa') ||
          url.includes('/auth/verify-2fa')
        if (isAuthCredentialAttempt) {
          return Promise.reject(error)
        }
        ElMessage.error('Login expired, please login again')
        localStorage.removeItem('token')
        router.push('/login')
      } else if (status === 403) {
        ElMessage.error(data?.detail || 'No permission')
      } else if (status === 404) {
        ElMessage.error('Resource not found')
      } else if (status >= 500) {
        ElMessage.error('Server error, please try again later')
      } else {
        ElMessage.error(data?.detail || 'Request failed')
      }
    } else {
      ElMessage.error('Network error, please check your connection')
    }
    return Promise.reject(error)
  }
)

export default request
