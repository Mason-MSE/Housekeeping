<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { permissionApi } from '@/api'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const userInfo = computed(() => userStore.userInfo)
const isLoggedIn = computed(() => !!userInfo.value)

const menuItems = ref([])
const loading = ref(false)

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

onMounted(() => {
  fetchMenus()
})

watch(() => userInfo.value, () => {
  fetchMenus()
})

const go = (path) => {
  router.push(path)
}

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
