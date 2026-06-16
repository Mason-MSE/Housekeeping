<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { portalService } from '@/services'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

// User store for role/permission information
const userStore = useUserStore()
// Loading state for the data table
const loading = ref(false)

// List of cleaner task applications
const tasks = ref<any[]>([])
// Total number of tasks matching the query
const total = ref(0)
// Current pagination page
const page = ref(1)
// Number of items per page
const pageSize = ref(20)
// Currently selected status filter value
const selectedStatus = ref<number | undefined>(undefined)

// The current cleaner's user ID
const cleanerId = computed(() => userStore.userInfo?.id)
// Whether the current user has a cleaner/staff/employee role
const isCleaner = computed(() => ['staff', 'cleaner', 'employee'].includes(userInfo.value?.role))

// The current user's info object
const userInfo = computed(() => userStore.userInfo)

// Options for task status filter
const statusOptions = [
  { value: undefined, label: 'All' },
  { value: 0, label: 'Pending', type: 'warning' },
  { value: 1, label: 'Accepted', type: 'success' },
  { value: 2, label: 'Rejected', type: 'danger' },
]

// Fetch the list of cleaner task applications from the API
const loadApplications = async () => {
  if (!cleanerId.value || !isCleaner.value) return
  
  loading.value = true
  try {
    const res: any = await portalService.getCleanerApplications(
      cleanerId.value,
      selectedStatus.value,
      page.value,
      pageSize.value
    )
    tasks.value = res?.items || []
    total.value = res?.total || 0
  } catch (e: any) {
    console.error('Failed to load applications:', e)
    ElMessage.error('Failed to load applications')
  } finally {
    loading.value = false
  }
}

// Trigger a search and reset to page 1
const handleSearch = () => {
  page.value = 1
  loadApplications()
}

// Handle pagination page change and reload data
const handlePageChange = (newPage: number) => {
  page.value = newPage
  loadApplications()
}

// Handle page size change and reload data from page 1
const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  page.value = 1
  loadApplications()
}

// Return the Element Plus tag type for a given task status
const getStatusType = (status: number) => {
  const types: Record<number, string> = { 
    0: 'warning', 
    1: 'success', 
    2: 'danger'
  }
  return types[status] || 'info'
}

// Filter the task list by a specific status value
const filterByStatus = (status: number | undefined) => {
  selectedStatus.value = status
  page.value = 1
  loadApplications()
}

// Lifecycle hook: load applications on mount if user is a cleaner
onMounted(() => {
  if (isCleaner.value) {
    loadApplications()
  }
})
</script>

<template>
  <div class="cleaner-tasks">
    <div class="header">
      <h2>My Tasks</h2>
      <el-button type="primary" @click="handleSearch" :loading="loading">Refresh</el-button>
    </div>

    <div class="status-tabs">
      <el-button 
        v-for="status in statusOptions" 
        :key="String(status.value)"
        :type="selectedStatus === status.value ? 'primary' : 'default'"
        @click="filterByStatus(status.value)"
      >
        {{ status.label }}
      </el-button>
    </div>

    <el-table :data="tasks" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="Application" min-width="200" />
      <el-table-column prop="property_type" label="Property" width="100" />
      <el-table-column prop="bedroom" label="Bedroom" width="80" />
      <el-table-column prop="bathroom" label="Bathroom" width="80" />
      <el-table-column prop="budget" label="Budget" width="100">
        <template #default="{ row }">
          <span class="price">${{ row.budget }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Status" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ row.status_text }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="Applied" width="150" />
    </el-table>

    <el-pagination
      class="pagination"
      v-model:current-page="page"
      v-model:page-size="pageSize"
      :page-sizes="[10, 20, 50, 100]"
      :total="total"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
    />

    <el-empty v-if="!isCleaner" description="You don't have access to this page" />
  </div>
</template>

<style scoped>
.cleaner-tasks {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.header h2 {
  margin: 0;
}
.status-tabs {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
.price {
  color: #ff6b6b;
  font-weight: bold;
}
</style>
