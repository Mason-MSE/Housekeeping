<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { portalApi } from '@/api'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

// User store for role/permission information
const userStore = useUserStore()
// Loading state for the data table
const loading = ref(false)

// List of tasks
const tasks = ref<any[]>([])
// Total number of tasks matching the query
const total = ref(0)
// Current pagination page
const page = ref(1)
// Number of items per page
const pageSize = ref(20)

// Filter criteria for the tasks list
const filters = ref({
  order_no: '',
  cleaner_name: '',
  status: null as number | null,
  start_date: '',
  end_date: ''
})

// Date range picker model
const dateRange = ref<[string, string] | null>(null)

// Array of role names for the current user
const userRoles = computed(() => userStore.userInfo?.roles || [userStore.userInfo?.role || 'guest'])
// Whether the current user has an admin/manager role
const isAdmin = computed(() => userRoles.value.some(r => ['admin', 'manager', 'administrator'].includes(r.toLowerCase())))

// Options for task status filter
const statusOptions = [
  { value: 0, label: 'Pending' },
  { value: 1, label: 'Accepted' },
  { value: 2, label: 'In Progress' },
  { value: 3, label: 'Pending Review' },
  { value: 4, label: 'Completed' },
  { value: 5, label: 'Cancelled' }
]

// Fetch the paginated list of tasks from the API
const loadData = async () => {
  if (!isAdmin.value) return
  
  loading.value = true
  try {
    const params: any = {
      page: page.value,
      page_size: pageSize.value
    }
    if (filters.value.order_no) params.order_no = filters.value.order_no
    if (filters.value.cleaner_name) params.cleaner_name = filters.value.cleaner_name
    if (filters.value.status !== null) params.status = filters.value.status
    if (filters.value.start_date) params.start_date = filters.value.start_date
    if (filters.value.end_date) params.end_date = filters.value.end_date
    
    const res = await portalApi.getAdminTasks(params)
    tasks.value = res?.items || []
    total.value = res?.total || 0
  } catch (e: any) {
    console.error('Failed to load tasks:', e)
    ElMessage.error('Failed to load tasks')
  } finally {
    loading.value = false
  }
}

// Trigger a search with current filters, resetting to page 1
const handleSearch = () => {
  page.value = 1
  loadData()
}

// Reset all filters and reload data from page 1
const handleReset = () => {
  filters.value = {
    order_no: '',
    cleaner_name: '',
    status: null,
    start_date: '',
    end_date: ''
  }
  dateRange.value = null
  page.value = 1
  loadData()
}

// Update date filters when the date range picker changes
const handleDateRangeChange = (val: [string, string] | null) => {
  if (val) {
    filters.value.start_date = val[0]
    filters.value.end_date = val[1]
  } else {
    filters.value.start_date = ''
    filters.value.end_date = ''
  }
}

// Return the human-readable label for a given task status
const getStatusLabel = (status: number) => {
  const option = statusOptions.find(s => s.value === status)
  return option ? option.label : 'Unknown'
}

// Return the Element Plus tag type for a given task status
const getStatusType = (status: number) => {
  const types = ['info', 'success', 'warning', 'warning', 'success', 'danger']
  return types[status] || 'info'
}

// Lifecycle hook: load tasks data on mount
onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="admin-tasks">
    <div class="page-header">
      <h2>Task Management</h2>
      <p class="subtitle">View all cleaner tasks and work progress</p>
    </div>
    
    <el-card class="filter-card">
      <div class="filters">
        <el-input v-model="filters.order_no" placeholder="Order No." clearable style="width: 160px" />
        <el-input v-model="filters.cleaner_name" placeholder="Cleaner Name" clearable style="width: 160px" />
        <el-select v-model="filters.status" placeholder="Status" clearable style="width: 140px">
          <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="to"
          start-placeholder="Start date"
          end-placeholder="End date"
          value-format="YYYY-MM-DD"
          @change="handleDateRangeChange"
        />
        <el-button type="primary" @click="handleSearch">Search</el-button>
        <el-button @click="handleReset">Reset</el-button>
      </div>
    </el-card>
    
    <el-card class="data-card">
      <el-table :data="tasks" v-loading="loading" stripe>
        <el-table-column prop="order_no" label="Order No." width="180" />
        <el-table-column prop="cleaner_name" label="Cleaner" width="120">
          <template #default="{ row }">
            <span v-if="row.cleaner_name">{{ row.cleaner_name }}</span>
            <span v-else class="not-assigned">Not assigned</span>
          </template>
        </el-table-column>
        <el-table-column prop="service_type" label="Service Type" width="150" />
        <el-table-column prop="guest_name" label="Guest Name" width="120" />
        <el-table-column prop="guest_phone" label="Phone" width="130" />
        <el-table-column prop="property_type" label="Property" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.property_type || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Rooms" width="100">
          <template #default="{ row }">
            <span v-if="row.bedroom">{{ row.bedroom }}B/{{ row.bathroom }}B</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="budget" label="Budget" width="90">
          <template #default="{ row }">
            <span class="price">${{ row.budget || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="Created" width="140" />
        <el-table-column prop="complete_time" label="Completed" width="140" />
      </el-table>
      
      <el-pagination
        class="pagination"
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadData"
      />
    </el-card>
  </div>
</template>

<style scoped>
.admin-tasks {
  padding: 24px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #303133;
}

.subtitle {
  margin: 0;
  color: #909399;
}

.filter-card {
  margin-bottom: 16px;
}

.filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.data-card {
  margin-bottom: 16px;
}

.not-assigned {
  color: #909399;
  font-style: italic;
}

.price {
  color: #ff6b6b;
  font-weight: 500;
}

.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
