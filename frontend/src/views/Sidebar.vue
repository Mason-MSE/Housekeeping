<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { permissionApi } from '@/api'

// Router instance
const router = useRouter()
// Route instance
const route = useRoute()
// User store instance
const userStore = useUserStore()

// Computed current user info
const userInfo = computed(() => userStore.userInfo)
// Computed whether the user is logged in
const isLoggedIn = computed(() => !!userInfo.value)

// List of menu items for the sidebar
const menuItems = ref([])
// Loading state for menu fetching
const loading = ref(false)

// Fetch menu items from the API based on user permissions
const fetchMenus = async () => {
  if (!isLoggedIn.value) {
    menuItems.value = []
    return
  }
  
  try {
    loading.value = true
    const response = await permissionApi.getMyMenus()
    menuItems.value = Array.isArray(response)
      ? response
      : (response?.data || [])
  } catch (error) {
    console.error('Failed to fetch menus:', error)
    menuItems.value = []
  } finally {
    loading.value = false
  }
}

// Lifecycle hook: fetch menus on mount
onMounted(() => {
  fetchMenus()
})

// Watcher: re-fetch menus when user info changes (login/logout)
watch(() => userInfo.value, () => {
  fetchMenus()
})

// Navigate to a given route path
const go = (path) => {
  router.push(path)
}

// Check if a given path matches the current route
const isActive = (path) => {
  return route.path === path
}
</script>

<template>
  <aside class="sidebar">
    <h2 class="logo">Admin</h2>
    <div v-if="loading" class="loading">Loading...</div>
    <ul v-else>
      <li 
        v-for="item in menuItems" 
        :key="item.path"
        :class="{ active: isActive(item.path) }"
      >
        <a @click.prevent="go(item.path)">{{ item.menu_name }}</a>
      </li>
    </ul>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 200px;
  background: #fff;
  border-right: 1px solid #eee;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  overflow-y: auto;
}

.logo {
  padding: 20px;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  border-bottom: 1px solid #eee;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

li {
  border-bottom: 1px solid #f5f5f5;
}

li a {
  display: block;
  padding: 14px 20px;
  color: #666;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s;
}

li a:hover {
  background: #f0f0f0;
  color: #333;
}

li.active a {
  background: #e6f7ff;
  color: #1890ff;
  border-left: 3px solid #1890ff;
}

.loading {
  padding: 20px;
  text-align: center;
  color: #999;
}
</style>
