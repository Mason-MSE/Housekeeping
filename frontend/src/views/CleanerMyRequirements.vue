<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { portalApi } from '@/api'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)

const requirements = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const filters = ref({
  status: null as number | null
})

const userRoles = computed(() => userStore.userInfo?.roles || [userStore.userInfo?.role || 'guest'])
const isCleaner = computed(() => userRoles.value.some(r => ['cleaner', 'staff', 'employee'].includes(r.toLowerCase())))

const cleanerId = computed(() => userStore.userInfo?.id || userStore.userInfo?.userId)

const statusOptions = [
  { value: 0, label: 'Pending' },
  { value: 1, label: 'Assigned/Accepted' },
  { value: 2, label: 'Rejected' }
]

const loadRequirements = async () => {
  if (!isCleaner.value || !cleanerId.value) {
    ElMessage.warning('Only cleaners can access this page')
    return
  }
  
  loading.value = true
  try {
    const params: any = {
      page: page.value,
      page_size: pageSize.value
    }
    if (filters.value.status !== null) params.status = filters.value.status
    
    const res = await portalApi.getCleanerRequirements(cleanerId.value, params)
    requirements.value = res?.items || []
    total.value = res?.total || 0
  } catch (e: any) {
    console.error('Failed to load requirements:', e)
    ElMessage.error('Failed to load requirements')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  loadRequirements()
}

const handleReset = () => {
  filters.value = {
    status: null
  }
  page.value = 1
  loadRequirements()
}

const getStatusType = (status: number) => {
  const types = ['warning', 'success', 'danger']
  return types[status] || 'info'
}

onMounted(() => {
  if (isCleaner.value) {
    loadRequirements()
  }
})
</script>

<template>
  <div class="cleaner-my-requirements">
    <div class="page-header">
      <h2>Cleaner: my requirements</h2>
     
    </div>
    
    <el-card class="filter-card">
      <div class="filters">
        <el-select v-model="filters.status" placeholder="Application Status" clearable style="width: 180px">
          <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
        <el-button type="primary" @click="handleSearch">Search</el-button>
        <el-button @click="handleReset">Reset</el-button>
      </div>
    </el-card>
    
    <el-card class="data-card">
      <el-table :data="requirements" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="guest_name" label="Customer" width="120" />
        <el-table-column prop="guest_phone" label="Phone" width="130" />
        <el-table-column prop="property_type" label="Property" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.property_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Rooms" width="100">
          <template #default="{ row }">
            {{ row.bedroom }}B/{{ row.bathroom }}B
          </template>
        </el-table-column>
        <el-table-column prop="service_type_name" label="Service" width="150" />
        <el-table-column prop="budget" label="Budget" width="90">
          <template #default="{ row }">
            <span class="price">${{ row.budget }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="application_status" label="Status" width="140">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.application_status)" size="small">
              {{ row.application_status_text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="Created" width="140" />
      </el-table>
      
      <el-pagination
        class="pagination"
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="loadRequirements"
      />
    </el-card>
  </div>
</template>

<style scoped>
.cleaner-my-requirements {
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

.price {
  color: #ff6b6b;
  font-weight: 500;
}

.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
