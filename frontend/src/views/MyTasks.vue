<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { portalService } from '@/services'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)

const activeTab = ref('applications')
const applications = ref<any[]>([])
const orders = ref<any[]>([])
const totalApplications = ref(0)
const totalOrders = ref(0)

const page = ref(1)
const pageSize = ref(10)
const searchStatus = ref<number | undefined>(undefined)

const userInfo = computed(() => userStore.userInfo)
const isCleaner = computed(() => ['staff', 'cleaner', 'employee'].includes(userInfo.value?.role))

const statusOptions = [
  { label: 'All Status', value: undefined },
  { label: 'Pending', value: 0 },
  { label: 'Accepted', value: 1 },
  { label: 'Rejected', value: 2 },
]

const orderStatusOptions = [
  { label: 'All Status', value: undefined },
  { label: 'Pending', value: 0 },
  { label: 'Accepted', value: 1 },
  { label: 'In Progress', value: 2 },
  { label: 'Completed', value: 4 },
  { label: 'Cancelled', value: 5 },
]

const statusMap: Record<number, { label: string; type: string }> = {
  0: { label: 'Pending', type: 'warning' },
  1: { label: 'Accepted', type: 'success' },
  2: { label: 'In Progress', type: 'primary' },
  3: { label: 'Pending Review', type: 'info' },
  4: { label: 'Completed', type: 'success' },
  5: { label: 'Cancelled', type: 'danger' }
}

const loadApplications = async () => {
  if (!isCleaner.value || !userInfo.value?.id) return
  
  loading.value = true
  try {
    const res: any = await portalService.getCleanerApplications(
      userInfo.value.id,
      searchStatus.value,
      page.value,
      pageSize.value
    )
    applications.value = res.items || []
    totalApplications.value = res.total || 0
  } catch (e: any) {
    console.error('Failed to load applications:', e)
    ElMessage.error(e?.message || 'Failed to load applications')
  } finally {
    loading.value = false
  }
}

const loadOrders = async () => {
  if (!isCleaner.value || !userInfo.value?.id) return
  
  loading.value = true
  try {
    const res: any = await portalService.getCleanerTasks(
      userInfo.value.id,
      searchStatus.value,
      page.value,
      pageSize.value
    )
    orders.value = res.items || []
    totalOrders.value = res.total || 0
  } catch (e: any) {
    console.error('Failed to load orders:', e)
    ElMessage.error(e?.message || 'Failed to load orders')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  if (activeTab.value === 'applications') {
    loadApplications()
  } else {
    loadOrders()
  }
}

const handlePageChange = (newPage: number) => {
  page.value = newPage
  if (activeTab.value === 'applications') {
    loadApplications()
  } else {
    loadOrders()
  }
}

const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  page.value = 1
  if (activeTab.value === 'applications') {
    loadApplications()
  } else {
    loadOrders()
  }
}

const getStatusInfo = (status: number) => {
  return statusMap[status] || { label: 'Unknown', type: 'info' }
}

watch(activeTab, () => {
  page.value = 1
  searchStatus.value = undefined
  if (activeTab.value === 'applications') {
    loadApplications()
  } else {
    loadOrders()
  }
})

onMounted(() => {
  if (isCleaner.value) {
    loadApplications()
  }
})
</script>

<template>
  <div class="my-tasks-page">
    <div class="page-header">
      <h2>My Tasks</h2>
      <p class="subtitle">Manage your applications and orders</p>
    </div>

    <el-tabs v-model="activeTab" class="task-tabs">
      <el-tab-pane label="My Applications" name="applications">
        <el-card class="task-card">
          
          <el-table :data="applications" v-loading="loading" stripe>
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column label="Type" width="100">
              <template #default="{ row }">
                <el-tag>Application</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="Title" min-width="180" />
            <el-table-column prop="property_type" label="Property" width="100" />
            <el-table-column prop="bedroom" label="Bedroom" width="80" />
            <el-table-column prop="bathroom" label="Bathroom" width="90" />
            <el-table-column prop="budget" label="Budget" width="100">
              <template #default="{ row }">
                <span class="price">${{ row.budget }}</span>
              </template>
            </el-table-column>
            <el-table-column label="Status" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusInfo(row.status).type">
                  {{ getStatusInfo(row.status).label }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="create_time" label="Created" width="150" />
          </el-table>
          
          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="page"
              v-model:page-size="pageSize"
              :page-sizes="[5, 10, 20, 50]"
              :total="totalApplications"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handlePageChange"
            />
          </div>
          
          <el-empty v-if="!loading && applications.length === 0" description="No applications found" />
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="My Orders" name="orders">
        <el-card class="task-card">
          
          <el-table :data="orders" v-loading="loading" stripe>
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="order_no" label="Order No" width="150" />
            <el-table-column prop="service_type" label="Service" min-width="150" />
            <el-table-column prop="guest_name" label="Guest" width="100" />
            <el-table-column prop="property_type" label="Property" width="100" />
            <el-table-column prop="bedroom" label="Bedroom" width="80" />
            <el-table-column prop="bathroom" label="Bathroom" width="90" />
            <el-table-column label="Status" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusInfo(row.status).type">
                  {{ row.status_text }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="create_time" label="Created" width="150" />
          </el-table>
          
          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="page"
              v-model:page-size="pageSize"
              :page-sizes="[5, 10, 20, 50]"
              :total="totalOrders"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handlePageChange"
            />
          </div>
          
          <el-empty v-if="!loading && orders.length === 0" description="No orders found" />
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<style scoped>
.my-tasks-page {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
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

.task-tabs {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.task-card {
  margin-top: 16px;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.price {
  color: #ff6b6b;
  font-weight: bold;
}
</style>
