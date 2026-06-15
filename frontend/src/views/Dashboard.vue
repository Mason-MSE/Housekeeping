<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { serviceOrderApi, roomApi, userApi } from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const statistics = ref({
  todayOrders: 0,
  pendingOrders: 0,
  totalRooms: 0,
  availableRooms: 0,
  totalStaff: 0,
  todayCompleted: 0
})

const recentOrders = ref([])

const statusOptions = {
  0: { label: 'Pending', type: 'info' },
  1: { label: 'Assigned', type: 'warning' },
  2: { label: 'In Progress', type: 'primary' },
  3: { label: 'Pending Check', type: 'warning' },
  4: { label: 'Completed', type: 'success' },
  5: { label: 'Cancelled', type: 'danger' }
}

const fetchData = async () => {
  loading.value = true
  try {
    const [orderRes, roomRes, staffRes] = await Promise.all([
      serviceOrderApi.paginated({ page: 1, page_size: 5 }),
      roomApi.list(),
      userApi.getByRole('cleaner')
    ])
    
    recentOrders.value = orderRes.items || []
    
    const rooms = roomRes || []
    statistics.value = {
      todayOrders: orderRes.total || 0,
      pendingOrders: orderRes.items?.filter((o: any) => o.status < 4).length || 0,
      totalRooms: rooms.length,
      availableRooms: rooms.filter((r: any) => r.status === 0).length,
      totalStaff: staffRes?.length || 0,
      todayCompleted: orderRes.items?.filter((o: any) => o.status === 4).length || 0
    }
  } catch (error) {
    console.error('Failed to fetch data:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})

const getStatusType = (status: number) => {
  return statusOptions[status]?.type || 'info'
}

const getStatusLabel = (status: number) => {
  return statusOptions[status]?.label || 'Unknown'
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('en-US')
}

const goToOrders = () => {
  router.push('/orders')
}
</script>

<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stat-cards">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #409eff, #337ecc)">
            <el-icon size="28"><Document /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.todayOrders }}</div>
            <div class="stat-label">Total Orders</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #e6a23c, #cf9236)">
            <el-icon size="28"><Clock /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.pendingOrders }}</div>
            <div class="stat-label">Pending</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #67c23a, #529b2e)">
            <el-icon size="28"><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.availableRooms }}/{{ statistics.totalRooms }}</div>
            <div class="stat-label">Available Rooms</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-icon" style="background: linear-gradient(135deg, #909399, #73767a)">
            <el-icon size="28"><UserFilled /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.totalStaff }}</div>
            <div class="stat-label">Cleaners</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Recent Orders</span>
              <el-button type="primary" link @click="$router.push('/orders')">View All</el-button>
            </div>
          </template>
          <el-table :data="recentOrders" v-loading="loading" style="width: 100%">
            <el-table-column prop="order_no" label="Order No" width="150" />
            <el-table-column prop="room_id" label="Room ID" width="80" />
            <el-table-column prop="status" label="Status" width="120">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="priority" label="Priority" width="100">
              <template #default="{ row }">
                <el-tag :type="row.priority === 0 ? 'info' : row.priority === 1 ? 'warning' : 'danger'">
                  {{ ['Normal', 'Urgent', 'Emergency'][row.priority] }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="request_time" label="Request Time">
              <template #default="{ row }">
                {{ formatDate(row.request_time) }}
              </template>
            </el-table-column>
            <el-table-column label="Action" width="120" fixed="right">
              <template #default>
                <el-button type="primary" link size="small" @click="goToOrders">Detail</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  border-radius: 12px;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 16px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}
</style>
