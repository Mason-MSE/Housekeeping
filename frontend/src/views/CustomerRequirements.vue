<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { portalService } from '@/services'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)

const requirements = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const expandedRows = ref<any[]>([])
const requirementId = ref<string>('')

const userId = computed(() => userStore.userInfo?.id)
const userRoles = computed(() => userStore.userInfo?.roles || [userStore.userInfo?.role || 'guest'])
const isGuest = computed(() => userRoles.value.includes('guest') || userRoles.value.length === 0)

const loadData = async () => {
  if (!userId.value) return
  
  loading.value = true
  try {
    const rid = requirementId.value.trim()
    const res = await portalService.getCustomerRequirements(userId.value, page.value, pageSize.value, {
      requirement_id: rid ? Number(rid) : null
    })
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
  expandedRows.value = []
  loadData()
}

const handlePageChange = (newPage: number) => {
  page.value = newPage
  loadData()
}

const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  page.value = 1
  loadData()
}

const getStatusType = (status: number) => {
  const types: Record<number, string> = { 
    0: 'warning', 
    1: 'success', 
    2: 'primary'
  }
  return types[status] || 'info'
}

const getAppStatusType = (status: number) => {
  const types: Record<number, string> = { 
    0: 'warning', 
    1: 'success', 
    2: 'danger'
  }
  return types[status] || 'info'
}

const pendingCount = computed(() => requirements.value.filter(r => r.status === 0).length)
const assignedCount = computed(() => requirements.value.filter(r => r.status === 1).length)

onMounted(() => {
  if (isGuest.value && userId.value) {
    loadData()
  }
})
</script>

<template>
  <div class="customer-requirements">
    <div class="header">
      <h2>My Requirements</h2>
      <div class="header-actions">
        <el-input
          v-model="requirementId"
          placeholder="Search by Requirement ID"
          clearable
          style="width: 220px"
          @keyup.enter="handleSearch"
        />
        <el-button type="primary" @click="handleSearch" :loading="loading">Search</el-button>
        <el-button @click="loadData" :loading="loading">Refresh</el-button>
      </div>
    </div>

    <div class="stats-cards" v-if="isGuest">
      <el-card class="stat-card">
        <div class="stat-value">{{ pendingCount }}</div>
        <div class="stat-label">Pending</div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-value">{{ assignedCount }}</div>
        <div class="stat-label">Assigned</div>
      </el-card>
    </div>

    <el-table 
      :data="requirements" 
      v-loading="loading" 
      style="width: 100%" 
      stripe
      row-key="id"
      :expand-row-keys="expandedRows"
      @expand-change="(row: any, expanded: boolean) => expandedRows = expanded ? [row.id] : []"
    >
      <el-table-column type="expand">
        <template #default="{ row }">
          <div class="applications-section">
            <h4>Cleaner Applications</h4>
            <el-table v-if="row.applications && row.applications.length > 0" :data="row.applications" size="small">
              <el-table-column prop="cleaner_name" label="Cleaner" width="150" />
              <el-table-column label="Offered Price" width="100">
                <template #default="{ row }">
                  ${{ row.offered_price || 'N/A' }}
                </template>
              </el-table-column>
              <el-table-column prop="status_text" label="Status" width="100">
                <template #default="{ row }">
                  <el-tag :type="getAppStatusType(row.status)" size="small">{{ row.status_text }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="create_time" label="Applied" />
            </el-table>
            <el-empty v-else description="No applications yet" :image-size="60" />
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="guest_name" label="Name" width="100" />
      <el-table-column prop="guest_phone" label="Phone" width="130" />
      <el-table-column prop="property_type" label="Property" width="100" />
      <el-table-column label="Details" width="100">
        <template #default="{ row }">
          {{ row.bedroom }}BR/{{ row.bathroom }}BA
        </template>
      </el-table-column>
      <el-table-column prop="service_type_name" label="Service" width="130" />
      <el-table-column prop="preferred_time" label="Preferred Time" width="130" />
      <el-table-column label="Budget" width="80">
        <template #default="{ row }">
          ${{ row.budget }}
        </template>
      </el-table-column>
      <el-table-column label="Status" width="120">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ row.status_text }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Applications" width="100">
        <template #default="{ row }">
          {{ row.applications?.length || 0 }}
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="Created" width="140" />
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

    <el-empty v-if="!loading && requirements.length === 0 && isGuest" description="No requirements found" />
    <el-empty v-if="!isGuest" description="You don't have access to this page" />
  </div>
</template>

<style scoped>
.customer-requirements {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.header h2 {
  margin: 0;
}
.stats-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}
.stat-card {
  flex: 1;
  text-align: center;
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
}
.stat-label {
  color: #606266;
  margin-top: 5px;
}
.applications-section {
  padding: 10px 20px;
}
.applications-section h4 {
  margin: 0 0 10px 0;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
