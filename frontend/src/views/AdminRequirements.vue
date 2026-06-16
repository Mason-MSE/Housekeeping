<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { portalApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

// User store for role/permission information
const userStore = useUserStore()
// Loading state for the data table
const loading = ref(false)

// List of customer requirements
const requirements = ref<any[]>([])
// List of available cleaners for assignment
const cleaners = ref<any[]>([])
// Total number of requirements matching the query
const total = ref(0)
// Current pagination page
const page = ref(1)
// Number of items per page
const pageSize = ref(20)

// Filter criteria for the requirements list
const filters = ref({
  guest_name: '',
  guest_phone: '',
  property_type: '',
  service_type: '',
  start_date: '',
  end_date: ''
})

// Date range picker model
const dateRange = ref<[string, string] | null>(null)

// Dialog visibility for cleaner assignment
const showAssignDialog = ref(false)
// The requirement currently being assigned
const selectedRequirement = ref<any>(null)
// The selected cleaner ID for assignment
const selectedCleanerId = ref<any>(null)
// Loading state during assignment submission
const assignLoading = ref(false)

// Array of role names for the current user
const userRoles = computed(() => userStore.userInfo?.roles || [userStore.userInfo?.role || 'guest'])
// Whether the current user has an admin/manager role
const isAdmin = computed(() => userRoles.value.some(r => ['admin', 'manager', 'administrator'].includes(r.toLowerCase())))

// Options for requirement status filter
const statusOptions = [
  { value: 0, label: 'Pending', type: 'warning' },
  { value: 1, label: 'Assigned', type: 'success' },
  { value: 2, label: 'In Progress', type: 'primary' },
  { value: 3, label: 'Completed', type: 'info' }
]

// Available property type options
const propertyTypes = ['House', 'Apartment', 'Villa', 'Condo', 'Townhouse', 'Studio']

// Fetch requirements and cleaners data from the API
const loadData = async () => {
  if (!isAdmin.value) return
  
  loading.value = true
  try {
    const params: any = {
      page: page.value,
      page_size: pageSize.value
    }
    if (filters.value.guest_name) params.guest_name = filters.value.guest_name
    if (filters.value.guest_phone) params.guest_phone = filters.value.guest_phone
    if (filters.value.property_type) params.property_type = filters.value.property_type
    if (filters.value.service_type) params.service_type = filters.value.service_type
    if (filters.value.start_date) params.start_date = filters.value.start_date
    if (filters.value.end_date) params.end_date = filters.value.end_date
    
    const [reqRes, cleanerRes] = await Promise.all([
      portalApi.getAdminRequirements(params),
      portalApi.getAdminCleaners()
    ])
    requirements.value = reqRes?.items || []
    total.value = reqRes?.total || 0
    cleaners.value = cleanerRes || []
  } catch (e: any) {
    console.error('Failed to load data:', e)
    ElMessage.error('Failed to load data')
  } finally {
    loading.value = false
  }
}

// Trigger a search with current filters, resetting to page 1
const handleSearch = () => {
  page.value = 1
  loadData()
}

// Reset all filters and reload data from page 1
const handleReset = () => {
  filters.value = {
    guest_name: '',
    guest_phone: '',
    property_type: '',
    service_type: '',
    start_date: '',
    end_date: ''
  }
  dateRange.value = null
  page.value = 1
  loadData()
}

// Update date filters when the date range picker changes
const handleDateRangeChange = (val: [string, string] | null) => {
  if (val) {
    filters.value.start_date = val[0]
    filters.value.end_date = val[1]
  } else {
    filters.value.start_date = ''
    filters.value.end_date = ''
  }
  page.value = 1
  loadData()
}

// Handle pagination page change and reload data
const handlePageChange = (newPage: number) => {
  page.value = newPage
  loadData()
}

// Handle page size change and reload data from page 1
const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  page.value = 1
  loadData()
}

// Return the Element Plus tag type for a given requirement status
const getStatusType = (status: number) => {
  const types: Record<number, string> = { 0: 'warning', 1: 'success', 2: 'primary', 3: 'info' }
  return types[status] || 'info'
}

// Return the human-readable label for a given requirement status
const getStatusLabel = (status: number) => {
  const labels: Record<number, string> = { 0: 'Pending', 1: 'Assigned', 2: 'In Progress', 3: 'Completed' }
  return labels[status] || 'Unknown'
}

// Return the cleaner's username for display in the assign dropdown
const cleanerUsername = (c: any) => {
  const u = (c?.username || '').trim()
  return u || `#${c?.id ?? '?'}`
}

// Open the dialog to assign a cleaner to a requirement
const openAssignDialog = (req: any) => {
  if (req.can_reassign_cleaner === false) {
    ElMessage.warning(
      'This order is no longer only "assigned" (e.g. in progress or pending payment). Cleaner cannot be changed.'
    )
    return
  }
  selectedRequirement.value = req
  selectedCleanerId.value = req.assigned_cleaner_id || null
  showAssignDialog.value = true
}

// Confirm and submit the cleaner assignment to the API
const confirmAssign = async () => {
  if (!selectedRequirement.value || !selectedCleanerId.value) {
    ElMessage.warning('Please select a cleaner')
    return
  }
  
  assignLoading.value = true
  try {
    await portalApi.assignRequirementToCleaner(selectedRequirement.value.id, selectedCleanerId.value)
    ElMessage.success('Cleaner assigned successfully')
    showAssignDialog.value = false
    loadData()
  } catch (e: any) {
    console.error('Failed to assign:', e)
    ElMessage.error(e?.response?.data?.detail || 'Failed to assign cleaner')
  } finally {
    assignLoading.value = false
  }
}

// Hide a requirement from the portal after user confirmation
const handleHide = async (req: any) => {
  try {
    await ElMessageBox.confirm(`Are you sure you want to hide this requirement?`, 'Confirm', {
      confirmButtonText: 'Yes',
      cancelButtonText: 'Cancel',
      type: 'warning'
    })
    
    await portalApi.hideRequirement(req.id)
    ElMessage.success('Requirement hidden successfully')
    loadData()
  } catch (e: any) {
    if (e !== 'cancel') {
      console.error('Failed to hide:', e)
      ElMessage.error('Failed to hide requirement')
    }
  }
}

// Permanently delete a requirement after user confirmation
const handleDelete = async (req: any) => {
  try {
    await ElMessageBox.confirm(`Are you sure you want to permanently delete this requirement? This action cannot be undone.`, 'Confirm Delete', {
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      type: 'warning'
    })
    
    await portalApi.deleteRequirement(req.id)
    ElMessage.success('Requirement deleted successfully')
    loadData()
  } catch (e: any) {
    if (e !== 'cancel') {
      console.error('Failed to delete:', e)
      ElMessage.error('Failed to delete requirement')
    }
  }
}

// Lifecycle hook: load requirements data on mount
onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="requirements-management">
    <div class="header">
      <h2>Requirements Management</h2>
    </div>

    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="">
          <el-input v-model="filters.guest_name" placeholder="Guest Name" clearable style="width: 120px" />
        </el-form-item>
        <el-form-item label="">
          <el-input v-model="filters.guest_phone" placeholder="Phone" clearable style="width: 120px" />
        </el-form-item>
        <el-form-item label="">
          <el-select v-model="filters.property_type" placeholder="Property" clearable style="width: 120px">
            <el-option v-for="p in propertyTypes" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>
        <el-form-item label="">
          <el-input v-model="filters.service_type" placeholder="Service" clearable style="width: 100px" />
        </el-form-item>
        <el-form-item label="">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="~"
            start-placeholder="Start"
            end-placeholder="End"
            value-format="YYYY-MM-DD"
            style="width: 200px"
            @change="handleDateRangeChange"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">Search</el-button>
          <el-button @click="handleReset">Reset</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-table :data="requirements" v-loading="loading" stripe size="small">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="guest_name" label="Guest" width="100" />
      <el-table-column prop="guest_phone" label="Phone" width="110" />
      <el-table-column prop="property_type" label="Property" width="90" />
      <el-table-column label="Room" width="80">
        <template #default="{ row }">
          {{ row.bedroom }}BR/{{ row.bathroom }}BA
        </template>
      </el-table-column>
      <el-table-column prop="service_type_name" label="Service" width="100" />
      <el-table-column prop="budget" label="Budget" width="70">
        <template #default="{ row }">
          ${{ row.budget }}
        </template>
      </el-table-column>
      <el-table-column prop="preferred_time" label="Preferred" width="100" />
      <el-table-column label="Status" width="80">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Cleaner" min-width="120">
        <template #default="{ row }">
          {{ row.assigned_cleaner_username || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="applications_count" label="Apps" width="50" align="center" />
      <el-table-column prop="create_time" label="Created" width="90" />
      <el-table-column label="Actions" width="150" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-tooltip
              :disabled="row.can_reassign_cleaner !== false"
              placement="top"
              content="Order already in progress, completed, or pending payment — cannot change cleaner."
            >
              <span>
                <el-button
                  size="small"
                  type="primary"
                  link
                  :disabled="row.can_reassign_cleaner === false"
                  @click="openAssignDialog(row)"
                >
                  Assign
                </el-button>
              </span>
            </el-tooltip>
            <el-button size="small" type="warning" link @click="handleHide(row)">Hide</el-button>
            <!-- <el-button size="small" type="danger" link @click="handleDelete(row)">Delete</el-button> -->
          </div>
        </template>
      </el-table-column>
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

    <el-dialog v-model="showAssignDialog" title="Assign Cleaner" width="400px">
      <div v-if="selectedRequirement" class="assign-info">
        <p><strong>#{{ selectedRequirement.id }}</strong> - {{ selectedRequirement.guest_name }}</p>
        <p>{{ selectedRequirement.property_type }} | {{ selectedRequirement.service_type_name }} | ${{ selectedRequirement.budget }}</p>
      </div>
      
      <el-form label-width="80px" style="margin-top: 16px">
        <el-form-item label="Username">
          <el-select v-model="selectedCleanerId" placeholder="Select username" style="width: 100%">
            <el-option
              v-for="cleaner in cleaners"
              :key="cleaner.id"
              :label="`${cleanerUsername(cleaner)} · P:${cleaner.pending_tasks}/C:${cleaner.completed_tasks}`"
              :value="cleaner.id"
            >
              <span>{{ cleanerUsername(cleaner) }}</span>
              <span style="float: right; color: #8492a6; font-size: 12px">
                {{ cleaner.pending_tasks }}P / {{ cleaner.completed_tasks }}C
              </span>
            </el-option>
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showAssignDialog = false">Cancel</el-button>
        <el-button type="primary" @click="confirmAssign" :loading="assignLoading">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.requirements-management {
  padding: 16px;
}
.header {
  margin-bottom: 16px;
}
.header h2 {
  margin: 0;
  font-size: 18px;
}
.filter-card {
  margin-bottom: 16px;
}
.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.filter-form :deep(.el-form-item) {
  margin-bottom: 0;
  margin-right: 8px;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
.action-buttons {
  display: flex;
  gap: 4px;
  white-space: nowrap;
}
.action-buttons .el-button {
  padding: 2px 4px;
  min-width: auto;
}
.assign-info {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}
.assign-info p {
  margin: 4px 0;
  font-size: 14px;
}
</style>
