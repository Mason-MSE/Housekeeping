<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { House, ArrowDown } from '@element-plus/icons-vue'
import { permissionApi } from '@/api'

const router = useRouter()
const userStore = useUserStore()

const isLoggedIn = computed(() => !!userStore.userInfo)
const userInfo = computed(() => userStore.userInfo)
const dropdownMenus = ref<any[]>([])

const loadMenus = async () => {
  if (!isLoggedIn.value) {
    dropdownMenus.value = []
    return
  }
  try {
    const res = await permissionApi.getMyMenus()
    dropdownMenus.value = Array.isArray(res) ? res : (res?.data || [])
  } catch (e) {
    console.error('Failed to load menus:', e)
    dropdownMenus.value = []
  }
}

const goToDashboard = (path: string) => {
  if (path === 'logout') {
    userStore.logout()
    router.push('/')
  } else {
    router.push(path)
  }
}

const goToLogin = () => {
  router.push({ path: '/login', query: { redirect: 'portal' } })
}

const goToRegister = () => {
  router.push({ path: '/login', query: { mode: 'register', redirect: 'portal' } })
}

onMounted(() => {
  loadMenus()
})

watch(isLoggedIn, () => {
  loadMenus()
})
</script>

<template>
  <header class="portal-header">
    <div class="header-content">
      <div class="logo">
        <div class="logo-icon-wrapper">
          <el-icon class="logo-icon"><House /></el-icon>
        </div>
        <div class="logo-text-wrapper">
          <span class="logo-text">CleanPro</span>
          <span class="logo-tag">Professional</span>
        </div>
      </div>

      <nav class="header-nav">
      </nav>

      <div class="header-actions" v-if="isLoggedIn">
        <el-dropdown trigger="click" @command="goToDashboard">
          <div class="user-menu">
            <el-avatar :size="32" class="user-avatar">
              {{ userInfo?.username?.charAt(0)?.toUpperCase() || 'U' }}
            </el-avatar>
            <span class="username">{{ userInfo?.username || 'User' }}</span>
            <el-icon><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item 
                v-for="menu in dropdownMenus" 
                :key="menu.path" 
                :command="menu.path"
              >
                {{ menu.menu_name }}
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">Logout</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <div class="header-actions" v-else>
        <el-button text @click="goToLogin">Login</el-button>
        <el-button type="primary" @click="goToRegister">Sign Up</el-button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.portal-header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 12px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  font-size: 24px;
  color: #409eff;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.logo-tag {
  background: #409eff;
  color: #fff;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
}

.header-nav {
  display: flex;
  gap: 4px;
}

.nav-item {
  padding: 6px 12px;
  color: #666;
  text-decoration: none;
  font-size: 14px;
  border-radius: 4px;
}

.nav-item:hover {
  color: #409eff;
  background: #f5f7fa;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 16px;
  background: rgba(64, 158, 255, 0.1);
}

.user-avatar {
  background: #409eff;
}

.username {
  color: #409eff;
  font-size: 14px;
}

@media (max-width: 768px) {
  .header-nav {
    display: none;
  }
}
</style>
