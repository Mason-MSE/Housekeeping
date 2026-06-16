<script setup lang="ts">
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import MyOrdersCustomer from './MyOrdersCustomer.vue'
import MyOrdersCleaner from './MyOrdersCleaner.vue'

// User store instance
const userStore = useUserStore()
// Computed user role list
const userRoles = computed(() => userStore.userInfo?.roles || [userStore.userInfo?.role || 'guest'])

// Computed whether the current user is a cleaner/staff/employee
const isCleaner = computed(() =>
  userRoles.value.some(r => ['staff', 'cleaner', 'employee'].includes(String(r).toLowerCase()))
)
</script>

<template>
  <MyOrdersCleaner v-if="isCleaner" />
  <MyOrdersCustomer v-else />
</template>

