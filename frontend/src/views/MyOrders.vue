<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { portalApi } from '@/api'
import { serviceOrderApi, orderPhotoApi, transactionApi, reviewApi, complaintApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import draggable from 'vuedraggable'
import { Rank } from '@element-plus/icons-vue'

type ForcedRole = 'customer' | 'cleaner'

const props = defineProps<{
  /** When set, forces this page to behave as customer or cleaner (no role-based mixing). */
  forcedRole?: ForcedRole
}>()

const userStore = useUserStore()
const loading = ref(false)

const myOrders = ref<any[]>([])
const totalOrders = ref(0)
const page = ref(1)
const pageSize = ref(20)

const userId = computed(() => userStore.userInfo?.id || userStore.userInfo?.userId)
const userRoles = computed(() => userStore.userInfo?.roles || [userStore.userInfo?.role || 'guest'])
const isCleaner = computed(() => {
  if (props.forcedRole) return props.forcedRole === 'cleaner'
  return userRoles.value.some(r => ['staff', 'cleaner', 'employee'].includes(String(r).toLowerCase()))
})
const isCustomer = computed(() => {
  if (props.forcedRole) return props.forcedRole === 'customer'
  return userRoles.value.some(r => ['guest', 'customer', 'user'].includes(String(r).toLowerCase()))
})

const pageTitle = computed(() => (isCleaner.value ? 'My Orders (Cleaner)' : 'My Orders (Customer)'))

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

const handleReorder = async () => {
  const currentPhotos = sortedPhotos.value
  const photoIds = currentPhotos.map((p: any) => p.id)
  try {
    await orderPhotoApi.reorder(photoIds)
    ElMessage.success('Photos reordered')
  } catch (error: any) {
    console.error('Reorder error:', error)
    ElMessage.error('Failed to reorder photos')
  }
}

const previewVisible = ref(false)
const previewUrl = ref('')
const previewUrls = ref<string[]>([])
const previewInitialIndex = ref(0)

const reviewDialogVisible = ref(false)
const reviewForm = ref({
  rating: 0,
  comment: ''
})

const formatPayAmount = (order: any) => {
  const n = Number(order?.payment_amount)
  return Number.isFinite(n) ? n.toFixed(2) : '100.00'
}

const handlePayment = async (order: any) => {
  try {
    await ElMessageBox.confirm(
      `Please confirm payment for Order #${order.order_no}. Amount: $${formatPayAmount(order)}`,
      'Confirm Payment',
      { confirmButtonText: 'Pay Now', cancelButtonText: 'Cancel', type: 'info' }
    )
    await transactionApi.pay(order.id)
    ElMessage.success('Payment successful!')
    selectedOrder.value = order
    reviewForm.value = { rating: 0, comment: '' }
    reviewDialogVisible.value = true
    detailDialogVisible.value = false
    loadMyOrders()
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
    loadMyOrders()
  } catch (error: any) {
    console.error('Review error:', error)
    ElMessage.error(error?.response?.data?.detail || 'Failed to submit review')
  }
}

const myComplaints = ref<any[]>([])

const loadMyComplaints = async () => {
  if (!userId.value || !isCustomer.value) return
  try {
    const list = await complaintApi.myList()
    myComplaints.value = Array.isArray(list) ? list : []
  } catch {
    myComplaints.value = []
  }
}

const complaintByOrderId = computed(() => {
  const m = new Map<number, any>()
  for (const c of myComplaints.value) {
    if (c?.order_id != null) m.set(Number(c.order_id), c)
  }
  return m
})

/** List API uses complete_time; detail uses actual_complete */
const orderCompletionTime = (order: any) => order?.actual_complete || order?.complete_time || null

const withinComplaintWindow = (order: any) => {
  const ac = orderCompletionTime(order)
  if (!ac) return false
  const done = new Date(ac).getTime()
  if (!Number.isFinite(done)) return false
  const limitMs = 15 * 24 * 60 * 60 * 1000
  return Date.now() - done <= limitMs
}

const complaintForOrder = (order: any) => complaintByOrderId.value.get(Number(order.id))

/** Current order detail dialog — customer complaint + evidence */
const selectedComplaint = computed(() => {
  if (!isCustomer.value || !selectedOrder.value) return null
  return complaintForOrder(selectedOrder.value) ?? null
})

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
    waive_partial: 'Partial amount waived (unpaid)',
  }
  return map[type] || type
}

/** URLs for el-image preview gallery in Order Details */
const complaintPreviewUrlList = (c: any) =>
  (c?.evidence || []).map((e: any) => e?.photo_url).filter((u: string) => Boolean(u && String(u).trim()))

const canFileComplaint = (order: any) => {
  if (!isCustomer.value) return false
  if (Number(order.status) === 8) return false
  if (!orderCompletionTime(order)) return false
  if (!withinComplaintWindow(order)) return false
  if (complaintForOrder(order)) return false
  return [4, 5, 6, 7].includes(Number(order.status))
}

const complaintDialogVisible = ref(false)
const complaintOrderId = ref<number | null>(null)
const complaintForm = ref({ title: '', description: '' })
const complaintUploadList = ref<any[]>([])

const openComplaintDialog = (order: any) => {
  complaintOrderId.value = order.id
  complaintForm.value = { title: '', description: '' }
  complaintUploadList.value = []
  complaintDialogVisible.value = true
}

const handleComplaintFilesChange = (_file: any, files: any) => {
  complaintUploadList.value = files
}

const submitComplaint = async () => {
  if (!complaintOrderId.value) return
  const title = complaintForm.value.title.trim()
  if (!title) {
    ElMessage.warning('Please enter a title')
    return
  }
  const evidence_urls: string[] = []
  const files = complaintUploadList.value.slice()
  const readOne = (entry: any) =>
    new Promise<string>((resolve, reject) => {
      const raw = entry?.raw ?? entry
      const reader = new FileReader()
      reader.onload = () => resolve(String(reader.result || ''))
      reader.onerror = () => reject(new Error('read failed'))
      reader.readAsDataURL(raw)
    })
  try {
    for (const f of files) {
      if (evidence_urls.length >= 20) break
      evidence_urls.push(await readOne(f))
    }
    await complaintApi.create({
      order_id: complaintOrderId.value,
      title,
      description: complaintForm.value.description.trim() || undefined,
      evidence_urls
    })
    ElMessage.success('Complaint submitted')
    complaintDialogVisible.value = false
    await loadMyComplaints()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Failed to submit complaint')
  }
}

const loadMyOrders = async () => {
  if (!userId.value) return
  
  loading.value = true
  try {
    let res: any
    if (isCleaner.value) {
      res = await portalApi.getCleanerBookings(userId.value, page.value, pageSize.value)
    } else {
      res = await portalApi.getCustomerBookings(userId.value, page.value, pageSize.value)
    }
    myOrders.value = res?.items || []
    totalOrders.value = res?.total || 0
    await loadMyComplaints()
  } catch (e: any) {
    console.error('Failed to load orders:', e)
  } finally {
    loading.value = false
  }
}

const getStatusInfo = (status: number) => {
  return statusMap[status] || { label: 'Unknown', type: 'info' }
}

const detailPhotos = computed(() => orderPhotos.value)

const photoDialogVisible = ref(false)
const photoOrderId = ref<number | null>(null)
const photoType = ref('before')
const orderPhotos = ref<any[]>([])
const uploadFileList = ref<any[]>([])

const refreshOrderPhotos = async (orderId: number) => {
  const res = await orderPhotoApi.getByOrder(orderId)
  orderPhotos.value = Array.isArray(res) ? res : []
}

// Source-of-truth list for draggable (current photoType only).
// Uses a getter+setter so vuedraggable can mutate ordering safely.
const sortedPhotos = computed<any[]>({
  get: () => {
    return orderPhotos.value
      .filter((p: any) => p?.photo_type === photoType.value)
      .slice()
      .sort((a: any, b: any) => (Number(a?.sort_order) || 0) - (Number(b?.sort_order) || 0))
  },
  set: (newList: any[]) => {
    const updatedCurrentType = (newList || []).map((p: any, idx: number) => ({
      ...p,
      sort_order: idx
    }))
    const otherType = orderPhotos.value.filter((p: any) => p?.photo_type !== photoType.value)
    orderPhotos.value = [...updatedCurrentType, ...otherType]
  }
})

const detailDialogVisible = ref(false)
const selectedOrder = ref<any>(null)

const handleViewDetail = async (row: any) => {
  try {
    let res: any
    if (isCleaner.value) {
      res = await portalApi.getCleanerBookingDetail(row.id, userId.value)
    } else {
      res = await portalApi.getCustomerBookingDetail(row.id, userId.value)
    }
    selectedOrder.value = res
    await refreshOrderPhotos(row.id)
  } catch (e) {
    console.error('Failed to fetch order detail:', e)
    selectedOrder.value = row
    orderPhotos.value = []
  }
  await loadMyComplaints()
  detailDialogVisible.value = true
}

const handleOpenReview = async (row: any) => {
  await handleViewDetail(row)
  reviewForm.value = { rating: 0, comment: '' }
  reviewDialogVisible.value = true
}

const handleUploadPhoto = async (row: any, type: string) => {
  photoOrderId.value = row.id
  photoType.value = type
  uploadFileList.value = []
  try {
    await refreshOrderPhotos(row.id)
  } catch (e) {
    console.error('Failed to fetch photos:', e)
    orderPhotos.value = []
  }
  photoDialogVisible.value = true
}

const handlePhotoFilesChange = (file: any, files: any) => {
  uploadFileList.value = files
}

const confirmUploadPhotos = async () => {
  if (uploadFileList.value.length === 0) {
    ElMessage.warning('Please select photos to upload')
    return
  }
  
  let uploaded = 0
  for (const file of uploadFileList.value) {
    const reader = new FileReader()
    reader.onload = async (e) => {
      const base64 = e.target?.result as string
      try {
        await orderPhotoApi.create({
          order_id: photoOrderId.value,
          photo_type: photoType.value,
          photo_url: base64
        })
        uploaded++
        if (uploaded === uploadFileList.value.length) {
          ElMessage.success(`${uploaded} photos uploaded successfully`)
          await refreshOrderPhotos(photoOrderId.value!)
          uploadFileList.value = []
        }
      } catch (error: any) {
        console.error('Upload error:', error)
        ElMessage.error(error?.response?.data?.detail || 'Upload failed')
      }
    }
    reader.readAsDataURL(file.raw)
  }
}

const handleDeletePhoto = async (photoId: number) => {
  try {
    await ElMessageBox.confirm('Are you sure you want to delete this photo?', 'Confirm', {
      confirmButtonText: 'Confirm',
      cancelButtonText: 'Cancel',
      type: 'warning'
    })
    await orderPhotoApi.delete(photoId)
    ElMessage.success('Photo deleted')
    await refreshOrderPhotos(photoOrderId.value!)
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Delete error:', error)
      ElMessage.error(error?.response?.data?.detail || 'Failed to delete')
    }
  }
}

const previewPhoto = (photo: any, photos: any[]) => {
  const urls = photos.map((p: any) => p.photo_url)
  previewUrls.value = urls
  const idx = photos.findIndex((p: any) => p === photo || p?.photo_url === photo?.photo_url)
  previewInitialIndex.value = idx >= 0 ? idx : 0
  previewUrl.value = photo.photo_url
  previewVisible.value = true
}

const handleStart = async (row: any) => {
  try {
    await serviceOrderApi.start(row.id)
    ElMessage.success('Work started')
    loadMyOrders()
  } catch (error: any) {
    console.error('Start error:', error)
    ElMessage.error(error?.response?.data?.detail || 'Operation failed')
  }
}

const handleComplete = async (row: any) => {
  try {
    await serviceOrderApi.complete(row.id)
    ElMessage.success('Completed')
    loadMyOrders()
  } catch (error: any) {
    console.error('Complete error:', error)
    ElMessage.error(error?.response?.data?.detail || 'Operation failed')
  }
}

const handlePageChange = (newPage: number) => {
  page.value = newPage
  loadMyOrders()
}

const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  page.value = 1
  loadMyOrders()
}

const getStatusType = (status: number) => {
  const map: Record<number, string> = {
    0: 'info', 1: 'warning', 2: 'primary', 3: 'warning', 4: 'success', 5: 'danger'
  }
  return map[status] || 'info'
}

/** Decode API rating: legacy 1–5 or encoded ×10 (e.g. 20 -> 2) */
const normalizeOrderRating = (rating: unknown): number => {
  const n = Number(rating)
  if (!Number.isFinite(n) || n <= 0) return 0
  return n > 5 ? Math.round((n / 10) * 10) / 10 : n
}

const parseRemarksContactAndNotes = (remarks: unknown): { contactLine: string; notes?: string } | null => {
  if (!remarks || typeof remarks !== 'string') return null
  const parts = remarks
    .split(' | ')
    .map((p) => p.trim())
    .filter(Boolean)
  if (parts.length < 3) return null
  if (!parts[0].startsWith('Contact:') || !parts[1].startsWith('Email:') || !parts[2].startsWith('Phone:')) return null

  const contactLine = `${parts[0]} | ${parts[1]} | ${parts[2]}`
  if (parts.length <= 3) return { contactLine }

  // Older backend: Contact/Email/Phone | <notes>
  // Newer backend: Contact/Email/Phone | Notes: <notes>
  const tail = parts.slice(3).join(' | ').trim()
  const notes = tail.startsWith('Notes:') ? tail.slice('Notes:'.length).trim() : tail
  return { contactLine, notes }
}

const parsedRemarks = computed(() => parseRemarksContactAndNotes(selectedOrder.value?.remarks))

type StarState = 'full' | 'half' | 'empty'

/** One entry per star (0–4): full / half / empty for display */
const getStarStates = (rating: unknown): StarState[] => {
  const raw = normalizeOrderRating(rating)
  const r = Math.round(raw * 10) / 10
  return Array.from({ length: 5 }, (_, i) => {
    const rem = r - i
    if (rem >= 1 - 1e-6) return 'full'
    if (rem >= 0.5 - 1e-6) return 'half'
    return 'empty'
  })
}

onMounted(() => {
  loadMyOrders()
  loadMyComplaints()
})
</script>

<template>
  <div class="my-orders-page">
    <div class="page-header">
      <h2>{{ pageTitle }}</h2>
      <p class="subtitle">{{ isCleaner ? 'View and manage your assigned cleaning tasks' : 'Track your service orders and progress' }}</p>
    </div>

    <el-card class="order-card">
      <el-table :data="myOrders" v-loading="loading" stripe>
        <el-table-column prop="order_no" label="Order No" width="160" />
        <el-table-column label="Service" width="140">
          <template #default="{ row }">
            <el-tag type="primary">{{ row.service_type }}</el-tag>
          </template>
        </el-table-column>
        
        <template v-if="isCleaner">
          <el-table-column label="Customer" min-width="150">
            <template #default="{ row }">
              <div class="staff-info">
                <span>{{ row.guest_name || '-' }}</span>
                <span v-if="row.guest_phone" class="staff-nation">{{ row.guest_phone }}</span>
              </div>
            </template>
          </el-table-column>
        </template>
        
        <template v-else>
          <el-table-column label="Username" min-width="150">
            <template #default="{ row }">
              <div class="staff-info">
                <span>{{
                  row.assigned_staff
                    || (row.assigned_staff_id ? `#${row.assigned_staff_id}` : '-')
                }}</span>
                <span v-if="row.staff_nationality" class="staff-nation">{{ row.staff_nationality }}</span>
              </div>
            </template>
          </el-table-column>
        </template>
        
        <el-table-column label="Property" width="120">
          <template #default="{ row }">
            <span v-if="row.requirement">{{ row.requirement.property_type }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Rooms" width="100">
          <template #default="{ row }">
            <span v-if="row.requirement">{{ row.requirement.bedroom }}B/{{ row.requirement.bathroom }}B</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusInfo(row.status).label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="isCustomer" label="Complaint" min-width="140">
          <template #default="{ row }">
            <div v-if="complaintForOrder(row)" class="complaint-cell">
              <el-tag :type="complaintStatusTagType(complaintForOrder(row).status)" size="small">
                {{ complaintForOrder(row).status }}
              </el-tag>
              <span
                v-if="complaintForOrder(row).evidence?.length"
                class="complaint-evidence-badge"
              >
                {{ complaintForOrder(row).evidence.length }} photo(s)
              </span>
            </div>
            <span v-else class="text-muted">—</span>
          </template>
        </el-table-column>
        <el-table-column label="Rating" width="120">
          <template #default="{ row }">
            <div v-if="normalizeOrderRating(row.rating) > 0" class="rating-display">
              <span
                class="stars-visual stars-visual--sm"
                role="img"
                :aria-label="`${normalizeOrderRating(row.rating)} out of 5 stars`"
              >
                <span v-for="(state, idx) in getStarStates(row.rating)" :key="idx" class="star-cell">
                  <span class="star-bg" aria-hidden="true">★</span>
                  <span
                    v-if="state !== 'empty'"
                    class="star-fg"
                    :class="{ 'star-fg--half': state === 'half' }"
                    aria-hidden="true"
                  >★</span>
                </span>
              </span>
              {{ normalizeOrderRating(row.rating) }}
            </div>
            <span v-else class="no-rating">Not rated</span>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="300" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleViewDetail(row)">View</el-button>
            <el-button
              v-if="isCustomer && [4, 5].includes(Number(row.status))"
              size="small"
              type="warning"
              @click="handlePayment(row)"
            >
              Pay
            </el-button>
            <el-button
              v-if="isCustomer && Number(row.status) === 6"
              size="small"
              type="primary"
              @click="handleOpenReview(row)"
            >
              Write Review
            </el-button>
            <el-button
              v-if="canFileComplaint(row)"
              size="small"
              type="warning"
              plain
              @click="openComplaintDialog(row)"
            >
              Complaint
            </el-button>
            <el-button 
              v-if="isCleaner && row.status === 1" 
              type="success" 
              size="small" 
              @click="handleStart(row)"
            >
              Start
            </el-button>
            <el-button 
              v-if="isCleaner && row.status === 2" 
              type="warning" 
              size="small" 
              @click="handleComplete(row)"
            >
              Complete
            </el-button>
            <el-button 
              v-if="isCleaner && row.status !== 4 && row.status !== 5" 
              size="small" 
              @click="handleUploadPhoto(row, 'before')"
            >
              Before
            </el-button>
            <el-button 
              v-if="isCleaner && row.status !== 4 && row.status !== 5" 
              size="small" 
              type="success"
              @click="handleUploadPhoto(row, 'after')"
            >
              After
            </el-button>
          </template>
        </el-table-column>
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
      
      <el-empty v-if="!loading && myOrders.length === 0" description="No orders yet" />
    </el-card>

    <el-dialog v-model="photoDialogVisible" :title="'Upload ' + (photoType === 'before' ? 'Before' : 'After') + ' Photo'" width="700px" destroy-on-close>
      <div class="existing-photos" v-if="orderPhotos.filter((p: any) => p.photo_type === photoType).length > 0">
        <p class="drag-hint">Drag photos to reorder (changes apply to all photos)</p>
        <draggable 
          v-model="sortedPhotos" 
          item-key="id" 
          class="photo-drag-container"
          @end="handleReorder"
        >
          <template #item="{ element }">
            <div class="existing-photo-item">
              <div class="drag-handle">
                <el-icon><Rank /></el-icon>
              </div>
              <img :src="element.photo_url" class="existing-photo-img" @click="previewPhoto(element, sortedPhotos)" />
              <div class="photo-actions">
                <el-button size="small" type="danger" @click="handleDeletePhoto(element.id)">Delete</el-button>
              </div>
            </div>
          </template>
        </draggable>
      </div>
      
      <div class="photo-upload-section">
        <el-tag :type="photoType === 'before' ? 'warning' : 'success'">
          {{ photoType === 'before' ? 'Before Cleaning' : 'After Cleaning' }}
        </el-tag>
        
        <el-upload
          class="photo-uploader"
          :auto-upload="false"
          :on-change="handlePhotoFilesChange"
          multiple
          accept="image/*"
        >
          <el-button type="primary">Select Photos</el-button>
        </el-upload>
        <div style="margin-top: 8px; color: #909399; font-size: 12px">Click to upload multiple photos</div>
      </div>
      
      <template #footer>
        <el-button @click="photoDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmUploadPhotos" :disabled="uploadFileList.length === 0">
          Upload {{ uploadFileList.length }} Photo(s)
        </el-button>
      </template>
    </el-dialog>

    <el-dialog title="Order Details" v-model="detailDialogVisible" width="920px" top="5vh" destroy-on-close>
      <div v-if="selectedOrder" class="order-detail">
        <div class="detail-header">
          <div class="order-title">
            <h3>Order #{{ selectedOrder.order_no }}</h3>
            <el-tag :type="getStatusType(selectedOrder.status)" size="large">
              {{ getStatusInfo(selectedOrder.status).label }}
            </el-tag>
          </div>
        </div>

        <div class="detail-grid">
          <div class="detail-section">
            <h4>Service Information</h4>
            <div class="detail-row">
              <span class="label">Service Type:</span>
              <span class="value">{{ selectedOrder.service_type }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Request Time:</span>
              <span class="value">{{ selectedOrder.request_time || selectedOrder.create_time }}</span>
            </div>
            <div v-if="selectedOrder.actual_start" class="detail-row">
              <span class="label">Started:</span>
              <span class="value">{{ selectedOrder.actual_start }}</span>
            </div>
            <div v-if="selectedOrder.actual_complete" class="detail-row">
              <span class="label">Completed:</span>
              <span class="value">{{ selectedOrder.actual_complete }}</span>
            </div>
          </div>

          <div class="detail-section" v-if="isCustomer && selectedOrder.payment">
            <h4>Payment</h4>
            <div class="detail-row">
              <span class="label">Amount:</span>
              <span class="value price">${{ Number(selectedOrder.payment.amount || 0).toFixed(2) }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Status:</span>
              <span class="value">
                <el-tag :type="selectedOrder.payment.status === 'completed' ? 'success' : 'warning'" size="small">
                  {{ selectedOrder.payment.status === 'completed' ? 'Paid' : 'Pending payment' }}
                </el-tag>
              </span>
            </div>
            <div v-if="selectedOrder.payment.payment_method" class="detail-row">
              <span class="label">Method:</span>
              <span class="value">{{ selectedOrder.payment.payment_method }}</span>
            </div>
            <div v-if="selectedOrder.payment.paid_at" class="detail-row">
              <span class="label">Paid at:</span>
              <span class="value">{{ selectedOrder.payment.paid_at }}</span>
            </div>
            <div v-if="selectedOrder.payment.transaction_id" class="detail-row">
              <span class="label">Transaction ID:</span>
              <span class="value">{{ selectedOrder.payment.transaction_id }}</span>
            </div>
            <div v-if="selectedOrder.payment.description" class="detail-row">
              <span class="label">Note:</span>
              <span class="value">{{ selectedOrder.payment.description }}</span>
            </div>
          </div>

          <div
            class="detail-section"
            v-if="selectedOrder.assigned_staff || selectedOrder.assigned_staff_id"
          >
            <h4>Assigned Cleaner</h4>
            <div class="staff-card">
              <div class="staff-avatar">
                {{
                  (selectedOrder.assigned_staff || 'U').charAt(0)
                }}
              </div>
              <div class="staff-details">
                <span class="staff-name">{{
                  selectedOrder.assigned_staff
                    || (selectedOrder.assigned_staff_id
                      ? `User #${selectedOrder.assigned_staff_id}`
                      : '-')
                }}</span>
                <div class="staff-meta">
                  <span v-if="selectedOrder.staff_nationality">🌍 {{ selectedOrder.staff_nationality }}</span>
                  <span v-if="selectedOrder.staff_languages">🗣️ {{ selectedOrder.staff_languages }}</span>
                </div>
                <div class="staff-contact">
                  <span v-if="selectedOrder.staff_email">📧 {{ selectedOrder.staff_email }}</span>
                  <span v-if="selectedOrder.staff_phone">📞 {{ selectedOrder.staff_phone }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="detail-section" v-if="selectedOrder.requirement">
            <h4>Requirement Details</h4>
            <div class="detail-row">
              <span class="label">Property:</span>
              <span class="value">{{ selectedOrder.requirement.property_type }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Rooms:</span>
              <span class="value">
                {{ selectedOrder.requirement.bedroom }} Bed / {{ selectedOrder.requirement.bathroom }} Bath
                <span v-if="selectedOrder.requirement.living_room">, {{ selectedOrder.requirement.living_room }} Living</span>
                <span v-if="selectedOrder.requirement.kitchen">, {{ selectedOrder.requirement.kitchen }} Kitchen</span>
              </span>
            </div>
            <div v-if="selectedOrder.requirement.square_footage" class="detail-row">
              <span class="label">Area:</span>
              <span class="value">{{ selectedOrder.requirement.square_footage }} sqft</span>
            </div>
            <div v-if="selectedOrder.requirement.budget" class="detail-row">
              <span class="label">Budget:</span>
              <span class="value price">${{ selectedOrder.requirement.budget }}</span>
            </div>
            <div v-if="selectedOrder.requirement.preferred_time" class="detail-row">
              <span class="label">Preferred Time:</span>
              <span class="value">{{ selectedOrder.requirement.preferred_time }}</span>
            </div>
            <div v-if="selectedOrder.requirement.description" class="detail-row">
              <span class="label">Description:</span>
              <span class="value">{{ selectedOrder.requirement.description }}</span>
            </div>
          </div>

          <div class="detail-section" v-if="normalizeOrderRating(selectedOrder.rating) > 0">
            <h4>Your Review</h4>
            <div class="rating-section">
              <div class="rating-stars">
                <span
                  class="stars-visual stars-visual--lg"
                  role="img"
                  :aria-label="`${normalizeOrderRating(selectedOrder.rating)} out of 5 stars`"
                >
                  <span v-for="(state, idx) in getStarStates(selectedOrder.rating)" :key="idx" class="star-cell">
                    <span class="star-bg" aria-hidden="true">★</span>
                    <span
                      v-if="state !== 'empty'"
                      class="star-fg"
                      :class="{ 'star-fg--half': state === 'half' }"
                      aria-hidden="true"
                    >★</span>
                  </span>
                </span>
              </div>
              <p v-if="selectedOrder.guest_feedback" class="feedback">{{ selectedOrder.guest_feedback }}</p>
            </div>
          </div>
          <div class="detail-section" v-if="selectedOrder.remarks">
            <h4>Remarks</h4>
            <template v-if="parsedRemarks?.contactLine">
              <p>{{ parsedRemarks.contactLine }}</p>
              <p v-if="parsedRemarks.notes" class="notes-line">
                Notes: {{ parsedRemarks.notes }}
              </p>
            </template>
            <template v-else>
              <p>{{ selectedOrder.remarks }}</p>
            </template>
          </div>
        </div>

        <!-- Full-width complaint + evidence (especially photos), outside narrow grid -->
        <div v-if="isCustomer && selectedComplaint" class="order-detail-complaint-panel">
          <div class="complaint-panel-header">
            <h4 class="complaint-panel-title">Complaint 投诉</h4>
            <el-tag :type="complaintStatusTagType(selectedComplaint.status)" size="default">
              {{ selectedComplaint.status }}
            </el-tag>
          </div>
          <div class="complaint-panel-body">
            <div class="complaint-panel-meta">
              <div v-if="selectedComplaint.create_time" class="complaint-meta-line">
                <span class="label">Submitted 提交时间</span>
                <span>{{ selectedComplaint.create_time }}</span>
              </div>
              <div class="complaint-meta-line">
                <span class="label">Title 标题</span>
                <span>{{ selectedComplaint.title }}</span>
              </div>
              <div v-if="selectedComplaint.description" class="complaint-meta-block">
                <span class="label">Description 说明</span>
                <p class="complaint-desc-text">{{ selectedComplaint.description }}</p>
              </div>
              <template v-if="selectedComplaint.resolution_type || selectedComplaint.resolution_amount != null">
                <div class="complaint-meta-line">
                  <span class="label">Resolution 处理结果</span>
                  <span>{{ formatComplaintResolution(selectedComplaint.resolution_type) }}</span>
                </div>
                <div v-if="selectedComplaint.resolution_amount != null" class="complaint-meta-line">
                  <span class="label">Amount 金额</span>
                  <span class="price">${{ Number(selectedComplaint.resolution_amount).toFixed(2) }}</span>
                </div>
                <div v-if="selectedComplaint.admin_note" class="complaint-meta-block">
                  <span class="label">Admin note 管理员备注</span>
                  <p class="complaint-desc-text">{{ selectedComplaint.admin_note }}</p>
                </div>
              </template>
            </div>

            <div class="complaint-evidence-panel">
              <h5 class="complaint-evidence-heading">
                Evidence photos 证据图片
                <span v-if="selectedComplaint.evidence?.length" class="evidence-count">
                  ({{ selectedComplaint.evidence.length }})
                </span>
              </h5>
              <p v-if="selectedComplaint.evidence?.length" class="complaint-evidence-tip text-muted">
                点击图片可放大浏览 · Tap an image to zoom
              </p>
              <p v-else class="complaint-evidence-empty text-muted">No photos uploaded 未上传图片</p>
              <div v-if="selectedComplaint.evidence?.length" class="complaint-evidence-grid-large">
                <el-image
                  v-for="(ev, evIdx) in selectedComplaint.evidence"
                  :key="ev.id ?? evIdx"
                  class="complaint-evidence-elimage"
                  :src="ev.photo_url"
                  :preview-src-list="complaintPreviewUrlList(selectedComplaint)"
                  :initial-index="evIdx"
                  fit="cover"
                  preview-teleported
                >
                  <template #error>
                    <div class="complaint-image-error">Load failed 加载失败</div>
                  </template>
                </el-image>
              </div>
            </div>
          </div>
        </div>

        <div v-if="detailPhotos.length > 0" class="photos-section">
          <h4>Photos Comparison</h4>
          <div class="comparison-container">
            <div class="comparison-row">
              <div class="comparison-label">Before Cleaning</div>
              <div class="comparison-photos">
                <div v-for="photo in detailPhotos.filter((p: any) => p.photo_type === 'before')" :key="photo.id" class="photo-item" @click="previewPhoto(photo, detailPhotos)">
                  <img :src="photo.photo_url" class="photo-img" />
                </div>
                <div v-if="detailPhotos.filter((p: any) => p.photo_type === 'before').length === 0" class="no-photo">No photos</div>
              </div>
            </div>
            <div class="comparison-divider"></div>
            <div class="comparison-row">
              <div class="comparison-label">After Cleaning</div>
              <div class="comparison-photos">
                <div v-for="photo in detailPhotos.filter((p: any) => p.photo_type === 'after')" :key="photo.id" class="photo-item" @click="previewPhoto(photo, detailPhotos)">
                  <img :src="photo.photo_url" class="photo-img" />
                </div>
                <div v-if="detailPhotos.filter((p: any) => p.photo_type === 'after').length === 0" class="no-photo">No photos</div>
              </div>
            </div>
          </div>
          <div class="photo-hint">Click on any photo to view and compare</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">Close</el-button>
        <el-button
          v-if="selectedOrder && canFileComplaint(selectedOrder)"
          type="warning"
          @click="openComplaintDialog(selectedOrder)"
        >
          File complaint
        </el-button>
        <el-button
          v-if="(Number(selectedOrder?.status) === 6 && isCustomer)"
          type="primary"
          @click="reviewDialogVisible = true"
        >
          Write Review
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="complaintDialogVisible" title="File a complaint" width="560px" destroy-on-close>
      <p class="complaint-hint">
        You may submit one complaint per order within 15 days after service completion. Attach photos as evidence
        (optional).
      </p>
      <el-form label-position="top">
        <el-form-item label="Title" required>
          <el-input v-model="complaintForm.title" maxlength="200" show-word-limit placeholder="Short summary" />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="complaintForm.description" type="textarea" :rows="4" placeholder="What went wrong?" />
        </el-form-item>
        <el-form-item label="Evidence images (optional)">
          <el-upload
            :auto-upload="false"
            :on-change="handleComplaintFilesChange"
            multiple
            accept="image/*"
          >
            <el-button type="primary">Select images</el-button>
          </el-upload>
          <span class="text-muted" style="margin-left: 8px">{{ complaintUploadList.length }} file(s)</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="complaintDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitComplaint">Submit</el-button>
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

    <el-image-viewer
      v-if="previewVisible"
      :url-list="previewUrls"
      :initial-index="previewInitialIndex"
      @close="previewVisible = false"
    />
  </div>
</template>

<style scoped>
.my-orders-page {
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

.text-muted {
  color: #909399;
  font-size: 13px;
}

.complaint-hint {
  color: #606266;
  font-size: 13px;
  margin: 0 0 12px 0;
}

.complaint-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.complaint-evidence-badge {
  font-size: 12px;
  color: #909399;
}

.complaint-desc-text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  max-width: 100%;
}

/* Order Details — complaint + evidence (full width below grid) */
.order-detail-complaint-panel {
  margin-top: 20px;
  padding: 18px;
  background: linear-gradient(180deg, #f5f9ff 0%, #ffffff 48%);
  border: 1px solid #c6e2ff;
  border-radius: 12px;
}

.complaint-panel-header {
  display: flex;
  align-items: center;
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

.order-card {
  margin-top: 16px;
}

.staff-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.staff-nation {
  font-size: 11px;
  color: #909399;
}

.rating-display {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* Half-star: gray base + orange overlay clipped to 50% or 100% */
.stars-visual {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  line-height: 1;
}

.stars-visual--sm {
  font-size: 15px;
}

.stars-visual--lg {
  font-size: 26px;
}

.star-cell {
  position: relative;
  display: inline-block;
  width: 1em;
  height: 1em;
  line-height: 1;
  flex-shrink: 0;
}

.star-bg {
  display: block;
  color: #e4e7ed;
}

.star-fg {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  overflow: hidden;
  color: #ff9800;
  white-space: nowrap;
  pointer-events: none;
}

.star-fg--half {
  width: 50%;
}

.no-rating {
  color: #c0c4cc;
  font-size: 12px;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.order-detail {
  padding: 10px 0;
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

/* Remarks block in detail dialog */
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
  flex-direction: column;
  gap: 2px;
  font-size: 13px;
  line-height: 1.45;
  color: #8b919b;
}

.rating-section {
  text-align: center;
}

.rating-stars {
  line-height: 1.2;
}

.feedback {
  margin: 12px 0 0 0;
  color: #606266;
  font-style: italic;
  font-size: 14px;
  line-height: 1.6;
}

.photos-section {
  margin-top: 20px;
}

.photos-section h4 {
  margin: 0 0 14px 0;
  color: #303133;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.01em;
  line-height: 1.35;
}

.comparison-container {
  display: flex;
  gap: 16px;
  align-items: stretch;
}

.comparison-row {
  flex: 1;
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
}

.comparison-label {
  font-weight: 600;
  font-size: 13px;
  letter-spacing: 0.02em;
  color: #303133;
  margin-bottom: 10px;
  text-align: center;
  padding: 8px;
  background: #e4e7ed;
  border-radius: 4px;
}

.comparison-photos {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  min-height: 100px;
}

.comparison-divider {
  width: 4px;
  background: linear-gradient(to bottom, #409eff, #67c23a);
  border-radius: 2px;
}

.photo-hint {
  text-align: center;
  color: #8b919b;
  font-size: 13px;
  line-height: 1.45;
  margin-top: 12px;
}

.photo-tabs {
  display: flex;
  gap: 20px;
}

.photo-group {
  flex: 1;
}

.photo-label {
  display: block;
  font-weight: 500;
  margin-bottom: 8px;
  color: #606266;
}

.photo-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.photo-item {
  cursor: pointer;
  position: relative;
}

.photo-item:hover .photo-img {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.photo-img {
  width: 150px;
  height: 150px;
  object-fit: cover;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.photo-img:hover {
  opacity: 0.9;
}

.no-photo {
  color: #c0c4cc;
  font-style: italic;
}

.photo-upload-section {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.photo-uploader {
  margin-top: 10px;
}

.detail-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
}

.price {
  color: #ff6b6b;
  font-weight: bold;
}

.drag-hint {
  color: #909399;
  font-size: 12px;
  margin: 0 0 10px 0;
}

.photo-drag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.existing-photo-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  transition: all 0.3s;
}

.existing-photo-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.drag-handle {
  cursor: grab;
  color: #909399;
  font-size: 20px;
  padding: 4px;
}

.drag-handle:active {
  cursor: grabbing;
}

.existing-photo-img {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 4px;
  cursor: pointer;
}

.photo-actions {
  margin-top: 4px;
}

.existing-photos {
  margin-bottom: 20px;
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
