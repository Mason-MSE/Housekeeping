<template>
  <NavBar v-if="showNavBar" />
  <router-view v-else />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from '@/components/NavBar.vue'

const route = useRoute()
const showNavBar = computed(() => {
  const noNavPaths = ['/login', '/']
  return !noNavPaths.includes(route.path)
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --bg-color: #f5f7fa;
  --bg-color-page: #ffffff;
  --bg-color-overlay: #ffffff;
  --text-color-primary: #303133;
  --text-color-regular: #606266;
  --border-color: #dcdfe6;
  --border-color-light: #e4e7ed;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: var(--bg-color);
  color: var(--text-color-primary);
}

#app {
  min-height: 100vh;
  background-color: var(--bg-color-page);
}
</style>
