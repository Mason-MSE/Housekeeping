<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox, ElAvatar, ElDropdown, ElBadge } from 'element-plus'
import { walletApi, serviceOrderApi, notificationApi, permissionApi } from '@/api'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

// Whether the sidebar is collapsed
const isCollapse = ref(false)
// Current wallet balance information
const walletInfo = ref({ balance: 0 })
// Unread notification count
const notificationCount = ref(0)
// List of notifications for the dropdown
const notificationList = ref([])
// Whether the notification dropdown is visible
const notificationDropdownVisible = ref(false)
// Dynamic menu items loaded from the server
const dynamicMenus = ref<any[]>([])
// Permission codes for the current user
const userPermissions = ref<string[]>([])

// Checks whether the current theme is dark mode
const isDarkMode = computed(() => {
  return document.documentElement.classList.contains('dark')
})

// Fetches dynamic menu items from the server based on user permissions
const loadDynamicMenus = async () => {
  try {
    const res = await permissionApi.getMyMenus()
    dynamicMenus.value = Array.isArray(res) ? res : (res?.data || [])
  } catch (e) {
    console.error('Failed to load menus:', e)
    dynamicMenus.value = []
  }
}

// Loads the current user's permission codes from the server
const loadUserPermissions = async () => {
  try {
    const res = await permissionApi.getMyPermissions()
    userPermissions.value = (res || []).map((p: any) => p.permission_code)
  } catch (e) {
    console.error('Failed to load permissions:', e)
    userPermissions.value = []
  }
}

// Checks whether the user has a specific permission code
const hasPermission = (permissionCode: string): boolean => {
  return userPermissions.value.includes(permissionCode)
}

// Computes the sidebar menu items from dynamic menus or defaults based on permissions
const menuItems = computed(() => {
  if (dynamicMenus.value && dynamicMenus.value.length > 0) {
    return dynamicMenus.value.map((m: any) => ({
      path: m.path,
      title: m.menu_name,
      icon: m.icon || 'Menu',
      component: m.component
    }))
  }
  
  const defaultMenus = [
    { path: '/', title: 'Home', icon: 'House' }
  ]
  
  if (!userPermissions.value || userPermissions.value.length === 0) {
    return defaultMenus
  }
  
  if (hasPermission('menu:view') || hasPermission('user:view')) {
    defaultMenus.push({ path: '/users', title: 'User Management', icon: 'User' })
  }
  
  if (hasPermission('menu:view') || hasPermission('role:view')) {
    defaultMenus.push({ path: '/roles', title: 'Role Management', icon: 'Key' })
  }
  
  if (hasPermission('order:view')) {
    defaultMenus.push({ path: '/orders', title: 'Orders', icon: 'Document' })
  }
  
  if (hasPermission('wallet:view')) {
    defaultMenus.push({ path: '/wallet', title: 'Wallet', icon: 'Wallet' })
  }
  
  return defaultMenus
})

// Returns the current active route path for highlighting the sidebar menu
const activeMenu = computed(() => route.path)

// Navigates to the selected menu path
const handleMenuSelect = (path: string) => {
  router.push(path)
}

// Prompts the user for logout confirmation and performs logout
const handleLogout = () => {
  ElMessageBox.confirm('Are you sure to logout?', 'Confirm', {
    confirmButtonText: 'Yes',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    router.push('/login')
  })
}

// Fetches the current wallet balance from the server
const fetchWallet = async () => {
  try {
    const res = await walletApi.get()
    walletInfo.value = res
  } catch (e) {
    console.error('Failed to fetch wallet')
  }
}

// Fetches the unread notification count from the server
const fetchNotifications = async () => {
  try {
    const res = await notificationApi.getUnreadCount()
    notificationCount.value = res?.count || 0
  } catch (e) {
    notificationCount.value = 0
  }
}

// Fetches the full notification list for the dropdown
const fetchNotificationList = async () => {
  try {
    const res = await notificationApi.list({ page: 1, page_size: 10 })
    // GET /notification/ returns a plain array; paginated endpoint returns { items, total }
    notificationList.value = Array.isArray(res) ? res : (res?.items ?? [])
  } catch (e) {
    notificationList.value = []
  }
}

// Marks a notification as read and navigates to its link if provided
const handleNotificationClick = async (notification: any) => {
  if (!notification.is_read) {
    try {
      await notificationApi.markAsRead(notification.id)
      notification.is_read = 1
      notificationCount.value = Math.max(0, notificationCount.value - 1)
    } catch (e) {
      console.error('Failed to mark as read')
    }
  }
  
  if (notification.link_url) {
    router.push(notification.link_url)
  }
}

// Fetches the notification list when the dropdown is opened
const handleNotificationDropdown = async (visible: boolean) => {
  if (visible) {
    await fetchNotificationList()
  }
}

// Formats a timestamp into a human-readable relative time string
const formatTime = (time: string) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`
  return date.toLocaleDateString()
}

// Lifecycle hook: initializes wallet, notifications, menus, and permissions on mount
onMounted(() => {
  fetchWallet()
  fetchNotifications()
  loadDynamicMenus()
  loadUserPermissions()
  
  window.addEventListener('storage', (e) => {
    if (e.key === 'wallet_updated') {
      fetchWallet()
    }
  })
})
</script>

<template>
  <el-container class="layout-container">
    <!-- Left Sidebar -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <div class="logo">
        <el-icon v-if="isCollapse" class="logo-icon"><House /></el-icon>
        <span v-else>Housekeeping</span>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="false"
        class="sidebar-menu"
        :background-color="isDarkMode ? '#1e293b' : '#1e293b'"
        :text-color="isDarkMode ? '#94a3b8' : '#94a3b8'"
        active-text-color="#ffffff"
        @select="handleMenuSelect"
      >
        <el-menu-item v-for="item in menuItems" :key="item.path" :index="item.path">
          <el-icon><component :is="item.icon" /></el-icon>
          <template #title>{{ item.title }}</template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <div class="user-card" v-if="!isCollapse && userStore.userInfo">
          <el-avatar :size="36" :style="{ background: 'var(--el-color-primary)' }">
            {{ userStore.userInfo?.username?.charAt(0) || 'U' }}
          </el-avatar>
          <div class="user-info">
            <div class="username">{{ userStore.userInfo?.username || 'User' }}</div>
            <div class="role-tag">{{ userStore.userInfo?.roles?.[0] || 'Guest' }}</div>
          </div>
        </div>
        <div class="sidebar-actions">
          <el-button 
            type="primary" 
            link 
            :icon="isCollapse ? 'Expand' : 'Fold'"
            @click="isCollapse = !isCollapse"
          />
          <el-button 
            type="danger" 
            link 
            icon="SwitchButton"
            @click="handleLogout"
          />
        </div>
      </div>
    </el-aside>

    <!-- Right Content -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h2>{{ menuItems.find(m => m.path === route.path)?.title || 'Dashboard' }}</h2>
        </div>
        <div class="header-right">
          <div class="balance-display" v-if="!userStore.userInfo?.roles?.includes('Administrator')">
            <el-icon><Wallet /></el-icon>
            <span>¥{{ walletInfo.balance?.toFixed(2) || '0.00' }}</span>
          </div>
          
          <el-dropdown trigger="click" @visible-change="handleNotificationDropdown" placement="bottom-end">
            <el-badge :value="notificationCount" :hidden="notificationCount === 0" class="notification-badge">
              <el-icon size="20"><Bell /></el-icon>
            </el-badge>
            <template #dropdown>
              <div class="notification-dropdown">
                <div class="notification-header">
                  <span>Notifications</span>
                  <span class="notification-count" v-if="notificationCount > 0">({{ notificationCount }} unread)</span>
                </div>
                <div class="notification-list" v-if="notificationList.length > 0">
                  <div 
                    v-for="item in notificationList" 
                    :key="item.id" 
                    class="notification-item"
                    :class="{ unread: !item.is_read }"
                    @click="handleNotificationClick(item)"
                  >
                    <div class="notification-icon">
                      <el-icon v-if="item.type === 'warning'" color="#e6a23c"><Warning /></el-icon>
                      <el-icon v-else-if="item.type === 'success'" color="#67c23a"><CircleCheck /></el-icon>
                      <el-icon v-else color="#909399"><Bell /></el-icon>
                    </div>
                    <div class="notification-content">
                      <div class="notification-title">{{ item.title }}</div>
                      <div class="notification-desc" v-if="item.content">{{ item.content }}</div>
                      <div class="notification-time">{{ formatTime(item.create_time) }}</div>
                    </div>
                    <div class="unread-dot" v-if="!item.is_read"></div>
                  </div>
                </div>
                <div class="notification-empty" v-else>
                  <el-icon size="32" color="#c0c4cc"><Bell /></el-icon>
                  <div>No notifications</div>
                </div>
              </div>
            </template>
          </el-dropdown>
          
          <el-dropdown v-if="userStore.userInfo" trigger="click">
            <span class="user-dropdown">
              <el-avatar :size="32" :style="{ background: 'var(--el-color-primary)' }">
                {{ userStore.userInfo?.username?.charAt(0) || 'U' }}
              </el-avatar>
              <span class="username">{{ userStore.userInfo?.username || 'User' }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item icon="User">
                  <div class="profile-item">
                    <div>Username: {{ userStore.userInfo?.username }}</div>
                    <div class="sub-text">Role: {{ userStore.userInfo?.roles?.[0] || 'Guest' }}</div>
                  </div>
                </el-dropdown-item>
                <el-dropdown-item icon="Wallet" @click="router.push('/wallet')">
                  My Wallet
                </el-dropdown-item>
                <el-dropdown-item icon="Setting" @click="router.push('/settings')">Settings</el-dropdown-item>
                <el-dropdown-item divided icon="SwitchButton" @click="handleLogout">Logout</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: var(--sidebar-bg, #1e293b);
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--sidebar-text, #fff);
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-icon {
  font-size: 28px;
  color: var(--el-color-primary);
}

.sidebar-menu {
  flex: 1;
  border-right: none;
}

.sidebar-menu :deep(.el-menu-item) {
  margin: 4px 8px;
  border-radius: 8px;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: var(--el-color-primary) !important;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: var(--el-color-primary-light-9) !important;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  margin-bottom: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.username {
  font-size: 14px;
  color: var(--sidebar-text, #fff);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.role-tag {
  font-size: 12px;
  color: var(--sidebar-text-secondary, #94a3b8);
}

.sidebar-actions {
  display: flex;
  justify-content: space-around;
}

.header {
  background-color: var(--bg-color-overlay, #fff);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-left h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color-primary, #303133);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.balance-display {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(135deg, var(--el-color-primary) 0%, var(--el-color-primary-dark-2, #529b2e) 100%);
  color: #fff;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.notification-badge {
  cursor: pointer;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 12px;
  border-radius: 24px;
  transition: background-color 0.3s;
}

.user-dropdown:hover {
  background-color: var(--bg-color, #f5f7fa);
}

.user-dropdown .username {
  color: var(--text-color-primary, #303133);
  font-weight: 500;
}

.profile-item {
  padding: 4px 0;
}

.profile-item .sub-text {
  font-size: 12px;
  color: var(--text-color-regular, #909399);
  margin-top: 4px;
}

.main-content {
  background-color: var(--bg-color, #f5f7fa);
  padding: 20px;
  overflow-y: auto;
}

.notification-dropdown {
  width: 320px;
  max-height: 400px;
}

.notification-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color-light, #ebeef5);
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notification-count {
  font-size: 12px;
  color: var(--text-color-regular, #909399);
  font-weight: normal;
}

.notification-list {
  max-height: 350px;
  overflow-y: auto;
}

.notification-item {
  padding: 12px 16px;
  display: flex;
  gap: 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
}

.notification-item:hover {
  background-color: var(--bg-color, #f5f7fa);
}

.notification-item.unread {
  background-color: var(--el-color-primary-light-9, #f0f9ff);
}

.notification-item.unread:hover {
  background-color: var(--el-color-primary-light-8, #e6f7ff);
}

.notification-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-weight: 500;
  color: var(--text-color-primary, #303133);
  font-size: 14px;
}

.notification-desc {
  color: var(--text-color-regular, #606266);
  font-size: 12px;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.notification-time {
  color: var(--text-color-regular, #909399);
  font-size: 12px;
  margin-top: 4px;
}

.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--el-color-primary);
  flex-shrink: 0;
  margin-top: 6px;
}

.notification-empty {
  padding: 32px;
  text-align: center;
  color: var(--text-color-regular, #909399);
  font-size: 14px;
}

.notification-empty div {
  margin-top: 8px;
}
</style>
