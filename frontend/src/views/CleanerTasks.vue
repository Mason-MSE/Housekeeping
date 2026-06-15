<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { portalService } from '@/services'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)

const tasks = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const selectedStatus = ref<number | undefined>(undefined)

const cleanerId = computed(() => userStore.userInfo?.id)
const isCleaner = computed(() => ['staff', 'cleaner', 'employee'].includes(userInfo.value?.role))

const userInfo = computed(() => userStore.userInfo)

const statusOptions = [
  { value: undefined, label: 'All' },
  { value: 0, label: 'Pending', type: 'warning' },
  { value: 1, label: 'Accepted', type: 'success' },
  { value: 2, label: 'Rejected', type: 'danger' },
]

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

const handleSearch = () => {
  page.value = 1
  loadApplications()
}

const handlePageChange = (newPage: number) => {
  page.value = newPage
  loadApplications()
}

const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  page.value = 1
  loadApplications()
}

const getStatusType = (status: number) => {
  const types: Record<number, string> = { 
    0: 'warning', 
    1: 'success', 
    2: 'danger'
  }
  return types[status] || 'info'
}

const filterByStatus = (status: number | undefined) => {
  selectedStatus.value = status
  page.value = 1
  loadApplications()
}

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
