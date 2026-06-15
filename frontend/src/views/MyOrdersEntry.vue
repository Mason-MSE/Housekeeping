<script setup lang="ts">
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import MyOrdersCustomer from './MyOrdersCustomer.vue'
import MyOrdersCleaner from './MyOrdersCleaner.vue'

const userStore = useUserStore()
const userRoles = computed(() => userStore.userInfo?.roles || [userStore.userInfo?.role || 'guest'])

const isCleaner = computed(() =>
  userRoles.value.some(r => ['staff', 'cleaner', 'employee'].includes(String(r).toLowerCase()))
)
</script>

<template>
  <MyOrdersCleaner v-if="isCleaner" />
  <MyOrdersCustomer v-else />
</template>

