<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { complaintApi } from '@/api'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

/** Align with MyOrders order status display */
const orderStatusMap: Record<number, { label: string }> = {
  0: { label: 'Pending' },
  1: { label: 'Assigned' },
  2: { label: 'In Progress' },
  3: { label: 'Pending Review' },
  4: { label: 'Completed' },
  5: { label: 'Pending Payment' },
  6: { label: 'Pending Review' },
  7: { label: 'Completed' },
  8: { label: 'Cancelled' }
}

const getOrderStatusType = (status: number) => {
  const map: Record<number, string> = {
    0: 'info',
    1: 'warning',
    2: 'primary',
    3: 'warning',
    4: 'success',
    5: 'danger',
    6: 'warning',
    7: 'success',
    8: 'info'
  }
  return map[status] || 'info'
}

const orderStatusLabel = (booking: Record<string, unknown> | null | undefined) => {
  if (!booking) return '—'
  const text = booking.status_text as string | undefined
  if (text) return text
  const n = Number(booking.status)
  return orderStatusMap[n]?.label || 'Unknown'
}

const complaintStatusTagType = (status: string) => {
  if (status === 'resolved') return 'success'
  if (status === 'rejected') return 'info'
  return 'warning'
}

const formatComplaintResolution = (type: string | undefined) => {
  if (!type) return ''
  const map: Record<string, string> = {
    reject: 'Rejected (no refund)',
    refund_full: 'Full refund to wallet',
    refund_partial: 'Partial refund to wallet',
    waive_partial: 'Partial amount waived (unpaid)'
  }
  return map[type] || type
}

const complaintPreviewUrlList = (c: { evidence?: { photo_url?: string }[] } | null) =>
  (c?.evidence || []).map(e => e?.photo_url).filter((u): u is string => Boolean(u && String(u).trim()))

const userStore = useUserStore()
const loading = ref(false)
const items = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const statusFilter = ref<string | null>(null)

const detailVisible = ref(false)
const detailRow = ref<any>(null)

const bookingDetail = computed(() => detailRow.value?.booking_detail ?? null)

const resolveVisible = ref(false)
const resolveTarget = ref<any>(null)
const resolveForm = ref({
  action: 'reject',
  amount: null as number | null,
  admin_note: ''
})

const userRoles = computed(() => userStore.userInfo?.roles || [userStore.userInfo?.role || 'guest'])
const isAdmin = computed(() =>
  userRoles.value.some(r => ['admin', 'manager', 'administrator'].includes(String(r).toLowerCase()))
)

const statusLabel: Record<string, string> = {
  pending: 'Pending',
  resolved: 'Resolved',
  rejected: 'Rejected'
}

const loadList = async () => {
  if (!isAdmin.value) return
  loading.value = true
  try {
    const res: any = await complaintApi.adminList({
      page: page.value,
      page_size: pageSize.value,
      status: statusFilter.value || undefined
    })
    items.value = res?.items || []
    total.value = res?.total || 0
  } catch (e: any) {
    console.error(e)
    ElMessage.error(e?.response?.data?.detail || 'Failed to load complaints')
  } finally {
    loading.value = false
  }
}

const openDetail = async (row: any) => {
  try {
    const full = await complaintApi.adminGet(row.id)
    detailRow.value = full
    detailVisible.value = true
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Failed to load detail')
  }
}

const openResolve = (row: any) => {
  resolveTarget.value = row
  resolveForm.value = { action: 'reject', amount: null, admin_note: '' }
  resolveVisible.value = true
}

const submitResolve = async () => {
  if (!resolveTarget.value) return
  const payload: any = {
    action: resolveForm.value.action,
    admin_note: resolveForm.value.admin_note || null
  }
  if (['refund_partial', 'waive_partial'].includes(resolveForm.value.action)) {
    const a = Number(resolveForm.value.amount)
    if (!Number.isFinite(a) || a <= 0) {
      ElMessage.warning('Enter a positive amount')
      return
    }
    payload.amount = a
  }
  try {
    await complaintApi.adminResolve(resolveTarget.value.id, payload)
    ElMessage.success('Complaint updated')
    resolveVisible.value = false
    await loadList()
    if (detailVisible.value && detailRow.value?.id === resolveTarget.value.id) {
      detailRow.value = await complaintApi.adminGet(resolveTarget.value.id)
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Resolve failed')
  }
}

onMounted(() => {
  loadList()
})
</script>

<template>
  <div class="admin-complaints">
    <div class="page-header">
      <h2>Customer complaints</h2>
      <p class="subtitle">Review disputes on service orders (refund paid orders or waive unpaid balance).</p>
    </div>

    <el-card v-if="!isAdmin">
      <el-empty description="Admin access only" />
    </el-card>

    <el-card v-else>
      <div class="toolbar">
        <el-select v-model="statusFilter" clearable placeholder="Status" style="width: 160px" @change="loadList">
          <el-option label="Pending" value="pending" />
          <el-option label="Resolved" value="resolved" />
          <el-option label="Rejected" value="rejected" />
        </el-select>
        <el-button type="primary" @click="loadList">Refresh</el-button>
      </div>

      <el-table v-loading="loading" :data="items" stripe style="width: 100%; margin-top: 16px">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="order_no" label="Order" width="140" />
        <el-table-column prop="guest_name" label="Guest" width="140" />
        <el-table-column prop="title" label="Title" min-width="160" show-overflow-tooltip />
        <el-table-column label="Status" width="110">
          <template #default="{ row }">
            <el-tag :type="row.status === 'pending' ? 'warning' : row.status === 'resolved' ? 'success' : 'info'">
              {{ statusLabel[row.status] || row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="Created" width="170" />
        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="openDetail(row)">Detail</el-button>
            <el-button v-if="row.status === 'pending'" size="small" type="primary" @click="openResolve(row)">
              Resolve
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next"
          :page-sizes="[10, 20, 50]"
          @current-change="loadList"
          @size-change="loadList"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="detailVisible"
      title="Complaint detail"
      width="920px"
      top="5vh"
      class="complaint-detail-dialog"
      destroy-on-close
    >
      <div v-if="detailRow" class="complaint-detail-wrap">
        <!-- Complaint (guest dispute) -->
        <div class="order-detail-complaint-panel">
          <div class="complaint-panel-header">
            <div>
              <h4 class="complaint-panel-title">Complaint</h4>
              <p class="complaint-guest-line">
                Guest: <strong>{{ detailRow.guest_name || '—' }}</strong>
                <span class="text-muted">(id {{ detailRow.guest_id }})</span>
              </p>
            </div>
            <el-tag :type="complaintStatusTagType(detailRow.status)" size="default">
              {{ statusLabel[detailRow.status] || detailRow.status }}
            </el-tag>
          </div>
          <div class="complaint-panel-body">
            <div class="complaint-panel-meta">
              <div v-if="detailRow.create_time" class="complaint-meta-line">
                <span class="label">Submitted</span>
                <span>{{ detailRow.create_time }}</span>
              </div>
              <div class="complaint-meta-line">
                <span class="label">Order</span>
                <span
                  >#{{ detailRow.order_no || '—' }}
                  <span class="text-muted">(id {{ detailRow.order_id }})</span></span
                >
              </div>
              <div class="complaint-meta-line">
                <span class="label">Title</span>
                <span>{{ detailRow.title }}</span>
              </div>
              <div v-if="detailRow.description" class="complaint-meta-block">
                <span class="label">Description</span>
                <p class="complaint-desc-text">{{ detailRow.description }}</p>
              </div>
              <template v-if="detailRow.resolution_type || detailRow.resolution_amount != null">
                <div class="complaint-meta-line">
                  <span class="label">Resolution</span>
                  <span>{{ formatComplaintResolution(detailRow.resolution_type) }}</span>
                </div>
                <div v-if="detailRow.resolution_amount != null" class="complaint-meta-line">
                  <span class="label">Amount</span>
                  <span class="price">${{ Number(detailRow.resolution_amount).toFixed(2) }}</span>
                </div>
                <div v-if="detailRow.admin_note" class="complaint-meta-block">
                  <span class="label">Admin note</span>
                  <p class="complaint-desc-text">{{ detailRow.admin_note }}</p>
                </div>
              </template>
            </div>
            <div class="complaint-evidence-panel">
              <h5 class="complaint-evidence-heading">
                Evidence photos
                <span v-if="detailRow.evidence?.length" class="evidence-count">
                  ({{ detailRow.evidence.length }})
                </span>
              </h5>
              <p v-if="detailRow.evidence?.length" class="complaint-evidence-tip text-muted">
                Tap an image to zoom
              </p>
              <p v-else class="complaint-evidence-empty text-muted">No photos uploaded</p>
              <div v-if="detailRow.evidence?.length" class="complaint-evidence-grid-large">
                <el-image
                  v-for="(ev, evIdx) in detailRow.evidence"
                  :key="ev.id ?? evIdx"
                  class="complaint-evidence-elimage"
                  :src="ev.photo_url"
                  :preview-src-list="complaintPreviewUrlList(detailRow)"
                  :initial-index="evIdx"
                  fit="cover"
                  preview-teleported
                >
                  <template #error>
                    <div class="complaint-image-error">Load failed</div>
                  </template>
                </el-image>
              </div>
            </div>
          </div>
        </div>

        <!-- Linked order: service, payment, requirement (same data as guest order detail) -->
        <div v-if="!bookingDetail" class="booking-missing">
          <el-alert type="warning" show-icon :closable="false" title="Order snapshot unavailable" />
          <p class="text-muted">
            The linked order may be missing or no longer visible for this guest. Use order id
            {{ detailRow.order_id }} for manual lookup.
          </p>
        </div>

        <div v-else class="order-detail">
          <div class="detail-header">
            <div class="order-title">
              <h3>Order #{{ bookingDetail.order_no }}</h3>
              <el-tag :type="getOrderStatusType(Number(bookingDetail.status))" size="large">
                {{ orderStatusLabel(bookingDetail) }}
              </el-tag>
            </div>
          </div>

          <div class="detail-grid">
            <div class="detail-section">
              <h4>Service information</h4>
              <div class="detail-row">
                <span class="label">Service type:</span>
                <span class="value">{{ bookingDetail.service_type || '—' }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Request time:</span>
                <span class="value">{{ bookingDetail.request_time || bookingDetail.create_time || '—' }}</span>
              </div>
              <div v-if="bookingDetail.scheduled_start" class="detail-row">
                <span class="label">Scheduled start:</span>
                <span class="value">{{ bookingDetail.scheduled_start }}</span>
              </div>
              <div v-if="bookingDetail.scheduled_end" class="detail-row">
                <span class="label">Scheduled end:</span>
                <span class="value">{{ bookingDetail.scheduled_end }}</span>
              </div>
              <div v-if="bookingDetail.actual_start" class="detail-row">
                <span class="label">Started:</span>
                <span class="value">{{ bookingDetail.actual_start }}</span>
              </div>
              <div v-if="bookingDetail.actual_complete" class="detail-row">
                <span class="label">Completed:</span>
                <span class="value">{{ bookingDetail.actual_complete }}</span>
              </div>
            </div>

            <div class="detail-section payment-section">
              <h4>Payment</h4>
              <template v-if="bookingDetail.payment">
                <div class="detail-row">
                  <span class="label">Amount:</span>
                  <span class="value price">${{ Number(bookingDetail.payment.amount || 0).toFixed(2) }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Status:</span>
                  <span class="value">
                    <el-tag
                      :type="bookingDetail.payment.status === 'completed' ? 'success' : 'warning'"
                      size="small"
                    >
                      {{
                        bookingDetail.payment.status === 'completed' ? 'Paid' : 'Pending payment'
                      }}
                    </el-tag>
                  </span>
                </div>
                <div v-if="bookingDetail.payment.payment_method" class="detail-row">
                  <span class="label">Method:</span>
                  <span class="value">{{ bookingDetail.payment.payment_method }}</span>
                </div>
                <div v-if="bookingDetail.payment.paid_at" class="detail-row">
                  <span class="label">Paid at:</span>
                  <span class="value">{{ bookingDetail.payment.paid_at }}</span>
                </div>
                <div v-if="bookingDetail.payment.transaction_id" class="detail-row">
                  <span class="label">Transaction ID:</span>
                  <span class="value">{{ bookingDetail.payment.transaction_id }}</span>
                </div>
                <div v-if="bookingDetail.payment.description" class="detail-row">
                  <span class="label">Note:</span>
                  <span class="value">{{ bookingDetail.payment.description }}</span>
                </div>
              </template>
              <template v-else>
                <p class="payment-hint text-muted">No payment row on file (guest may not have paid yet).</p>
              </template>
              <div
                v-if="bookingDetail.payment_amount != null && bookingDetail.payment_amount !== ''"
                class="detail-row payment-amount-row"
              >
                <span class="label">Payable reference:</span>
                <span class="value price">${{ Number(bookingDetail.payment_amount).toFixed(2) }}</span>
              </div>
            </div>

            <div
              v-if="bookingDetail.assigned_staff || bookingDetail.assigned_staff_id"
              class="detail-section"
            >
              <h4>Assigned cleaner</h4>
              <div class="staff-card">
                <div class="staff-avatar">
                  {{ (bookingDetail.assigned_staff || 'U').toString().charAt(0) }}
                </div>
                <div class="staff-details">
                  <span class="staff-name">{{
                    bookingDetail.assigned_staff ||
                    (bookingDetail.assigned_staff_id
                      ? `User #${bookingDetail.assigned_staff_id}`
                      : '—')
                  }}</span>
                  <div class="staff-meta">
                    <span v-if="bookingDetail.staff_nationality">🌍 {{ bookingDetail.staff_nationality }}</span>
                    <span v-if="bookingDetail.staff_languages">🗣️ {{ bookingDetail.staff_languages }}</span>
                  </div>
                  <div class="staff-contact">
                    <span v-if="bookingDetail.staff_email">📧 {{ bookingDetail.staff_email }}</span>
                    <span v-if="bookingDetail.staff_phone">📞 {{ bookingDetail.staff_phone }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="bookingDetail.requirement" class="detail-section">
              <h4>Requirement details</h4>
              <div class="detail-row">
                <span class="label">Property:</span>
                <span class="value">{{ bookingDetail.requirement.property_type || '—' }}</span>
              </div>
              <div v-if="bookingDetail.requirement.service_type_name" class="detail-row">
                <span class="label">Service (req.):</span>
                <span class="value">{{ bookingDetail.requirement.service_type_name }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Rooms:</span>
                <span class="value">
                  {{ bookingDetail.requirement.bedroom }} Bed / {{ bookingDetail.requirement.bathroom }} Bath
                  <span v-if="bookingDetail.requirement.living_room"
                    >, {{ bookingDetail.requirement.living_room }} Living</span
                  >
                  <span v-if="bookingDetail.requirement.kitchen"
                    >, {{ bookingDetail.requirement.kitchen }} Kitchen</span
                  >
                </span>
              </div>
              <div v-if="bookingDetail.requirement.lawn || bookingDetail.requirement.car_space" class="detail-row">
                <span class="label">Outdoor / parking:</span>
                <span class="value">
                  <span v-if="bookingDetail.requirement.lawn">Lawn {{ bookingDetail.requirement.lawn }}</span>
                  <span v-if="bookingDetail.requirement.car_space">
                    {{ bookingDetail.requirement.lawn ? ' · ' : '' }}Car space
                    {{ bookingDetail.requirement.car_space }}</span
                  >
                </span>
              </div>
              <div v-if="bookingDetail.requirement.square_footage" class="detail-row">
                <span class="label">Area:</span>
                <span class="value">{{ bookingDetail.requirement.square_footage }} sqft</span>
              </div>
              <div v-if="bookingDetail.requirement.budget" class="detail-row">
                <span class="label">Budget:</span>
                <span class="value price">${{ bookingDetail.requirement.budget }}</span>
              </div>
              <div v-if="bookingDetail.requirement.preferred_time" class="detail-row">
                <span class="label">Preferred time:</span>
                <span class="value">{{ bookingDetail.requirement.preferred_time }}</span>
              </div>
              <div v-if="bookingDetail.requirement.create_time" class="detail-row">
                <span class="label">Requirement created:</span>
                <span class="value">{{ bookingDetail.requirement.create_time }}</span>
              </div>
              <div v-if="bookingDetail.requirement.description" class="detail-row">
                <span class="label">Description:</span>
                <span class="value">{{ bookingDetail.requirement.description }}</span>
              </div>
            </div>

            <div v-if="bookingDetail.remarks" class="detail-section">
              <h4>Order remarks</h4>
              <p>{{ bookingDetail.remarks }}</p>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="resolveVisible" title="Resolve complaint" width="520px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item label="Action">
          <el-radio-group v-model="resolveForm.action">
            <el-radio label="reject">Reject (no refund / no waiver)</el-radio>
            <el-radio label="refund_full">Refund full (paid orders only)</el-radio>
            <el-radio label="refund_partial">Refund partial (paid)</el-radio>
            <el-radio label="waive_partial">Waive partial (unpaid)</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item
          v-if="resolveForm.action === 'refund_partial' || resolveForm.action === 'waive_partial'"
          label="Amount"
        >
          <el-input-number v-model="resolveForm.amount" :min="0.01" :step="1" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Admin note (optional)">
          <el-input v-model="resolveForm.admin_note" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resolveVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitResolve">Submit</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.admin-complaints {
  padding: 24px;
}
.page-header h2 {
  margin: 0 0 8px 0;
}
.subtitle {
  margin: 0 0 16px 0;
  color: #909399;
}
.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
}
.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.text-muted {
  color: #909399;
  font-size: 13px;
}

.complaint-detail-wrap {
  max-height: 72vh;
  overflow-y: auto;
  padding-right: 4px;
}

.booking-missing {
  margin-top: 20px;
}
.booking-missing p {
  margin: 12px 0 0 0;
  font-size: 13px;
}

.complaint-guest-line {
  margin: 6px 0 0 0;
  font-size: 14px;
  color: #606266;
}

/* Complaint panel — match MyOrders */
.order-detail-complaint-panel {
  margin-bottom: 8px;
  padding: 18px;
  background: linear-gradient(180deg, #f5f9ff 0%, #ffffff 48%);
  border: 1px solid #c6e2ff;
  border-radius: 12px;
}

.complaint-panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.complaint-panel-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.complaint-panel-meta {
  font-size: 14px;
  color: #606266;
}

.complaint-meta-line {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 16px;
  margin-bottom: 10px;
  align-items: baseline;
}

.complaint-meta-line .label {
  min-width: 140px;
  color: #909399;
  font-size: 13px;
}

.complaint-meta-block {
  margin-bottom: 12px;
}

.complaint-meta-block .label {
  display: block;
  color: #909399;
  font-size: 13px;
  margin-bottom: 6px;
}

.complaint-desc-text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  max-width: 100%;
}

.complaint-meta-line .price {
  color: #67c23a;
  font-weight: 600;
}

.complaint-evidence-panel {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px dashed #dcdfe6;
}

.complaint-evidence-heading {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.complaint-evidence-heading .evidence-count {
  font-weight: 500;
  color: #409eff;
}

.complaint-evidence-tip {
  margin: 0 0 12px 0;
  font-size: 13px;
}

.complaint-evidence-empty {
  margin: 0;
  font-size: 13px;
}

.complaint-evidence-grid-large {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
}

.complaint-evidence-elimage {
  width: 168px;
  height: 168px;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #dcdfe6;
  flex-shrink: 0;
  cursor: zoom-in;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.complaint-evidence-elimage:hover {
  border-color: #409eff;
  box-shadow: 0 4px 14px rgba(64, 158, 255, 0.25);
}

.complaint-evidence-elimage :deep(.el-image__inner) {
  width: 168px !important;
  height: 168px !important;
}

.complaint-image-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 168px;
  height: 168px;
  background: #f5f7fa;
  font-size: 12px;
  color: #909399;
  text-align: center;
  padding: 8px;
}

/* Order snapshot — match MyOrders order detail */
.order-detail {
  padding: 10px 0 0;
  font-size: 14px;
  line-height: 1.55;
  color: #606266;
  -webkit-font-smoothing: antialiased;
}

.detail-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.order-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.order-title h3 {
  margin: 0;
  color: #303133;
  font-size: 19px;
  font-weight: 600;
  letter-spacing: -0.02em;
  line-height: 1.3;
}

.detail-grid {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-section {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px 18px;
}

.payment-section {
  background: linear-gradient(135deg, #f0f9eb 0%, #f5f7fa 100%);
  border: 1px solid #e1f3d8;
}

.payment-hint {
  margin: 0 0 10px 0;
  font-size: 13px;
}

.payment-amount-row {
  margin-top: 8px;
  padding-top: 10px;
  border-top: 1px dashed #dcdfe6;
}

.detail-section h4 {
  margin: 0 0 14px 0;
  color: #303133;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.01em;
  line-height: 1.35;
  border-bottom: 1px solid #dcdfe6;
  padding-bottom: 10px;
}

.detail-row {
  display: flex;
  margin-bottom: 10px;
  font-size: 14px;
  line-height: 1.5;
  align-items: flex-start;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-row .label {
  flex-shrink: 0;
  color: #8b919b;
  min-width: 132px;
  font-size: 13px;
  font-weight: 500;
}

.detail-row .value {
  color: #303133;
  font-weight: 400;
  flex: 1;
  min-width: 0;
  word-break: break-word;
}

.detail-row .price {
  color: #67c23a;
  font-weight: 600;
  font-size: 15px;
  font-variant-numeric: tabular-nums;
}

.detail-section > p {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
}

.staff-card {
  display: flex;
  gap: 16px;
  align-items: center;
}

.staff-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: bold;
}

.staff-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.staff-name {
  font-weight: 600;
  font-size: 15px;
  color: #303133;
  letter-spacing: -0.01em;
}

.staff-meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
  line-height: 1.45;
  color: #606266;
}

.staff-contact {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  font-size: 13px;
  color: #606266;
}
</style>
