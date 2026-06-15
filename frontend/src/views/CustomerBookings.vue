<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { portalApi, transactionApi, reviewApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)

const bookings = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const userId = computed(() => userStore.userInfo?.id || userStore.userInfo?.userId)
const userRoles = computed(() => userStore.userInfo?.roles || [userStore.userInfo?.role || 'guest'])
const isGuest = computed(() => userRoles.value.some(r => ['guest', 'customer', 'user'].includes(r.toLowerCase())))

const detailDialogVisible = ref(false)
const selectedOrder = ref<any>(null)
const reviewDialogVisible = ref(false)
const reviewForm = ref({
  rating: 0,
  comment: ''
})

const statusMap: Record<number, { label: string; type: string }> = {
  0: { label: 'Pending', type: 'info' },
  1: { label: 'Assigned', type: 'warning' },
  2: { label: 'In Progress', type: 'primary' },
  3: { label: 'Pending Review', type: 'warning' },
  4: { label: 'Completed', type: 'success' },
  5: { label: 'Pending Payment', type: 'danger' },
  6: { label: 'Pending Review', type: 'warning' },
  7: { label: 'Completed', type: 'success' },
  8: { label: 'Cancelled', type: 'info' }
}

const loadData = async () => {
  if (!userId.value) return
  
  loading.value = true
  try {
    const res = await portalApi.getCustomerBookings(userId.value, page.value, pageSize.value)
    bookings.value = res?.items || []
    total.value = res?.total || 0
  } catch (e: any) {
    console.error('Failed to load bookings:', e)
    ElMessage.error('Failed to load bookings')
  } finally {
    loading.value = false
  }
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

const getStatusInfo = (status: number) => {
  return statusMap[status] || { label: 'Unknown', type: 'info' }
}

const handleViewDetail = async (row: any) => {
  try {
    const res = await portalApi.getCustomerBookingDetail(row.id, userId.value)
    selectedOrder.value = res
  } catch (e) {
    console.error('Failed to fetch order detail:', e)
    selectedOrder.value = row
  }
  detailDialogVisible.value = true
}

const formatPayAmount = (order: any) => {
  const n = Number(order?.payment_amount)
  return Number.isFinite(n) ? n.toFixed(2) : '100.00'
}

const openReviewDialog = () => {
  reviewForm.value = { rating: 0, comment: '' }
  reviewDialogVisible.value = true
}

const handleOpenReview = async (row: any) => {
  await handleViewDetail(row)
  openReviewDialog()
}

const handlePayment = async (order: any) => {
  try {
    await ElMessageBox.confirm(
      `Please confirm payment for Order #${order.order_no}. Amount: ¥${formatPayAmount(order)}`,
      'Confirm Payment',
      { confirmButtonText: 'Pay Now', cancelButtonText: 'Cancel', type: 'info' }
    )
    await transactionApi.pay(order.id)
    ElMessage.success('Payment successful!')
    selectedOrder.value = order
    reviewForm.value = { rating: 0, comment: '' }
    reviewDialogVisible.value = true
    detailDialogVisible.value = false
    loadData()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Payment error:', error)
      ElMessage.error(error?.response?.data?.detail || 'Payment failed')
    }
  }
}

const handleSubmitReview = async () => {
  if (!selectedOrder.value) return
  const r = Number(reviewForm.value.rating)
  if (!Number.isFinite(r) || r < 0.5 || r > 5) {
    ElMessage.warning('Please select a rating (0.5–5 stars)')
    return
  }
  try {
    await reviewApi.submit(selectedOrder.value.id, r, reviewForm.value.comment)
    ElMessage.success('Review submitted successfully!')
    reviewDialogVisible.value = false
    detailDialogVisible.value = false
    loadData()
  } catch (error: any) {
    console.error('Review error:', error)
    ElMessage.error(error?.response?.data?.detail || 'Failed to submit review')
  }
}

const pendingCount = computed(() => bookings.value.filter(b => b.status === 5).length)
const completedCount = computed(() => bookings.value.filter(b => b.status === 7).length)

onMounted(() => {
  if (isGuest.value && userId.value) {
    loadData()
  }
})
</script>

<template>
  <div class="customer-bookings">
    <div class="header">
      <h2>My Bookings</h2>
      <el-button type="primary" @click="loadData" :loading="loading">Refresh</el-button>
    </div>

    <div class="stats-cards" v-if="isGuest">
      <el-card class="stat-card pending">
        <div class="stat-value">{{ pendingCount }}</div>
        <div class="stat-label">Pending Payment</div>
      </el-card>
      <el-card class="stat-card completed">
        <div class="stat-value">{{ completedCount }}</div>
        <div class="stat-label">Completed</div>
      </el-card>
    </div>

    <el-table :data="bookings" v-loading="loading" style="width: 100%" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="order_no" label="Order No" width="180" />
      <el-table-column prop="service_type" label="Service Type" width="140" />
      <el-table-column prop="room_no" label="Room" width="80" />
      <el-table-column prop="assigned_staff_name" label="Cleaner" width="120" />
      <el-table-column label="Status" width="140">
        <template #default="{ row }">
          <el-tag :type="getStatusInfo(row.status).type">{{ getStatusInfo(row.status).label }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Actions" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleViewDetail(row)">View</el-button>
          <el-button 
            v-if="row.status === 5" 
            type="warning" 
            size="small" 
            @click="handlePayment(row)"
          >
            Pay
          </el-button>
          <el-button 
            v-if="row.status === 6" 
            type="primary" 
            size="small" 
            @click="handleOpenReview(row)"
          >
            Review
          </el-button>
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

    <el-empty v-if="!loading && bookings.length === 0 && isGuest" description="No bookings found" />
    <el-empty v-if="!isGuest" description="You don't have access to this page" />

    <el-dialog v-model="detailDialogVisible" title="Order Details" width="600px" destroy-on-close>
      <div v-if="selectedOrder" class="order-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Order No">{{ selectedOrder.order_no }}</el-descriptions-item>
          <el-descriptions-item label="Status">
            <el-tag :type="getStatusInfo(selectedOrder.status).type">{{ getStatusInfo(selectedOrder.status).label }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Service Type">{{ selectedOrder.service_type }}</el-descriptions-item>
          <el-descriptions-item label="Cleaner">{{ selectedOrder.assigned_staff_name || 'N/A' }}</el-descriptions-item>
          <el-descriptions-item label="Request Time" :span="2">{{ selectedOrder.request_time }}</el-descriptions-item>
          <el-descriptions-item label="Remarks" :span="2">{{ selectedOrder.remarks || 'N/A' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button v-if="selectedOrder?.status === 5" type="warning" @click="handlePayment(selectedOrder)">
          Pay Now
        </el-button>
        <el-button v-if="selectedOrder?.status === 6" type="primary" @click="openReviewDialog">
          Write Review
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="reviewDialogVisible" title="Write Review" width="500px" destroy-on-close>
      <div class="review-form">
        <div class="review-rating">
          <span class="rating-label">Rating:</span>
          <el-rate v-model="reviewForm.rating" allow-half />
        </div>
        <div class="review-comment">
          <el-input
            v-model="reviewForm.comment"
            type="textarea"
            :rows="4"
            placeholder="Share your experience with this cleaner..."
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSubmitReview">Submit Review</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.customer-bookings {
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
.stats-cards {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}
.stat-card {
  flex: 1;
  text-align: center;
}
.stat-card.pending .stat-value {
  color: #e6a23c;
}
.stat-card.completed .stat-value {
  color: #67c23a;
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
}
.stat-label {
  color: #606266;
  margin-top: 5px;
}
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
.order-detail {
  padding: 10px 0;
}
.review-form {
  padding: 10px 0;
}
.review-rating {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.rating-label {
  font-weight: 500;
  color: #303133;
}
.review-comment {
  margin-top: 10px;
}
</style>
