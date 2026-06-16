<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { portalApi } from '@/api'
import { transactionApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

// User store for role/permission information
const userStore = useUserStore()
// Loading state for the data table
const loading = ref(false)

// List of customer requirements
const requirements = ref<any[]>([])
// Total number of requirements matching the query
const total = ref(0)
// Current pagination page
const page = ref(1)
// Number of items per page
const pageSize = ref(20)

// Filter criteria for the requirements list
const filters = ref({
  requirement_id: '' as string,
  status: null as number | null,
  property_type: '',
  service_type: '',
  // Customer-only: scope of rows you created (not cleaner assignments)
  portal_scope: 'all' as 'all' | 'published' | 'draft'
})

// Array of role names for the current user
const userRoles = computed(() => userStore.userInfo?.roles || [userStore.userInfo?.role || 'guest'])
// Whether the current user has a guest/customer role
const isGuest = computed(() => userRoles.value.some(r => ['guest', 'customer', 'user'].includes(r.toLowerCase())))

// The current customer's user ID
const userId = computed(() => userStore.userInfo?.id || userStore.userInfo?.userId)

// Dialog visibility for cleaner assignment
const showAssignDialog = ref(false)
// The requirement currently being assigned
const selectedRequirement = ref<any>(null)
// The selected cleaner ID for assignment
const selectedCleanerId = ref<number | null>(null)
// Loading state during assignment submission
const assignLoading = ref(false)

// Dialog visibility for cleaner profile view
const showCleanerProfile = ref(false)
// The selected cleaner profile data
const selectedCleanerProfile = ref<any>(null)

// Maps requirement status numbers to display labels
const statusTextMap: Record<number, string> = {
  0: 'Pending',
  1: 'Assigned',
  2: 'In Progress',
  3: 'Completed',
  4: 'Cancelled'
}

// Options for requirement status filter
const statusOptions = [
  { value: 0, label: 'Pending' },
  { value: 1, label: 'Assigned' },
  { value: 2, label: 'In Progress' },
  { value: 3, label: 'Completed' },
  { value: 4, label: 'Cancelled' }
]

// Available property type options
const propertyTypes = ['House', 'Apartment', 'Villa', 'Condo', 'Townhouse', 'Studio']
// Fallback service types when portal data is not available
const serviceTypesFallback = [
  'Standard Cleaning',
  'Deep Cleaning',
  'Move-in Cleaning',
  'Move-out Cleaning',
  'Post-Construction'
]
// Service types loaded from the portal API
const serviceTypesFromPortal = ref<any[]>([])

// Computed list of service type options (from portal or fallback)
const serviceTypeOptions = computed(() => {
  if (serviceTypesFromPortal.value.length) {
    return serviceTypesFromPortal.value.map((s: any) => s.type_name).filter(Boolean)
  }
  return serviceTypesFallback
})

// Dialog visibility for create/edit requirement form
const showCreateDialog = ref(false)
// ID of the requirement being edited, null when creating
const editingRequirementId = ref<number | null>(null)
// Loading state during create/update submission
const createSubmitting = ref(false)
// Form data for creating/editing a requirement
const createForm = ref({
  guest_name: '',
  guest_phone: '',
  guest_email: '',
  guest_address: '',
  property_type: 'House',
  bedroom: 2,
  bathroom: 1,
  living_room: 1,
  kitchen: 1,
  lawn: 0,
  car_space: 0,
  square_footage: null as number | null,
  service_type_name: '',
  preferred_time: '' as string,
  budget: null as number | null,
  description: '',
  publish_to_portal: true
})

// Fetch available service types from the portal API
const loadServiceTypes = async () => {
  try {
    const res = await portalApi.getServices()
    serviceTypesFromPortal.value = Array.isArray(res) ? res : []
  } catch {
    serviceTypesFromPortal.value = []
  }
}

// Open the dialog for creating a new requirement, pre-filling user info
const openCreateRequirement = () => {
  const u = userStore.userInfo as any
  createForm.value = {
    guest_name: u?.full_name || u?.username || '',
    guest_phone: u?.phone || '',
    guest_email: u?.email || '',
    guest_address: u?.address || '',
    property_type: 'House',
    bedroom: 2,
    bathroom: 1,
    living_room: 1,
    kitchen: 1,
    lawn: 0,
    car_space: 0,
    square_footage: null,
    service_type_name: serviceTypeOptions.value[0] || '',
    preferred_time: '',
    budget: null,
    description: '',
    publish_to_portal: true
  }
  showCreateDialog.value = true
}

// Reset editing requirement ID when the dialog is closed
const onRequirementDialogClosed = () => {
  editingRequirementId.value = null
}

// Map API value to el-date-picker value-format YYYY-MM-DD HH:mm:ss; clear legacy free-text
const normalizePreferredTimeForPicker = (raw: unknown): string => {
  if (raw == null || raw === '') return ''
  const s = String(raw).trim()
  if (!/^\d{4}-\d{2}-\d{2}/.test(s)) return ''
  if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/.test(s)) return `${s}:00`
  if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(s)) return s
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(s)) {
    return s.replace('T', ' ').slice(0, 19)
  }
  return ''
}

// Check whether a requirement is a draft (not published on the portal)
const isPortalDraft = (row: any) => {
  const p = row?.is_published
  if (p === true || p === 1 || p === '1') return false
  if (p === false || p === 0 || p === '0') return true
  return false
}

// Open the dialog for editing a draft requirement
const openEditRequirement = (row: any) => {
  if (!isPortalDraft(row)) {
    ElMessage.warning('Only drafts (not yet published) can be edited')
    return
  }
  editingRequirementId.value = row.id
  createForm.value = {
    guest_name: row.guest_name || '',
    guest_phone: row.guest_phone || '',
    guest_email: row.guest_email || '',
    guest_address: row.guest_address || '',
    property_type: row.property_type || 'House',
    bedroom: row.bedroom ?? 1,
    bathroom: row.bathroom ?? 1,
    living_room: row.living_room ?? 1,
    kitchen: row.kitchen ?? 1,
    lawn: row.lawn ?? 0,
    car_space: row.car_space ?? 0,
    square_footage: row.square_footage != null ? Number(row.square_footage) : null,
    service_type_name: row.service_type_name || serviceTypeOptions.value[0] || '',
    preferred_time: normalizePreferredTimeForPicker(row.preferred_time),
    budget: row.budget != null ? Number(row.budget) : null,
    description: row.description || '',
    publish_to_portal: false
  }
  showCreateDialog.value = true
}

// Submit the create/update requirement form to the API
const submitCreateRequirement = async () => {
  if (!userId.value) return
  if (!createForm.value.guest_name?.trim() || !createForm.value.guest_phone?.trim()) {
    ElMessage.warning('Name and phone are required')
    return
  }
  if (editingRequirementId.value != null) {
    const b = createForm.value.budget
    if (b === null || b === undefined || !Number.isFinite(Number(b)) || Number(b) < 0) {
      ElMessage.warning('Budget (USD) is required')
      return
    }
  }
  createSubmitting.value = true
  const payload = {
    guest_name: createForm.value.guest_name.trim(),
    guest_phone: createForm.value.guest_phone.trim(),
    guest_email: createForm.value.guest_email?.trim() || undefined,
    guest_address: createForm.value.guest_address?.trim() || undefined,
    property_type: createForm.value.property_type,
    bedroom: createForm.value.bedroom,
    bathroom: createForm.value.bathroom,
    living_room: createForm.value.living_room,
    kitchen: createForm.value.kitchen,
    lawn: createForm.value.lawn,
    car_space: createForm.value.car_space,
    square_footage: createForm.value.square_footage ?? undefined,
    service_type_name: createForm.value.service_type_name || undefined,
    preferred_time: createForm.value.preferred_time || undefined,
    budget: createForm.value.budget ?? undefined,
    description: createForm.value.description || undefined,
    publish_to_portal: createForm.value.publish_to_portal
  }
  try {
    const res: any =
      editingRequirementId.value != null
        ? await portalApi.updateCustomerRequirement(editingRequirementId.value, payload)
        : await portalApi.createCustomerRequirement(payload)
    if (res?.success) {
      ElMessage.success(
        res.published
          ? 'Requirement published on the portal'
          : 'Saved as draft (not listed on portal)'
      )
      showCreateDialog.value = false
      editingRequirementId.value = null
      await loadRequirements()
    } else {
      ElMessage.error(res?.message || 'Failed')
    }
  } catch (e: any) {
    ElMessage.error(
      e?.response?.data?.detail ||
        (editingRequirementId.value != null
          ? 'Failed to update requirement'
          : 'Failed to create requirement')
    )
  } finally {
    createSubmitting.value = false
  }
}

// Fetch the customer's requirements from the API
const loadRequirements = async () => {
  if (!isGuest.value || !userId.value) {
    ElMessage.warning('Only customers can access this page')
    return
  }
  
  loading.value = true
  try {
    const params: any = {
      page: page.value,
      page_size: pageSize.value
    }
    if (filters.value.requirement_id && filters.value.requirement_id.trim()) {
      params.requirement_id = Number(filters.value.requirement_id.trim())
    }
    if (filters.value.status !== null) params.status = filters.value.status
    if (filters.value.property_type) params.property_type = filters.value.property_type
    if (filters.value.service_type) params.service_type = filters.value.service_type
    
    const res = await portalApi.getCustomerRequirements(userId.value, params)
    requirements.value = res?.items || []
    total.value = res?.total || 0
  } catch (e: any) {
    console.error('Failed to load requirements:', e)
    ElMessage.error('Failed to load requirements')
  } finally {
    loading.value = false
  }
}

// Trigger a search with current filters, resetting to page 1
const handleSearch = () => {
  page.value = 1
  loadRequirements()
}

// Reset all filters and reload data from page 1
const handleReset = () => {
  filters.value = {
    requirement_id: '',
    status: null,
    property_type: '',
    service_type: '',
    portal_scope: 'all'
  }
  page.value = 1
  loadRequirements()
}

// Approve and assign a cleaner to a requirement after user confirmation
const handleApprove = async (requirement: any, cleaner: any) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to assign ${cleaner.cleaner_name} to this requirement?`,
      'Confirm Assignment',
      {
        confirmButtonText: 'Yes, Assign',
        cancelButtonText: 'Cancel',
        type: 'info'
      }
    )
    
    const res = await portalApi.approveCleaner(requirement.id, cleaner.cleaner_id)
    if (res.success) {
      ElMessage.success(res.message || 'Cleaner assigned successfully')
      loadRequirements()
    } else {
      ElMessage.error(res.message || 'Failed to assign cleaner')
    }
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('Failed to assign cleaner')
    }
  }
}

// Open the dialog to view a cleaner's full profile
const viewCleanerProfile = (app: any) => {
  selectedCleanerProfile.value = app
  showCleanerProfile.value = true
}

// Process payment for a completed requirement order
const handlePayNow = async (row: any) => {
  if (!row?.order_id) {
    ElMessage.warning('No payable order found for this requirement')
    return
  }
  try {
    await transactionApi.pay(row.order_id)
    ElMessage.success('Payment successful!')
    loadRequirements()
  } catch (e: any) {
    console.error('Payment error:', e)
    ElMessage.error(e?.response?.data?.detail || 'Payment failed')
  }
}

// Return the Element Plus tag type for a given requirement status
const getStatusType = (status: number) => {
  const types = ['warning', 'success', 'primary', 'info', 'danger']
  return types[status] || 'info'
}

// Return the Element Plus tag type for a given cleaner application status
const getApplicationStatusType = (status: number) => {
  const types = ['warning', 'success', 'danger']
  return types[status] || 'info'
}

// Generate an array of booleans for star display based on rating
const getRatingStars = (rating: number) => {
  return Array(5).fill(0).map((_, i) => i < rating)
}

// Lifecycle hook: load service types and requirements on mount if user is a guest
onMounted(() => {
  if (isGuest.value) {
    loadServiceTypes()
    loadRequirements()
  }
})
</script>

<template>
  <div class="customer-my-requirements">
    <div class="page-header page-header-row">
      <div>
        <h2>My posted requirements</h2>
      </div>
      <el-button v-if="isGuest" type="primary" @click="openCreateRequirement">New requirement</el-button>
    </div>
    
    <el-card class="filter-card">
      <div class="filters filters-row">
        <span class="filter-label">Portal</span>
        <el-radio-group v-model="filters.portal_scope" size="small" @change="handleSearch">
          <el-radio-button value="all">All</el-radio-button>
          <el-radio-button value="published">Live on portal</el-radio-button>
          <el-radio-button value="draft">Drafts</el-radio-button>
        </el-radio-group>
      </div>
      <div class="filters">
        <el-input
          v-model="filters.requirement_id"
          placeholder="Requirement ID"
          clearable
          style="width: 160px"
          @keyup.enter="handleSearch"
        />
        <el-select v-model="filters.status" placeholder="Status" clearable style="width: 140px">
          <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
        <el-select v-model="filters.property_type" placeholder="Property Type" clearable style="width: 160px">
          <el-option v-for="p in propertyTypes" :key="p" :label="p" :value="p" />
        </el-select>
        <el-select v-model="filters.service_type" placeholder="Service Type" clearable style="width: 180px">
          <el-option v-for="s in serviceTypeOptions" :key="s" :label="s" :value="s" />
        </el-select>
        <el-button type="primary" @click="handleSearch">Search</el-button>
        <el-button @click="handleReset">Reset</el-button>
      </div>
    </el-card>
    
    <el-card class="data-card">
      <el-table :data="requirements" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="property_type" label="Property" width="100">
          <template #default="{ row }">
            <span>{{ row.property_type }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Rooms" width="100">
          <template #default="{ row }">
            {{ row.bedroom }}B/{{ row.bathroom }}B
          </template>
        </el-table-column>
        <el-table-column prop="service_type_name" label="Service" width="140" />
        <el-table-column label="Portal" width="100">
          <template #default="{ row }">
            <el-tag v-if="isPortalDraft(row)" type="info" size="small">Draft</el-tag>
            <el-tag v-else type="success" size="small">Live</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="budget" label="Budget" width="90">
          <template #default="{ row }">
            <span class="price">${{ row.budget }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ statusTextMap[row.status] || 'Unknown' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Applications" min-width="450">
          <template #default="{ row }">
            <div v-if="row.applications && row.applications.length > 0" class="applications-list">
              <div v-for="app in row.applications" :key="app.id" class="application-item">
                <div class="cleaner-info">
                  <span class="cleaner-name" @click="viewCleanerProfile(app)">{{ app.cleaner_name }}</span>
                  <div class="cleaner-stats-inline">
                    <span class="rating">
                      <span class="stars">
                        <span v-for="(filled, idx) in getRatingStars(app.total_rating)" :key="idx" :class="filled ? 'star filled' : 'star'">★</span>
                      </span>
                      {{ app.total_rating.toFixed(1) }}
                    </span>
                    <span class="orders">{{ app.total_orders }} jobs</span>
                  </div>
                  <span class="offer-price">${{ app.offered_price }}</span>
                  <el-tag v-if="row.assigned_cleaner_id === app.cleaner_id" type="success" size="small">Assigned</el-tag>
                  <el-tag v-else :type="getApplicationStatusType(app.status)" size="small">
                    {{ app.status_text }}
                  </el-tag>
                  <el-button 
                    v-if="!row.assigned_cleaner_id && app.status === 0" 
                    size="small" 
                    type="primary" 
                    @click="handleApprove(row, app)"
                  >
                    Approve
                  </el-button>
                </div>
              </div>
            </div>
            <span v-else class="no-applications">No applications yet</span>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="Created" width="140" />
        <el-table-column label="Action" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="isPortalDraft(row)"
              type="primary"
              link
              size="small"
              @click="openEditRequirement(row)"
            >
              Edit
            </el-button>
            <el-button
              v-if="Number(row.status) === 3 && row.payment_pending"
              type="warning"
              size="small"
              @click="handlePayNow(row)"
            >
              Pay Now
            </el-button>
          </template>
        </el-table-column>
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

    <el-dialog
      v-model="showCreateDialog"
      class="requirement-dialog"
      width="720px"
      destroy-on-close
      align-center
      @closed="onRequirementDialogClosed"
    >
      <template #header>
        <div class="req-dialog-header">
          <span class="req-dialog-title">{{
            editingRequirementId != null ? 'Edit requirement' : 'New requirement'
          }}</span>
          <span class="req-dialog-sub">{{
            editingRequirementId != null
              ? 'Update your draft before publishing to the portal.'
              : 'Tell us about the job — max two fields per row for clarity.'
          }}</span>
        </div>
      </template>
      <div class="req-dialog-body">
        <el-form label-position="top" class="req-form">
          <div class="req-section">
            <div class="req-section-head">
              <span class="req-section-icon">Contact</span>
            </div>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Your name" required>
                  <el-input v-model="createForm.guest_name" maxlength="100" placeholder="Full name" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Phone" required>
                  <el-input v-model="createForm.guest_phone" maxlength="20" placeholder="Mobile number" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Email">
                  <el-input v-model="createForm.guest_email" maxlength="100" placeholder="name@example.com" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Service address">
                  <el-input
                    v-model="createForm.guest_address"
                    maxlength="500"
                    type="textarea"
                    :rows="2"
                    placeholder="Street, unit, city — where cleaning should take place"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <div class="req-section">
            <div class="req-section-head">
              <span class="req-section-icon">Property &amp; service</span>
            </div>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Property type">
                  <el-select v-model="createForm.property_type" placeholder="Select" style="width: 100%">
                    <el-option v-for="p in propertyTypes" :key="p" :label="p" :value="p" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Service type">
                  <el-select
                    v-model="createForm.service_type_name"
                    filterable
                    allow-create
                    placeholder="Select or type"
                    style="width: 100%"
                  >
                    <el-option v-for="s in serviceTypeOptions" :key="s" :label="s" :value="s" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Bedrooms">
                  <el-input-number v-model="createForm.bedroom" :min="0" :max="20" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Bathrooms">
                  <el-input-number v-model="createForm.bathroom" :min="0" :max="20" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Living rooms">
                  <el-input-number v-model="createForm.living_room" :min="0" :max="10" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Kitchens">
                  <el-input-number v-model="createForm.kitchen" :min="0" :max="10" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Lawn">
                  <el-input-number v-model="createForm.lawn" :min="0" :max="10" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Car spaces">
                  <el-input-number v-model="createForm.car_space" :min="0" :max="10" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Square feet (optional)">
                  <el-input-number v-model="createForm.square_footage" :min="0" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="Budget (USD)" :required="editingRequirementId != null">
                  <el-input-number v-model="createForm.budget" :min="0" :step="10" style="width: 100%" />
                </el-form-item>
              </el-col>
            </el-row>
          </div>

          <div class="req-section">
            <div class="req-section-head">
              <span class="req-section-icon">Schedule</span>
            </div>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="Preferred date &amp; time">
                  <el-date-picker
                    v-model="createForm.preferred_time"
                    type="datetime"
                    placeholder="Pick date and time"
                    format="YYYY-MM-DD HH:mm"
                    value-format="YYYY-MM-DD HH:mm:ss"
                    style="width: 100%"
                    clearable
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12" class="req-hint-col">
                <p class="req-hint">Uses your local timezone. Clear if you are flexible on timing.</p>
              </el-col>
            </el-row>
          </div>

          <div class="req-section req-section--flat">
            <el-form-item label="Description">
              <el-input
                v-model="createForm.description"
                type="textarea"
                :rows="3"
                maxlength="2000"
                show-word-limit
                placeholder="Access notes, pets, supplies, or other details"
              />
            </el-form-item>
            <el-form-item label="Portal visibility" class="req-visibility">
              <el-switch
                v-model="createForm.publish_to_portal"
                inline-prompt
                active-text="Live"
                inactive-text="Draft"
              />
              <span class="req-visibility-hint">Draft is private until you switch to Live.</span>
            </el-form-item>
          </div>
        </el-form>
      </div>
      <template #footer>
        <div class="req-dialog-footer">
          <el-button @click="showCreateDialog = false">Cancel</el-button>
          <el-button type="primary" :loading="createSubmitting" @click="submitCreateRequirement">
            Save
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="showCleanerProfile" title="Cleaner Profile" width="600px">
      <div v-if="selectedCleanerProfile" class="cleaner-profile">
        <div class="profile-header">
          <div class="avatar-placeholder">
            {{ selectedCleanerProfile.cleaner_name?.charAt(0).toUpperCase() }}
          </div>
          <div class="profile-info">
            <h3>{{ selectedCleanerProfile.cleaner_name }}</h3>
            <div class="profile-badges">
              <el-tag type="warning" size="small">
                <span class="tag-icon">⭐</span> {{ selectedCleanerProfile.star_level }} Star
              </el-tag>
              <el-tag type="success" size="small">Verified Cleaner</el-tag>
            </div>
            <div class="profile-meta">
              <span v-if="selectedCleanerProfile.nationality"><span class="meta-icon">🌍</span> {{ selectedCleanerProfile.nationality }}</span>
              <span v-if="selectedCleanerProfile.languages"><span class="meta-icon">🗣️</span> {{ selectedCleanerProfile.languages }}</span>
              <span v-if="selectedCleanerProfile.phone"><span class="meta-icon">📞</span> {{ selectedCleanerProfile.phone }}</span>
              <span v-if="selectedCleanerProfile.email"><span class="meta-icon">📧</span> {{ selectedCleanerProfile.email }}</span>
              <span v-if="selectedCleanerProfile.address"><span class="meta-icon">📍</span> {{ selectedCleanerProfile.address }}</span>
            </div>
          </div>
        </div>

        <div class="profile-bio" v-if="selectedCleanerProfile.bio">
          <h4>About Me</h4>
          <p>{{ selectedCleanerProfile.bio }}</p>
        </div>
        
        <div class="profile-stats-grid">
          <div class="stat-box">
            <span class="stat-value">{{ selectedCleanerProfile.total_rating?.toFixed(1) }}</span>
            <span class="stat-label">Rating</span>
            <div class="stat-stars">
              <span v-for="(_, idx) in getRatingStars(selectedCleanerProfile.total_rating)" :key="idx" class="star filled">★</span>
            </div>
          </div>
          <div class="stat-box">
            <span class="stat-value">{{ selectedCleanerProfile.completed_orders }}</span>
            <span class="stat-label">Completed Jobs</span>
          </div>
          <div class="stat-box">
            <span class="stat-value">{{ selectedCleanerProfile.star_level }}</span>
            <span class="stat-label">Star Level</span>
          </div>
        </div>

        <div class="profile-footer">
          <span class="join-date">📅 Member since {{ selectedCleanerProfile.join_date }}</span>
        </div>

        <div v-if="selectedCleanerProfile.recent_reviews?.length > 0" class="reviews-section">
          <h4>Customer Reviews ({{ selectedCleanerProfile.recent_reviews?.length }})</h4>
          <div v-for="(review, idx) in selectedCleanerProfile.recent_reviews" :key="idx" class="review-item">
            <div class="review-header">
              <div class="reviewer-info">
                <span class="reviewer-avatar">{{ review.guest_name?.charAt(0).toUpperCase() }}</span>
                <div>
                  <span class="reviewer-name">{{ review.guest_name }}</span>
                  <span class="review-date">{{ review.create_time }}</span>
                </div>
              </div>
              <div class="review-rating">
                <span v-for="(_, idx) in getRatingStars(review.rating)" :key="idx" class="star filled">★</span>
              </div>
            </div>
            <p class="review-comment">{{ review.comment || 'No comment provided' }}</p>
          </div>
        </div>
        <div v-else class="no-reviews">
          <el-empty description="No reviews yet" :image-size="60" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.customer-my-requirements {
  padding: 24px;
}

.filters-row {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
  align-items: center;
}

.filter-label {
  font-size: 13px;
  font-weight: 600;
  color: #606266;
  margin-right: 12px;
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

.page-header-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.data-card {
  margin-bottom: 16px;
}

.price {
  color: #ff6b6b;
  font-weight: 500;
}

.guest-tabs {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
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

.price {
  color: #ff6b6b;
  font-weight: 500;
}

.applications-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.application-item {
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.application-item:last-child {
  border-bottom: none;
}

.cleaner-name {
  cursor: pointer;
  color: #409eff;
  text-decoration: underline;
  white-space: nowrap;
}

.offer-price {
  color: #67c23a;
  font-weight: 500;
  white-space: nowrap;
}

.no-applications {
  color: #909399;
  font-style: italic;
}

.filter-card {
  margin-bottom: 16px;
}

.filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}

.cleaner-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: nowrap;
  overflow: hidden;
  font-size: 12px;
}

.cleaner-stats-inline {
  display: inline-flex;
  gap: 4px;
  font-size: 12px;
  color: #909399;
  align-items: center;
  white-space: nowrap;
}

.cleaner-stats-inline .rating {
  color: #ff9800;
}

.cleaner-stats-inline .stars {
  font-size: 11px;
}

.cleaner-stats-inline .star {
  margin-right: -1px;
}

.cleaner-stats-inline .star.filled {
  color: #ff9800;
}

.cleaner-stats-inline .star:not(.filled) {
  color: #dcdfe6;
}

.rating {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.stars {
  color: #ff9800;
}

.stars .star.filled {
  color: #ff9800;
}

.stars .star:not(.filled) {
  color: #dcdfe6;
}

.orders {
  color: #909399;
}

.cleaner-profile {
  padding: 10px 0;
}

.profile-header {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.avatar-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 32px;
  font-weight: bold;
}

.profile-info h3 {
  margin: 0 0 10px 0;
  font-size: 22px;
  color: #303133;
}

.profile-badges {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}

.profile-meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  color: #606266;
}

.meta-icon {
  margin-right: 4px;
}

.profile-bio {
  background: linear-gradient(135deg, #f0f9eb 0%, #e8f5e9 100%);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.profile-bio h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 14px;
}

.profile-bio p {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.profile-footer {
  text-align: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 16px;
}

.join-date {
  font-size: 13px;
  color: #909399;
}

.profile-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-box {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.stat-box .stat-value {
  display: block;
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
}

.stat-box .stat-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.stat-box .stat-stars {
  margin-top: 6px;
}

.stat-box .star {
  font-size: 16px;
  color: #ff9800;
}

.reviews-section {
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.reviews-section h4 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}

.review-item {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.reviewer-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.reviewer-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
  font-weight: bold;
}

.reviewer-name {
  display: block;
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.review-date {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.review-rating .star {
  font-size: 16px;
  color: #ff9800;
}

.review-comment {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.5;
}

.no-reviews {
  text-align: center;
  padding: 20px;
}
</style>

<style>
/* Dialog is teleported — keep styles global under this class */
.requirement-dialog.el-dialog {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.requirement-dialog .el-dialog__header {
  margin-right: 0;
  padding: 20px 24px 16px;
  border-bottom: 1px solid #ebeef5;
  background: linear-gradient(180deg, #f8fafc 0%, #fff 100%);
}

.requirement-dialog .el-dialog__body {
  padding: 0 24px 8px;
}

.requirement-dialog .el-dialog__footer {
  padding: 16px 24px 20px;
  border-top: 1px solid #ebeef5;
  background: #fafbfc;
}

.req-dialog-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.req-dialog-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  letter-spacing: -0.02em;
}

.req-dialog-sub {
  font-size: 13px;
  color: #909399;
  font-weight: 400;
}

.req-dialog-body {
  max-height: min(70vh, 620px);
  overflow-y: auto;
  padding-top: 16px;
}

.req-form .el-form-item {
  margin-bottom: 18px;
}

.req-section {
  background: #f9fafb;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  padding: 16px 18px 4px;
  margin-bottom: 16px;
}

.req-section--flat {
  background: transparent;
  border: none;
  padding: 0 0 8px;
}

.req-section-head {
  margin: -4px 0 12px;
}

.req-section-icon {
  display: inline-block;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #409eff;
  padding: 4px 10px;
  background: rgba(64, 158, 255, 0.1);
  border-radius: 6px;
}

.req-hint-col {
  display: flex;
  align-items: flex-end;
  padding-bottom: 28px;
}

.req-hint {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
  color: #909399;
}

.req-visibility {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.req-visibility-hint {
  font-size: 13px;
  color: #606266;
}

.req-dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
