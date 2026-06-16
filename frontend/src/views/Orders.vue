<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { serviceOrderApi, roomApi, userApi, serviceTypeApi, walletApi, orderPhotoApi } from '@/api'
import { ElMessage, ElMessageBox, ElImageViewer } from 'element-plus'
import { useUserStore } from '@/stores/user'
import draggable from 'vuedraggable'

// User store instance
const userStore = useUserStore()
// Loading state for data fetching
const loading = ref(false)
// List of service orders
const orderList = ref([])
// Total count of orders
const total = ref(0)
// Pagination current page
const currentPage = ref(1)
// Pagination page size
const pageSize = ref(10)

// Computed user role list
const userRoles = computed(() => userStore.userInfo?.roles || [userStore.userInfo?.role || 'guest'])
// Computed whether the user can create orders
const canCreateOrder = computed(() => userRoles.value.some(r => ['admin', 'guest'].includes(r)))
// Computed whether the user can assign orders
const canAssign = computed(() => userRoles.value.includes('admin'))
// Computed whether the user is a cleaner
const isCleaner = computed(() => userRoles.value.includes('cleaner'))
// Computed whether the user is a guest
const isGuestUser = computed(() => userRoles.value.includes('guest'))
// Computed whether the dialog is in detail mode
const isDetailMode = computed(() => dialogTitle.value === 'Order Detail')

const statusOptions = [
  { value: 0, label: 'Pending' },
  { value: 1, label: 'Assigned' },
  { value: 2, label: 'In Progress' },
  { value: 3, label: 'Pending Check' },
  { value: 4, label: 'Completed' },
  { value: 5, label: 'Cancelled' }
]

// Filter options for order list
const filters = ref({
  status: null
})

// Dialog visibility for create/detail
const dialogVisible = ref(false)
// Dialog title
const dialogTitle = ref('')
// Dialog visibility for assign cleaner
const assignDialogVisible = ref(false)
// Order ID being assigned
const assignOrderId = ref(null)
// List of staff available for assignment
const staffList = ref([])
// Selected staff ID for assignment
const selectedStaffId = ref(null)
// Dialog visibility for rating
const rateDialogVisible = ref(false)
// Order ID being rated
const rateOrderId = ref(null)
// Rating form data
const rateForm = ref({ rating: 5, comment: '' })

// Dialog visibility for photo upload
const photoDialogVisible = ref(false)
// Order ID for photo operations
const photoOrderId = ref(null)
// Photo type (before/after)
const photoType = ref('before')
// Photo URL input
const photoUrl = ref('')
// List of order photos
const orderPhotos = ref([])

// Dialog visibility for payment
const paymentDialogVisible = ref(false)
// Order ID for payment
const paymentOrderId = ref(null)
// List of paid order IDs
const paidOrders = ref<number[]>([])

// Check if a given order has been paid
const isOrderPaid = (orderId: number) => {
  return paidOrders.value.includes(orderId)
}

// Fetch paid orders from wallet transactions and cache in localStorage
const fetchPaidOrders = async () => {
  try {
    const res = await walletApi.transactions()
    const paymentOrders = res
      ?.filter((t: any) => t.type === 'payment' && t.status === 'completed')
      ?.map((t: any) => t.order_id) || []
    paidOrders.value = [...new Set([...paidOrders.value, ...paymentOrders])]
    localStorage.setItem('paid_orders', JSON.stringify(paidOrders.value))
  } catch (e) {
    console.error('Failed to fetch transactions')
  }
}
// Payment amount for the current payment
const paymentAmount = ref(0)
// Photos displayed in order detail dialog
const detailPhotos = ref<any[]>([])
// File list for photo upload
const uploadFileList = ref<any[]>([])

// List of service types
const serviceTypes = ref([])
// List of rooms
const rooms = ref([])
// Form data for creating/editing orders
const formData = ref({
  room_id: null,
  service_type_id: 1,
  priority: 0,
  request_time: '',
  remarks: ''
})

// Fetch available service types from API
const fetchServiceTypes = async () => {
  try {
    serviceTypes.value = await serviceTypeApi.list()
  } catch (e) {
    console.error('Failed to fetch service types:', e)
  }
}

// Fetch available rooms from API
const fetchRooms = async () => {
  try {
    rooms.value = await roomApi.list()
  } catch (e) {
    console.error('Failed to fetch rooms:', e)
  }
}

// Fetch paginated order list from API
const fetchOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      filters: filters.value.status !== null ? { status: filters.value.status } : {}
    }
    const res = await serviceOrderApi.paginated(params)
    orderList.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('Failed to fetch orders:', error)
  } finally {
    loading.value = false
  }
}

// Open dialog to create a new order
const handleAdd = async () => {
  await fetchServiceTypes()
  await fetchRooms()
  dialogTitle.value = 'Create Order'
  formData.value = { room_id: null, service_type_id: 1, priority: 0, request_time: new Date().toISOString(), remarks: '' }
  dialogVisible.value = true
}

// Submit the create-order form
const handleSubmit = async () => {
  try {
    await serviceOrderApi.create(formData.value)
    ElMessage.success('Created successfully')
    dialogVisible.value = false
    fetchOrders()
  } catch (error) {
    ElMessage.error('Failed to create')
  }
}

// Open assign dialog and load available cleaners
const handleAssign = async (row: any) => {
  try {
    const staff = await userApi.getByRole('cleaner')
    staffList.value = staff || []
    if (!staffList.value || staffList.value.length === 0) {
      ElMessage.warning('No available cleaners')
      return
    }
    assignOrderId.value = row.order_id
    selectedStaffId.value = staffList.value[0]?.id || null
    assignDialogVisible.value = true
  } catch (error) {
    console.error('Failed to fetch cleaners:', error)
    ElMessage.error('Failed to load cleaners')
  }
}

// Confirm assignment of an order to the selected cleaner
const confirmAssign = async () => {
  if (!selectedStaffId.value) {
    ElMessage.warning('Please select a cleaner')
    return
  }
  try {
    await serviceOrderApi.assign(assignOrderId.value, selectedStaffId.value)
    const staff = staffList.value.find((s: any) => s.id === selectedStaffId.value)
    ElMessage.success('Assigned to ' + (staff?.full_name || 'staff'))
    assignDialogVisible.value = false
    fetchOrders()
  } catch (error: any) {
    console.error('Assign error:', error)
    ElMessage.error(error?.response?.data?.detail || 'Failed to assign')
  }
}

// Start work on an order (change status to In Progress)
const handleStart = async (row: any) => {
  try {
    await serviceOrderApi.start(row.order_id)
    ElMessage.success('Work started')
    fetchOrders()
  } catch (error: any) {
    console.error('Start error:', error)
    ElMessage.error(error?.response?.data?.detail || 'Operation failed')
  }
}

// Mark an order as completed
const handleComplete = async (row: any) => {
  try {
    await serviceOrderApi.complete(row.order_id)
    ElMessage.success('Completed')
    fetchOrders()
  } catch (error: any) {
    console.error('Complete error:', error)
    ElMessage.error(error?.response?.data?.detail || 'Operation failed')
  }
}

// Cancel an order with a cancellation reason
const handleCancel = async (row: any) => {
  try {
    await ElMessageBox.prompt('Please enter cancellation reason:', 'Cancel Order', {
      confirmButtonText: 'Confirm',
      cancelButtonText: 'Cancel'
    })
    .then(async ({ value }) => {
      await serviceOrderApi.cancel(row.order_id, value)
      ElMessage.success('Order cancelled')
      fetchOrders()
    })
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Cancel error:', error)
      ElMessage.error(error?.response?.data?.detail || 'Operation failed')
    }
  }
}

// Open the rating dialog for a completed order
const handleRate = (row: any) => {
  rateOrderId.value = row.order_id
  rateForm.value = { rating: row.rating || 5, comment: row.guest_feedback || '' }
  rateDialogVisible.value = true
}

// Submit the rating for an order
const confirmRate = async () => {
  try {
    await serviceOrderApi.rate(rateOrderId.value, rateForm.value.rating, rateForm.value.comment)
    ElMessage.success('Thank you for your feedback!')
    rateDialogVisible.value = false
    fetchOrders()
  } catch (error: any) {
    console.error('Rate error:', error)
    ElMessage.error(error?.response?.data?.detail || 'Operation failed')
  }
}

// Open photo upload dialog for before/after photos
const handleUploadPhoto = async (row: any, type: string) => {
  photoOrderId.value = row.order_id
  photoType.value = type
  photoUrl.value = ''
  try {
    const res = await orderPhotoApi.getByOrder(row.order_id)
    orderPhotos.value = res || []
  } catch (e) {
    console.error('Failed to fetch photos:', e)
    orderPhotos.value = []
  }
  photoDialogVisible.value = true
}

// Confirm uploading a single photo
const confirmUploadPhoto = async () => {
  if (!photoUrl.value) {
    ElMessage.warning('Please upload a photo')
    return
  }
  try {
    await orderPhotoApi.create({
      order_id: photoOrderId.value,
      photo_type: photoType.value,
      photo_url: photoUrl.value
    })
    ElMessage.success('Photo uploaded successfully')
    photoDialogVisible.value = false
  } catch (error: any) {
    console.error('Upload error:', error)
    ElMessage.error(error?.response?.data?.detail || 'Upload failed')
  }
}

// Handle photo file selection change
const handlePhotoFilesChange = (file: any, files: any) => {
  uploadFileList.value = files
}

// Upload multiple selected photos as base64
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
          photoDialogVisible.value = false
          uploadFileList.value = []
          const res = await orderPhotoApi.getByOrder(photoOrderId.value)
          orderPhotos.value = res || []
        }
      } catch (error: any) {
        console.error('Upload error:', error)
        ElMessage.error(error?.response?.data?.detail || 'Upload failed')
      }
    }
    reader.readAsDataURL(file.raw)
  }
}

// Delete a photo after confirmation
const handleDeletePhoto = async (photoId: number) => {
  try {
    await ElMessageBox.confirm('Are you sure you want to delete this photo?', 'Confirm', {
      confirmButtonText: 'Confirm',
      cancelButtonText: 'Cancel',
      type: 'warning'
    })
    await orderPhotoApi.delete(photoId)
    ElMessage.success('Photo deleted')
    const res = await orderPhotoApi.getByOrder(photoOrderId.value)
    orderPhotos.value = res || []
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Delete error:', error)
      ElMessage.error(error?.response?.data?.detail || 'Failed to delete')
    }
  }
}

// Save the reordered photo sequence
const handleReorder = async () => {
  const photoIds = orderPhotos.value.map((p: any) => p.id)
  try {
    await orderPhotoApi.reorder(photoIds)
  } catch (error) {
    console.error('Failed to save order:', error)
  }
}

// Image preview dialog visibility
const previewVisible = ref(false)
// Image preview URL
const previewUrl = ref('')
// List of image URLs for preview
const previewUrls = ref<string[]>([])

// Preview a photo in the image viewer
const previewPhoto = (url: string, photos: any[]) => {
  previewUrls.value = photos.map((p: any) => p.photo_url)
  previewUrl.value = url
  previewVisible.value = true
}

// Open the payment dialog for an order
const handlePayment = async (row: any) => {
  paymentOrderId.value = row.order_id
  const serviceType = serviceTypes.value.find(
    (s: any) => (s.id ?? s.type_id) === row.service_type_id
  )
  paymentAmount.value = serviceType?.price || 0
  paymentDialogVisible.value = true
}

// Confirm and process payment for the order
const confirmPayment = async () => {
  try {
    await walletApi.pay(paymentOrderId.value)
    ElMessage.success('Payment successful')
    paymentDialogVisible.value = false
    fetchOrders()
    paidOrders.value.push(paymentOrderId.value)
    localStorage.setItem('paid_orders', JSON.stringify(paidOrders.value))
    localStorage.setItem('wallet_updated', Date.now().toString())
  } catch (error: any) {
    console.error('Payment error:', error)
    ElMessage.error(error?.response?.data?.detail || 'Payment failed')
  }
}

// Open the order detail dialog and load photos
const handleDetail = async (row: any) => {
  formData.value = {
    room_id: row.room_id,
    service_type_id: row.service_type_id,
    priority: row.priority,
    request_time: row.request_time,
    remarks: row.remarks || ''
  }
  
  try {
    const res = await orderPhotoApi.getByOrder(row.order_id)
    detailPhotos.value = res || []
  } catch (e) {
    console.error('Failed to fetch photos:', e)
    detailPhotos.value = []
  }
  
  dialogTitle.value = 'Order Detail'
  dialogVisible.value = true
}

// Apply filters and refresh the order list
const handleSearch = () => {
  currentPage.value = 1
  fetchOrders()
}

// Reset filters to defaults and refresh
const handleReset = () => {
  filters.value = { status: null }
  currentPage.value = 1
  fetchOrders()
}

// Handle pagination page change
const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchOrders()
}

// Get the Element tag type for a given status code
const getStatusType = (status: number) => {
  const map: Record<number, string> = {
    0: 'info', 1: 'warning', 2: 'primary', 3: 'warning', 4: 'success', 5: 'danger'
  }
  return map[status] || 'info'
}

// Format a date string for display
const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('en-US')
}

// Lifecycle hook: fetch orders, service types, and restore paid orders on mount
onMounted(() => {
  fetchOrders()
  fetchServiceTypes()
  fetchPaidOrders()
  const storedPaidOrders = localStorage.getItem('paid_orders')
  if (storedPaidOrders) {
    paidOrders.value = JSON.parse(storedPaidOrders)
  }
})
</script>

<template>
  <div class="orders-page">
    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="Status">
          <el-select v-model="filters.status" placeholder="Select status" clearable style="width: 150px">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleReset">Reset</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="hover" style="margin-top: 16px">
        <template #header>
          <div class="card-header">
            <span>Service Orders</span>
            <el-button v-if="canCreateOrder" type="primary" @click="handleAdd">Create Order</el-button>
          </div>
        </template>

      <el-table :data="orderList" v-loading="loading" style="width: 100%">
        <el-table-column prop="order_no" label="Order No" width="150" />
        <el-table-column prop="room_id" label="Room ID" width="80" />
        <el-table-column prop="guest_id" label="Guest ID" width="80" />
        <el-table-column prop="assigned_staff_id" label="Assigned To" width="150">
          <template #default="{ row }">
            <span v-if="row.assigned_staff_name">{{ row.assigned_staff_name }}</span>
            <span v-else class="text-gray">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ statusOptions.find(s => s.value === row.status)?.label || 'Unknown' }}
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
        <el-table-column prop="request_time" label="Request Time" width="180">
          <template #default="{ row }">
            {{ formatDate(row.request_time) }}
          </template>
        </el-table-column>
        <el-table-column label="Action" width="420" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleDetail(row)">Detail</el-button>
            <el-button v-if="canAssign && row.status === 0" type="primary" link @click="handleAssign(row)">Assign</el-button>
            <el-button v-if="row.status === 1 && isCleaner" type="warning" link @click="handleStart(row)">Start</el-button>
            <el-button v-if="row.status === 1 && isCleaner" type="info" link @click="handleUploadPhoto(row, 'before')">Before Photo</el-button>
            <el-button v-if="row.status === 2 && isCleaner" type="success" link @click="handleComplete(row)">Complete</el-button>
            <el-button v-if="row.status === 2 && isCleaner" type="info" link @click="handleUploadPhoto(row, 'after')">After Photo</el-button>
            <el-button v-if="row.status === 4 && isGuestUser && !isOrderPaid(row.order_id)" type="danger" link @click="handlePayment(row)">Pay</el-button>
            <el-button v-if="row.status < 4 && isGuestUser" type="danger" link @click="handleCancel(row)">Cancel</el-button>
            <el-button v-if="row.status === 4 && isGuestUser && !row.rating" type="info" link @click="handleRate(row)">Rate</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close>
      <el-form :model="formData" label-width="100px" :disabled="isDetailMode">
        <el-form-item label="Room">
          <el-select v-model="formData.room_id" placeholder="Select room" style="width: 100%">
            <el-option
              v-for="room in rooms"
              :key="room.room_id"
              :label="room.room_number + ' (' + room.room_type + ')'"
              :value="room.room_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Service Type">
          <el-select v-model="formData.service_type_id" style="width: 100%">
            <el-option
              v-for="st in serviceTypes"
              :key="st.id ?? st.type_id"
              :label="st.type_name + ' - $' + st.price"
              :value="st.id ?? st.type_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Priority">
          <el-radio-group v-model="formData.priority">
            <el-radio :value="0">Normal</el-radio>
            <el-radio :value="1">Urgent</el-radio>
            <el-radio :value="2">Emergency</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Remarks">
          <el-input v-model="formData.remarks" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      
      <div v-if="detailPhotos.length > 0" class="detail-photos">
        <div class="photo-section">
          <div class="photo-title">Before Cleaning</div>
          <div class="photo-grid">
            <div v-for="photo in detailPhotos.filter((p: any) => p.photo_type === 'before')" :key="photo.id" class="photo-item" @click="previewPhoto(photo.photo_url, detailPhotos.filter((p: any) => p.photo_type === 'before'))">
              <img :src="photo.photo_url" class="photo-img" />
            </div>
            <div v-if="detailPhotos.filter((p: any) => p.photo_type === 'before').length === 0" class="no-photo">No photos</div>
          </div>
        </div>
        <div class="photo-section">
          <div class="photo-title">After Cleaning</div>
          <div class="photo-grid">
            <div v-for="photo in detailPhotos.filter((p: any) => p.photo_type === 'after')" :key="photo.id" class="photo-item" @click="previewPhoto(photo.photo_url, detailPhotos.filter((p: any) => p.photo_type === 'after'))">
              <img :src="photo.photo_url" class="photo-img" />
            </div>
            <div v-if="detailPhotos.filter((p: any) => p.photo_type === 'after').length === 0" class="no-photo">No photos</div>
          </div>
        </div>
      </div>
      <div v-else class="no-photos">No photos uploaded yet</div>
      
      <template #footer>
        <el-button @click="dialogVisible = false">Close</el-button>
        <el-button v-if="!isDetailMode" type="primary" @click="handleSubmit">Confirm</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="assignDialogVisible" title="Assign Cleaner" width="400px" destroy-on-close>
      <el-form label-width="80px">
        <el-form-item label="Select Cleaner">
          <el-select v-model="selectedStaffId" placeholder="Select a cleaner" style="width: 100%">
            <el-option
              v-for="staff in staffList"
              :key="staff.id"
              :label="staff.full_name + ' (' + staff.username + ')'"
              :value="staff.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmAssign">Confirm</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="rateDialogVisible" title="Rate Service" width="400px" destroy-on-close>
      <el-form label-width="80px">
        <el-form-item label="Rating">
          <el-rate v-model="rateForm.rating" :max="5" show-text :texts="['Terrible', 'Poor', 'Average', 'Good', 'Excellent']" />
        </el-form-item>
        <el-form-item label="Comment">
          <el-input v-model="rateForm.comment" type="textarea" :rows="3" placeholder="Share your experience..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rateDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmRate">Submit</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="photoDialogVisible" :title="'Upload ' + (photoType === 'before' ? 'Before' : 'After') + ' Photo'" width="600px" destroy-on-close>
      <div v-if="orderPhotos.length > 0" style="margin-bottom: 16px">
        <div style="font-weight: 500; margin-bottom: 8px">Existing Photos:</div>
        <draggable 
          v-model="orderPhotos" 
          item-key="id"
          class="existing-photos"
          @end="handleReorder"
        >
          <template #item="{ element }">
            <div v-if="element.photo_type === photoType" class="existing-photo-item">
              <img :src="element.photo_url" class="existing-photo-img" @click="previewPhoto(element.photo_url, orderPhotos.filter((p: any) => p.photo_type === photoType))" />
              <div class="photo-actions">
                <el-button size="small" type="danger" circle @click="handleDeletePhoto(element.id)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </template>
        </draggable>
      </div>
      <el-form label-width="100px">
        <el-form-item label="Photo Type">
          <el-tag :type="photoType === 'before' ? 'warning' : 'success'">
            {{ photoType === 'before' ? 'Before Cleaning' : 'After Cleaning' }}
          </el-tag>
        </el-form-item>
        <el-form-item label="Upload Photos">
          <el-upload
            class="photo-uploader"
            :auto-upload="false"
            :on-change="handlePhotoFilesChange"
            :file-list="uploadFileList"
            multiple
            list-type="picture-card"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div style="margin-top: 8px; color: #909399; font-size: 12px">Click to upload multiple photos</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="photoDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmUploadPhotos" :disabled="uploadFileList.length === 0">Upload {{ uploadFileList.length }} Photo(s)</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="paymentDialogVisible" title="Order Payment" width="400px" destroy-on-close>
      <el-result icon="warning" title="Confirm Payment">
        <template #sub-title>
          <div style="font-size: 24px; margin: 20px 0">
            Amount: <span style="color: #67c23a; font-weight: bold">${{ paymentAmount }}</span>
          </div>
          <div>Please confirm to pay for this service order</div>
        </template>
      </el-result>
      <template #footer>
        <el-button @click="paymentDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmPayment">Confirm Payment</el-button>
      </template>
    </el-dialog>

    <el-image-viewer
      v-if="previewVisible"
      :url-list="previewUrls"
      @close="previewVisible = false"
    />
  </div>
</template>

<style scoped>
.filter-card :deep(.el-card__body) {
  padding-bottom: 0;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
.text-gray {
  color: #909399;
}
.photo-item {
  cursor: pointer;
  padding: 8px;
  margin-bottom: 8px;
  background: #f5f7fa;
  border-radius: 4px;
}
.detail-photos {
  margin-top: 20px;
  border-top: 1px solid #ebeef5;
  padding-top: 16px;
}
.photo-section {
  margin-bottom: 16px;
}
.photo-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: #303133;
}
.photo-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.photo-img {
  width: 120px;
  height: 90px;
  object-fit: cover;
  border-radius: 8px;
  cursor: pointer;
}
.photo-img:hover {
  transform: scale(1.05);
  transition: transform 0.2s;
}
.no-photo, .no-photos {
  color: #909399;
  font-size: 14px;
  padding: 16px;
  text-align: center;
  background: #f5f7fa;
  border-radius: 8px;
  width: 100%;
}
.existing-photos {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.existing-photo-item {
  text-align: center;
  position: relative;
}
.existing-photo-img {
  width: 100px;
  height: 75px;
  object-fit: cover;
  border-radius: 8px;
  cursor: pointer;
  border: 2px solid #ebeef5;
}
.existing-photo-img:hover {
  border-color: #409eff;
}
.photo-actions {
  margin-top: 4px;
}
.photo-label {
  font-size: 12px;
  color: #606266;
  margin-top: 4px;
}
.photo-uploader {
  width: 150px;
  height: 150px;
  border: 1px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
.photo-uploader:hover {
  border-color: #409eff;
}
.photo-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.upload-icon {
  font-size: 28px;
  color: #8c939d;
}
</style>
