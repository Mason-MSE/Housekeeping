<script lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { userApi } from '@/api'
import { request } from '@/api'

export default {
  name: 'Settings',
  setup() {
    // User store instance
    const userStore = useUserStore()
    // Loading state for operations
    const loading = ref(false)
    
    // Current active tab name
    const activeTab = ref('profile')
    
    // Profile edit form model
    const profileForm = ref({
      full_name: '',
      email: '',
      phone: ''
    })
    
    // Password change form model
    const passwordForm = ref({
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    // 2FA enabled status
    const twoFactorEnabled = ref(false)
    // Dialog visibility for 2FA QR code
    const showTwoFactorDialog = ref(false)
    // 2FA QR code image data
    const twoFactorQrCode = ref('')
    // 2FA verification code input
    const twoFactorCode = ref('')
    // Loading state for 2FA operations
    const twoFactorLoading = ref(false)
    
    // Theme settings (primary color, dark mode)
    const themeSettings = ref({
      primaryColor: '#409eff',
      darkMode: false
    })
    
    // Layout settings (sidebar, tags view, header)
    const layoutSettings = ref({
      sidebarCollapsed: false,
      showTagsView: true,
      fixedHeader: true
    })
    
    const colorOptions = [
      { value: '#409eff', label: 'Default Blue', color: '#409eff' },
      { value: '#67c23a', label: 'Success Green', color: '#67c23a' },
      { value: '#e6a23c', label: 'Warning Orange', color: '#e6a23c' },
      { value: '#f56c6c', label: 'Danger Red', color: '#f56c6c' },
      { value: '#909399', label: 'Info Gray', color: '#909399' },
      { value: '#9013fe', label: 'Purple', color: '#9013fe' },
      { value: '#ffc0cb', label: 'Pink', color: '#ffc0cb' },
      { value: '#000000', label: 'Black', color: '#000000' }
    ]
    
    // Load theme and layout settings from localStorage
    const loadSettings = () => {
      const savedTheme = localStorage.getItem('theme_settings')
      if (savedTheme) {
        themeSettings.value = JSON.parse(savedTheme)
        applyTheme(themeSettings.value)
      }
      
      const savedLayout = localStorage.getItem('layout_settings')
      if (savedLayout) {
        layoutSettings.value = JSON.parse(savedLayout)
        applyLayout(layoutSettings.value)
      }
    }
    
    // Load the current 2FA status from the API
    const loadTwoFactorStatus = async () => {
      try {
        const res = await request.get('/user/me/2fa-status')
        twoFactorEnabled.value = res.is_2fa_enabled
      } catch (error) {
        console.error('Failed to load 2FA status:', error)
      }
    }
    
    // Apply theme settings to CSS custom properties
    const applyTheme = (theme: any) => {
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
    
    // Apply layout settings (sidebar collapse)
    const applyLayout = (layout: any) => {
      const sidebar = document.querySelector('.sidebar')
      if (sidebar) {
        sidebar.classList.toggle('collapsed', layout.sidebarCollapsed)
      }
    }
    
    // Save and apply theme settings
    const handleThemeChange = () => {
      localStorage.setItem('theme_settings', JSON.stringify(themeSettings.value))
      applyTheme(themeSettings.value)
      ElMessage.success('Theme settings saved')
    }
    
    // Save and apply layout settings, then reload
    const handleLayoutChange = () => {
      localStorage.setItem('layout_settings', JSON.stringify(layoutSettings.value))
      applyLayout(layoutSettings.value)
      window.location.reload()
    }
    
    // Save profile information to the API
    const handleProfileSave = async () => {
      loading.value = true
      try {
        await userApi.update(userStore.userInfo?.id, profileForm.value)
        userStore.userInfo = { ...userStore.userInfo, ...profileForm.value }
        localStorage.setItem('user_info', JSON.stringify(userStore.userInfo))
        ElMessage.success('Profile updated successfully')
      } catch (error: any) {
        ElMessage.error(error?.response?.data?.detail || 'Failed to update profile')
      } finally {
        loading.value = false
      }
    }
    
    // Change the user's password
    const handlePasswordChange = async () => {
      if (!passwordForm.value.oldPassword || !passwordForm.value.newPassword) {
        ElMessage.warning('Please fill in all password fields')
        return
      }
      if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
        ElMessage.warning('New passwords do not match')
        return
      }
      loading.value = true
      try {
        await userApi.changePassword({
          old_password: passwordForm.value.oldPassword,
          new_password: passwordForm.value.newPassword
        })
        ElMessage.success('Password changed successfully')
        passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
      } catch (error: any) {
        ElMessage.error(error?.response?.data?.detail || 'Failed to change password')
      } finally {
        loading.value = false
      }
    }
    
    // Enable 2FA and generate QR code
    const handleEnableTwoFactor = async () => {
      twoFactorLoading.value = true
      try {
        const res = await request.post('/user/me/enable-2fa')
        twoFactorQrCode.value = res.qr_code
        showTwoFactorDialog.value = true
      } catch (error: any) {
        ElMessage.error(error?.response?.data?.detail || 'Failed to generate QR code')
      } finally {
        twoFactorLoading.value = false
      }
    }
    
    // Verify 2FA code to complete enablement
    const handleVerifyTwoFactor = async () => {
      if (!twoFactorCode.value) {
        ElMessage.warning('Please enter verification code')
        return
      }
      
      twoFactorLoading.value = true
      try {
        await request.post('/user/me/verify-2fa', null, {
          params: { code: twoFactorCode.value }
        })
        ElMessage.success('2FA enabled successfully')
        twoFactorEnabled.value = true
        showTwoFactorDialog.value = false
        twoFactorCode.value = ''
        twoFactorQrCode.value = ''
      } catch (error: any) {
        ElMessage.error(error?.response?.data?.detail || 'Invalid verification code')
      } finally {
        twoFactorLoading.value = false
      }
    }
    
    // Disable 2FA after confirmation
    const handleDisableTwoFactor = async () => {
      try {
        await ElMessageBox.confirm(
          'Are you sure you want to disable 2FA? This will make your account less secure.',
          'Disable 2FA',
          {
            confirmButtonText: 'Disable',
            cancelButtonText: 'Cancel',
            type: 'warning'
          }
        )
        
        loading.value = true
        await request.post('/user/me/disable-2fa')
        ElMessage.success('2FA disabled successfully')
        twoFactorEnabled.value = false
      } catch (error: any) {
        if (error !== 'cancel') {
          ElMessage.error(error?.response?.data?.detail || 'Failed to disable 2FA')
        }
      } finally {
        loading.value = false
      }
    }
    
    // Clear all localStorage and sessionStorage data
    const handleClearCache = () => {
      localStorage.clear()
      sessionStorage.clear()
      ElMessage.success('Cache cleared successfully')
    }
    
    // Reset all settings to their default values
    const handleResetSettings = () => {
      localStorage.removeItem('theme_settings')
      localStorage.removeItem('layout_settings')
      themeSettings.value = {
        primaryColor: '#409eff',
        darkMode: false
      }
      layoutSettings.value = {
        sidebarCollapsed: false,
        showTagsView: true,
        fixedHeader: true
      }
      applyTheme(themeSettings.value)
      ElMessage.success('Settings reset to defaults')
      window.location.reload()
    }
    
    // Lifecycle hook: populate profile form and load settings on mount
    onMounted(() => {
      if (userStore.userInfo) {
        profileForm.value = {
          full_name: userStore.userInfo.full_name || '',
          email: userStore.userInfo.email || '',
          phone: userStore.userInfo.phone || ''
        }
      }
      loadSettings()
      loadTwoFactorStatus()
    })
    
    return {
      activeTab,
      loading,
      profileForm,
      passwordForm,
      themeSettings,
      layoutSettings,
      colorOptions,
      twoFactorEnabled,
      showTwoFactorDialog,
      twoFactorQrCode,
      twoFactorCode,
      twoFactorLoading,
      handleThemeChange,
      handleLayoutChange,
      handleProfileSave,
      handlePasswordChange,
      handleEnableTwoFactor,
      handleVerifyTwoFactor,
      handleDisableTwoFactor,
      handleClearCache,
      handleResetSettings
    }
  }
}
</script>

<template>
  <div class="settings-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Settings</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" tab-position="left">
        <el-tab-pane label="Profile" name="profile">
          <div class="tab-content">
            <h3>Profile Settings</h3>
            <el-form :model="profileForm" label-width="100px" class="profile-form">
              <el-form-item label="Username">
                <el-input v-model="profileForm.full_name" placeholder="Your name" />
              </el-form-item>
              <el-form-item label="Email">
                <el-input v-model="profileForm.email" placeholder="your@email.com" />
              </el-form-item>
              <el-form-item label="Phone">
                <el-input v-model="profileForm.phone" placeholder="Phone number" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleProfileSave" :loading="loading">
                  Save Changes
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="Theme" name="theme">
          <div class="tab-content">
            <h3>Theme Settings</h3>
            <el-form label-width="120px">
              <el-form-item label="Primary Color">
                <div class="color-options">
                  <div
                    v-for="option in colorOptions"
                    :key="option.value"
                    class="color-option"
                    :class="{ active: themeSettings.primaryColor === option.value }"
                    :style="{ backgroundColor: option.color }"
                    @click="themeSettings.primaryColor = option.value"
                    :title="option.label"
                  >
                    <el-icon v-if="themeSettings.primaryColor === option.value" class="check-icon">
                      <Check />
                    </el-icon>
                  </div>
                </div>
              </el-form-item>
              <el-form-item label="Dark Mode">
                <el-switch v-model="themeSettings.darkMode" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleThemeChange">
                  Apply Theme
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="Layout" name="layout">
          <div class="tab-content">
            <h3>Layout Settings</h3>
            <el-form label-width="140px">
              <el-form-item label="Collapse Sidebar">
                <el-switch v-model="layoutSettings.sidebarCollapsed" />
              </el-form-item>
              <el-form-item label="Show Tags View">
                <el-switch v-model="layoutSettings.showTagsView" />
              </el-form-item>
              <el-form-item label="Fixed Header">
                <el-switch v-model="layoutSettings.fixedHeader" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handleLayoutChange">
                  Apply Layout
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="Security" name="security">
          <div class="tab-content">
            <h3>Security Settings</h3>
            
            <div class="security-section">
              <h4>Two-Factor Authentication (2FA)</h4>
              <p class="security-desc">
                Add an extra layer of security to your account by requiring a verification code from your authenticator app in addition to your password.
              </p>
              
              <div class="two-factor-status">
                <el-tag :type="twoFactorEnabled ? 'success' : 'info'" size="large">
                  {{ twoFactorEnabled ? 'Enabled' : 'Disabled' }}
                </el-tag>
                
                <el-button 
                  v-if="!twoFactorEnabled" 
                  type="primary" 
                  @click="handleEnableTwoFactor"
                  :loading="twoFactorLoading"
                >
                  Enable 2FA
                </el-button>
                
                <el-button 
                  v-else 
                  type="danger" 
                  @click="handleDisableTwoFactor"
                  :loading="loading"
                >
                  Disable 2FA
                </el-button>
              </div>
            </div>
            
            <el-divider />
            
            <h4>Change Password</h4>
            <el-form label-width="120px" class="password-form">
              <el-form-item label="Current Password">
                <el-input v-model="passwordForm.oldPassword" type="password" placeholder="Enter current password" show-password />
              </el-form-item>
              <el-form-item label="New Password">
                <el-input v-model="passwordForm.newPassword" type="password" placeholder="Enter new password" show-password />
              </el-form-item>
              <el-form-item label="Confirm Password">
                <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="Confirm new password" show-password />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="handlePasswordChange">
                  Change Password
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
        
        <el-tab-pane label="System" name="system">
          <div class="tab-content">
            <h3>System Settings</h3>
            <el-form label-width="120px">
              <el-form-item label="Clear Cache">
                <el-button @click="handleClearCache">
                  Clear Cache
                </el-button>
              </el-form-item>
              <el-form-item label="Reset Settings">
                <el-button type="warning" @click="handleResetSettings">
                  Reset to Defaults
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <!-- 2FA QR Code Dialog -->
    <el-dialog 
      v-model="showTwoFactorDialog" 
      title="Enable Two-Factor Authentication" 
      width="400px"
      :close-on-click-modal="false"
    >
      <div class="qr-dialog-content">
        <p>Scan this QR code with your Google Authenticator app:</p>
        <img :src="twoFactorQrCode" alt="QR Code" class="qr-image" />
        <p class="hint">After scanning, enter the 6-digit code from your app:</p>
        <el-input 
          v-model="twoFactorCode" 
          placeholder="Verification Code" 
          maxlength="6"
          @keyup.enter="handleVerifyTwoFactor"
        />
      </div>
      <template #footer>
        <el-button @click="showTwoFactorDialog = false">Cancel</el-button>
        <el-button 
          type="primary" 
          @click="handleVerifyTwoFactor"
          :loading="twoFactorLoading"
        >
          Verify & Enable
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.settings-page {
  padding: 20px;
}
.card-header {
  font-size: 18px;
  font-weight: 600;
}
.tab-content {
  padding: 20px;
  max-width: 600px;
}
.tab-content h3 {
  margin-bottom: 20px;
  color: #303133;
}
.tab-content h4 {
  margin-bottom: 12px;
  color: #606266;
}
.profile-form {
  max-width: 400px;
}
.password-form {
  max-width: 400px;
  margin-top: 20px;
}
.color-options {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.color-option {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 2px solid transparent;
}
.color-option:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
.color-option.active {
  border-color: #fff;
  box-shadow: 0 0 0 2px var(--el-color-primary);
}
.check-icon {
  color: #fff;
  font-weight: bold;
}
.security-section {
  margin-bottom: 24px;
}
.security-desc {
  color: #909399;
  font-size: 14px;
  margin-bottom: 16px;
  line-height: 1.6;
}
.two-factor-status {
  display: flex;
  align-items: center;
  gap: 16px;
}
.qr-dialog-content {
  text-align: center;
}
.qr-dialog-content p {
  margin-bottom: 16px;
  color: #606266;
}
.qr-dialog-content .hint {
  margin-top: 16px;
  margin-bottom: 12px;
}
.qr-image {
  width: 200px;
  height: 200px;
  margin: 16px 0;
}
</style>
