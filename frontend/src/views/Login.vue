<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { request } from '@/api'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const isRegisterMode = ref(false)
const show2FA = ref(false)
const qrCode = ref('')
const verifyCode = ref('')

onMounted(() => {
  if (route.query.mode === 'register') {
    isRegisterMode.value = true
  }
})
const tempToken = ref('')
const tempUsername = ref('')
const tempPassword = ref('')

const loginForm = ref({
  username: '',
  password: ''
})

const registerForm = ref({
  username: '',
  password: '',
  full_name: '',
  email: '',
  enable_2fa: false,
  role: 'guest'
})

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning('Please enter username and password')
    return
  }

  loading.value = true
  try {
    const res = await request.post('/auth/login', 
      new URLSearchParams({
        username: loginForm.value.username,
        password: loginForm.value.password
      }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
    
    if (res.requires_2fa) {
      tempToken.value = res.access_token
      show2FA.value = true
    } else {
      localStorage.setItem('token', res.access_token)
      if (res.user_info) {
        userStore.userInfo = res.user_info
        localStorage.setItem('userInfo', JSON.stringify(res.user_info))
      } else {
        const payload = JSON.parse(atob(res.access_token.split('.')[1]))
        userStore.userInfo = { username: payload.sub, role: 'guest' }
        localStorage.setItem('userInfo', JSON.stringify(userStore.userInfo))
      }
      ElMessage.success('Login successful')
      router.push('/')
    }
  } catch (error: any) {
    ElMessage.error('Invalid credentials')
  } finally {
    loading.value = false
  }
}

const handleVerify2FA = async () => {
  if (!verifyCode.value) {
    ElMessage.warning('Please enter verification code')
    return
  }

  loading.value = true
  try {
    const res = await request.post('/auth/login-with-2fa', {
      username: loginForm.value.username,
      password: loginForm.value.password,
      code: verifyCode.value
    })
    
    localStorage.setItem('token', res.access_token)
    if (res.user_info) {
      userStore.userInfo = res.user_info
      localStorage.setItem('userInfo', JSON.stringify(res.user_info))
    } else {
      const payload = JSON.parse(atob(res.access_token.split('.')[1]))
      userStore.userInfo = { username: payload.sub, roles: ['guest'] }
      localStorage.setItem('userInfo', JSON.stringify(userStore.userInfo))
    }
    ElMessage.success('Login successful')
    
    // Redirect based on role
    const roles = userStore.userInfo?.roles || [userStore.userInfo?.role || 'guest']
    const role = roles[0]
    if (role === 'admin' || role === 'manager') {
      router.push('/home')
    } else if (['staff', 'cleaner', 'employee'].includes(role)) {
      router.push('/cleaner-tasks')
    } else if (role === 'guest') {
      router.push('/my-requirements')
    } else {
      router.push('/')
    }
  } catch (error: any) {
    ElMessage.error('Invalid credentials')
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.password) {
    ElMessage.warning('Please enter username and password')
    return
  }

  loading.value = true
  try {
    const res = await request.post('/auth/register', registerForm.value)
    
    if (res.requires_2fa) {
      qrCode.value = res.qr_code
      tempUsername.value = registerForm.value.username
      tempPassword.value = registerForm.value.password
      show2FA.value = true
    } else {
      ElMessage.success('Registration successful')
      localStorage.setItem('token', res.temp_token)
      router.push('/')
    }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || 'Registration failed')
  } finally {
    loading.value = false
  }
}

const handleVerifyRegister = async () => {
  if (!verifyCode.value) {
    ElMessage.warning('Please enter verification code')
    return
  }

  loading.value = true
  try {
    const res = await request.post('/auth/verify-2fa', null, {
      params: {
        username: tempUsername.value,
        code: verifyCode.value,
        role: registerForm.value.role || 'guest'
      }
    })
    
    // After successful 2FA verification, use the token directly
    ElMessage.success('Registration successful!')
    
    localStorage.setItem('token', res.access_token)
    if (res.user_info) {
      userStore.userInfo = res.user_info
      localStorage.setItem('userInfo', JSON.stringify(res.user_info))
    } else {
      const payload = JSON.parse(atob(res.access_token.split('.')[1]))
      userStore.userInfo = { username: payload.sub, roles: [registerForm.value.role || 'guest'] }
      localStorage.setItem('userInfo', JSON.stringify(userStore.userInfo))
    }
    
    // Reset all state
    show2FA.value = false
    isRegisterMode.value = false
    verifyCode.value = ''
    tempUsername.value = ''
    tempPassword.value = ''
    
    // Redirect based on role
    const roles = userStore.userInfo?.roles || [userStore.userInfo?.role || 'guest']
    const role = roles[0]
    if (role === 'admin' || role === 'manager') {
      router.push('/home')
    } else if (['staff', 'cleaner', 'employee'].includes(role)) {
      router.push('/cleaner-tasks')
    } else if (role === 'guest') {
      router.push('/my-requirements')
    } else {
      router.push('/')
    }
  } catch (error: any) {
    ElMessage.error('Invalid credentials')
  } finally {
    loading.value = false
  }
}

const toggleMode = () => {
  isRegisterMode.value = !isRegisterMode.value
  show2FA.value = false
  verifyCode.value = ''
  qrCode.value = ''
  tempUsername.value = ''
  tempPassword.value = ''
  loginForm.value.username = ''
  loginForm.value.password = ''
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <el-icon class="logo-icon"><House /></el-icon>
        <h1>Housekeeping System</h1>
        <p>{{ isRegisterMode ? 'Create Account' : 'Management Portal' }}</p>
      </div>

      <!-- 2FA Verification -->
      <div v-if="show2FA" class="verify-2fa">
        <div class="qr-code-container" v-if="qrCode">
          <p>Scan QR Code with Authenticator App</p>
          <img :src="qrCode" alt="QR Code" class="qr-code" />
          <p class="hint">Then enter the code below</p>
        </div>
        <p v-else>Enter verification code from your authenticator app</p>
        
        <el-input
          v-model="verifyCode"
          placeholder="Verification Code"
          size="large"
          class="verify-input"
          @keyup.enter="qrCode ? handleVerifyRegister() : handleVerify2FA()"
        />
        
        <el-button
          type="primary"
          size="large"
          :loading="loading"
          class="login-button"
          @click="qrCode ? handleVerifyRegister() : handleVerify2FA()"
        >
          Verify
        </el-button>
        
        <div class="toggle-mode">
          <el-button link @click="toggleMode">Back to {{ isRegisterMode ? 'Login' : 'Register' }}</el-button>
        </div>
      </div>

      <!-- Login Form -->
      <el-form v-else-if="!isRegisterMode" :model="loginForm" class="login-form" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input
            v-model="loginForm.username"
            placeholder="Username"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="Password"
            prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            Login
          </el-button>
        </el-form-item>
        
        <div class="toggle-mode">
          <span>Don't have an account? </span>
          <el-button link type="primary" @click="toggleMode">Register</el-button>
        </div>
      </el-form>

      <!-- Register Form -->
      <el-form v-else :model="registerForm" class="login-form" @submit.prevent="handleRegister">
        <el-form-item>
          <el-input
            v-model="registerForm.username"
            placeholder="Username"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="Password"
            prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="registerForm.full_name"
            placeholder="Full Name"
            prefix-icon="UserFilled"
            size="large"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="registerForm.email"
            placeholder="Email"
            prefix-icon="Message"
            size="large"
          />
        </el-form-item>
        <el-form-item>
          <el-select v-model="registerForm.role" placeholder="Select Role" size="large" style="width: 100%">
            <el-option label="Customer (Guest)" value="guest" />
            <el-option label="Cleaner" value="cleaner" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="registerForm.enable_2fa">Enable Two-Factor Authentication</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button"
            @click="handleRegister"
          >
            Register
          </el-button>
        </el-form-item>
        
        <div class="toggle-mode">
          <span>Already have an account? </span>
          <el-button link type="primary" @click="toggleMode">Login</el-button>
        </div>
      </el-form>

      <div class="login-footer">
        <span>Default: admin / admin123</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 50%, #3d7ab5 100%);
  position: relative;
  overflow: hidden;
}

.login-page::before {
  content: '';
  position: absolute;
  width: 600px;
  height: 600px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 50%;
  top: -200px;
  right: -200px;
}

.login-page::after {
  content: '';
  position: absolute;
  width: 400px;
  height: 400px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 50%;
  bottom: -100px;
  left: -100px;
}

.login-card {
  width: 420px;
  padding: 40px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  position: relative;
  z-index: 1;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 16px;
}

.login-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.login-header p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.login-form {
  margin-top: 20px;
}

.login-form :deep(.el-input__wrapper) {
  padding: 4px 12px;
  border-radius: 8px;
}

.login-form :deep(.el-input__wrapper):hover {
  box-shadow: 0 0 0 1px #409eff inset;
}

.login-button {
  width: 100%;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
  background: linear-gradient(135deg, #409eff 0%, #337ecc 100%);
  border: none;
  transition: all 0.3s;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(64, 158, 255, 0.4);
}

.toggle-mode {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: #606266;
}

.login-footer {
  text-align: center;
  margin-top: 24px;
  font-size: 13px;
  color: #909399;
}

.verify-2fa {
  text-align: center;
}

.verify-2fa p {
  color: #606266;
  margin-bottom: 20px;
}

.qr-code-container {
  margin-bottom: 20px;
}

.qr-code {
  width: 200px;
  height: 200px;
  border-radius: 8px;
  margin: 10px 0;
}

.hint {
  font-size: 12px;
  color: #909399;
}

.verify-input {
  margin-bottom: 20px;
}
</style>
