<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { walletApi, serviceOrderApi } from '@/api'
import { ElMessage } from 'element-plus'

const dateRange = ref([])
const loading = ref(false)

const reportData = ref({
  totalOrders: 156,
  completedOrders: 132,
  pendingOrders: 24,
  avgCompletionTime: 45,
  satisfaction: 4.5,
  staffUtilization: 85
})

const cleanerEarnings = ref([])

const fetchCleanerEarnings = async () => {
  try {
    loading.value = true
    const res = await walletApi.getCleanerEarnings()
    cleanerEarnings.value = res || []
  } catch (error) {
    console.error('Failed to fetch cleaner earnings:', error)
  } finally {
    loading.value = false
  }
}

const handleSettle = async (cleanerId: number, cleanerName: string) => {
  try {
    const params = {
      page: 1,
      page_size: 100,
      filters: { assigned_staff_id: cleanerId, status: 4 }
    }
    const res = await serviceOrderApi.paginated(params)
    const completedOrders = res.items || []
    
    if (completedOrders.length === 0) {
      ElMessage.warning('No completed orders to settle')
      return
    }
    
    for (const order of completedOrders) {
      try {
        await walletApi.settle(order.order_id)
      } catch (e) {
        console.log('Order already settled or error:', e)
      }
    }
    
    ElMessage.success(`Settled payments for ${cleanerName}`)
    fetchCleanerEarnings()
  } catch (error: any) {
    console.error('Settlement error:', error)
    ElMessage.error(error?.response?.data?.detail || 'Settlement failed')
  }
}

const dailyStats = ref([
  { date: '02-22', completed: 28, pending: 4 },
  { date: '02-23', completed: 32, pending: 2 },
  { date: '02-24', completed: 25, pending: 6 },
  { date: '02-25', completed: 30, pending: 3 },
  { date: '02-26', completed: 35, pending: 5 },
  { date: '02-27', completed: 22, pending: 8 },
  { date: '02-28', completed: 18, pending: 3 }
])

const topRooms = ref([
  { room: '1001', times: 12, avgTime: 35 },
  { room: '2003', times: 10, avgTime: 42 },
  { room: '1005', times: 9, avgTime: 38 },
  { room: '3001', times: 8, avgTime: 55 },
  { room: '2002', times: 7, avgTime: 40 }
])

const topStaff = ref([
  { name: 'Zhang San', completed: 45, avgTime: 32, rating: 4.8 },
  { name: 'Li Si', completed: 42, avgTime: 35, rating: 4.7 },
  { name: 'Wang Wu', completed: 38, avgTime: 38, rating: 4.6 },
  { name: 'Zhao Liu', completed: 35, avgTime: 40, rating: 4.5 }
])

onMounted(() => {
  fetchCleanerEarnings()
})
</script>

<template>
  <div class="reports-page">
    <el-row :gutter="20" class="stat-cards">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ reportData.totalOrders }}</div>
            <div class="stat-label">Total Orders</div>
          </div>
          <el-icon class="stat-icon" color="#409eff"><Document /></el-icon>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ reportData.completedOrders }}</div>
            <div class="stat-label">Completed</div>
          </div>
          <el-icon class="stat-icon" color="#67c23a"><CircleCheck /></el-icon>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ reportData.avgCompletionTime }}<span class="unit">min</span></div>
            <div class="stat-label">Avg. Time</div>
          </div>
          <el-icon class="stat-icon" color="#e6a23c"><Timer /></el-icon>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ reportData.satisfaction }}<span class="unit">/5</span></div>
            <div class="stat-label">Satisfaction</div>
          </div>
          <el-icon class="stat-icon" color="#909399"><Star /></el-icon>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :xs="24" :lg="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Order Trend (Last 7 Days)</span>
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="to"
                start-placeholder="Start"
                end-placeholder="End"
                size="small"
              />
            </div>
          </template>
          <div class="chart-placeholder">
            <div class="bar-chart">
              <div v-for="(item, index) in dailyStats" :key="index" class="bar-item">
                <div class="bar completed" :style="{ height: (item.completed * 2.5) + 'px' }">
                  <span class="bar-value">{{ item.completed }}</span>
                </div>
                <div class="bar pending" :style="{ height: (item.pending * 10) + 'px' }">
                  <span class="bar-value">{{ item.pending }}</span>
                </div>
                <div class="bar-label">{{ item.date }}</div>
              </div>
            </div>
            <div class="chart-legend">
              <span class="legend-item"><span class="dot completed"></span>Completed</span>
              <span class="legend-item"><span class="dot pending"></span>Pending</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="6">
        <el-card shadow="hover">
          <template #header>
            <span>Top Rooms</span>
          </template>
          <div class="top-list">
            <div v-for="(room, index) in topRooms" :key="index" class="top-item">
              <div class="rank">{{ index + 1 }}</div>
              <div class="info">
                <div class="name">Room {{ room.room }}</div>
                <div class="desc">{{ room.times }} times · Avg {{ room.avgTime }}min</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="6">
        <el-card shadow="hover">
          <template #header>
            <span>Staff Performance</span>
          </template>
          <div class="top-list">
            <div v-for="(staff, index) in topStaff" :key="index" class="top-item">
              <el-avatar :size="36" :style="{ background: index === 0 ? '#f56c6c' : '#409eff' }">
                {{ staff.name.charAt(0) }}
              </el-avatar>
              <div class="info">
                <div class="name">{{ staff.name }}</div>
                <div class="desc">{{ staff.completed }} orders · {{ staff.rating }} rating</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>Cleaner Earnings & Settlement</span>
              <el-button type="primary" size="small" @click="fetchCleanerEarnings">Refresh</el-button>
            </div>
          </template>
          <el-table :data="cleanerEarnings" v-loading="loading" style="width: 100%">
            <el-table-column prop="cleaner_id" label="ID" width="80" />
            <el-table-column prop="cleaner_name" label="Name" width="150" />
            <el-table-column prop="username" label="Username" width="150" />
            <el-table-column prop="completed_orders" label="Completed Orders" width="150" />
            <el-table-column prop="total_earnings" label="Total Earnings ($)">
              <template #default="{ row }">
                <span style="color: #67c23a; font-weight: 600">${{ (row.total_earnings || 0).toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="Actions" width="200">
              <template #default="{ row }">
                <el-button type="success" size="small" @click="handleSettle(row.cleaner_id, row.cleaner_name)">
                  Settle Payment
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.stat-card {
  border-radius: 12px;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-value .unit {
  font-size: 14px;
  font-weight: 400;
  color: #909399;
  margin-left: 4px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.stat-icon {
  font-size: 40px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-placeholder {
  padding: 20px 0;
}

.bar-chart {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 180px;
  padding: 0 10px;
}

.bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.bar {
  width: 32px;
  border-radius: 4px 4px 0 0;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 4px;
}

.bar.completed {
  background: linear-gradient(180deg, #67c23a, #85ce61);
}

.bar.pending {
  background: linear-gradient(180deg, #e6a23c, #ebb563);
}

.bar-value {
  font-size: 11px;
  color: #fff;
  font-weight: 500;
}

.bar-label {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #606266;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.dot.completed {
  background: #67c23a;
}

.dot.pending {
  background: #e6a23c;
}

.top-list {
  padding: 0;
}

.top-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.top-item:last-child {
  border-bottom: none;
}

.rank {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #606266;
}

.top-item:first-child .rank {
  background: #f56c6c;
  color: #fff;
}

.info {
  flex: 1;
}

.name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.desc {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}
</style>
