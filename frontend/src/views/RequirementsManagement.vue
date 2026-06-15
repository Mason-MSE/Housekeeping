<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { portalApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const loading = ref(false)

const requirements = ref<any[]>([])
const cleaners = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const showAssignDialog = ref(false)
const selectedRequirement = ref<any>(null)
const selectedCleanerId = ref<number | null>(null)

const filters = ref({
  guest_name: '',
  guest_phone: '',
  property_type: '',
  service_type: '',
  status: null as number | null,
  start_date: '',
  end_date: ''
})

const statusOptions = [
  { value: 0, label: 'Pending' },
  { value: 1, label: 'Assigned' },
  { value: 2, label: 'In Progress' },
  { value: 3, label: 'Completed' },
  { value: 4, label: 'Cancelled' }
]

const propertyTypes = ['Apartment', 'House', 'Condo', 'Townhouse', 'Villa', 'Studio']
const serviceTypes = ['Standard Cleaning', 'Deep Cleaning', 'Move-in Cleaning', 'Move-out Cleaning', 'Post-Construction']

const cleanerUsername = (c: any) => {
  const u = (c?.username || '').trim()
  return u || `#${c?.id ?? '?'}`
}

const loadRequirements = async () => {
  loading.value = true
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (filters.value.guest_name) params.guest_name = filters.value.guest_name
    if (filters.value.guest_phone) params.guest_phone = filters.value.guest_phone
    if (filters.value.property_type) params.property_type = filters.value.property_type
    if (filters.value.service_type) params.service_type = filters.value.service_type
    if (filters.value.status !== null) params.status = filters.value.status
    if (filters.value.start_date) params.start_date = filters.value.start_date
    if (filters.value.end_date) params.end_date = filters.value.end_date

    const res = await portalApi.getAdminRequirements(params)
    requirements.value = res?.items || []
    total.value = res?.total || 0
  } catch (e: any) {
    console.error('Failed to load requirements:', e)
    ElMessage.error('Failed to load requirements')
  } finally {
    loading.value = false
  }
}

const loadCleaners = async () => {
  try {
    const res = await portalApi.getAdminCleaners()
    cleaners.value = res || []
  } catch (e: any) {
    console.error('Failed to load cleaners:', e)
  }
}

const handleSearch = () => {
  page.value = 1
  loadRequirements()
}

const handleReset = () => {
  filters.value = {
    guest_name: '',
    guest_phone: '',
    property_type: '',
    service_type: '',
    status: null,
    start_date: '',
    end_date: ''
  }
  page.value = 1
  loadRequirements()
}

const handleAssign = (row: any) => {
  if (row.can_reassign_cleaner === false) {
    ElMessage.warning(
      'This order is no longer only "assigned" (e.g. in progress or pending payment). Cleaner cannot be changed.'
    )
    return
  }
  selectedRequirement.value = row
  selectedCleanerId.value = row.assigned_cleaner_id ?? null
  showAssignDialog.value = true
}

const confirmAssign = async () => {
  if (!selectedRequirement.value || !selectedCleanerId.value) {
    ElMessage.warning('Please select a cleaner')
    return
  }

  try {
    await portalApi.assignRequirementToCleaner(selectedRequirement.value.id, selectedCleanerId.value)
    ElMessage.success('Requirement assigned successfully')
    showAssignDialog.value = false
    loadRequirements()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Failed to assign requirement')
  }
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('Are you sure you want to delete this requirement?', 'Warning', {
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      type: 'warning'
    })
    await portalApi.deleteRequirement(row.id)
    ElMessage.success('Requirement deleted')
    loadRequirements()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('Failed to delete requirement')
    }
  }
}

const getStatusLabel = (status: number) => {
  const option = statusOptions.find(s => s.value === status)
  return option ? option.label : 'Unknown'
}

const getStatusType = (status: number) => {
  const types = ['info', 'success', 'warning', 'success', 'danger']
  return types[status] || 'info'
}

onMounted(() => {
  loadRequirements()
  loadCleaners()
})
</script>

<template>
  <div class="requirements-management">
    <div class="header">
      <h2>Requirements Management</h2>
    </div>

    <div class="filters">
      <el-input v-model="filters.guest_name" placeholder="Guest Name" clearable style="width: 150px" />
      <el-input v-model="filters.guest_phone" placeholder="Phone" clearable style="width: 150px" />
      <el-select v-model="filters.property_type" placeholder="Property Type" clearable style="width: 150px">
        <el-option v-for="p in propertyTypes" :key="p" :label="p" :value="p" />
      </el-select>
      <el-select v-model="filters.service_type" placeholder="Service Type" clearable style="width: 180px">
        <el-option v-for="s in serviceTypes" :key="s" :label="s" :value="s" />
      </el-select>
      <el-select v-model="filters.status" placeholder="Status" clearable style="width: 130px">
        <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
      </el-select>
      <el-button type="primary" @click="handleSearch">Search</el-button>
      <el-button @click="handleReset">Reset</el-button>
    </div>

    <el-table :data="requirements" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="guest_name" label="Guest Name" width="120" />
      <el-table-column prop="guest_phone" label="Phone" width="130" />
      <el-table-column prop="property_type" label="Property" width="100" />
      <el-table-column prop="bedroom" label="Bedroom" width="80" />
      <el-table-column prop="bathroom" label="Bathroom" width="90" />
      <el-table-column prop="service_type_name" label="Service" width="150" />
      <el-table-column prop="budget" label="Budget" width="80">
        <template #default="{ row }">
          ${{ row.budget }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="Status" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Cleaner" min-width="120">
        <template #default="{ row }">
          {{ row.assigned_cleaner_username || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="Created" width="150" />
      <el-table-column label="Actions" width="180" fixed="right">
        <template #default="{ row }">
          <el-tooltip
            :disabled="row.can_reassign_cleaner !== false"
            placement="top"
            content="Order already in progress, completed, or pending payment — cannot change cleaner."
          >
            <span>
              <el-button
                size="small"
                type="primary"
                :disabled="row.can_reassign_cleaner === false"
                @click="handleAssign(row)"
              >
                Assign
              </el-button>
            </span>
          </el-tooltip>
          <el-button size="small" type="danger" @click="handleDelete(row)">Delete</el-button>
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

    <el-dialog v-model="showAssignDialog" title="Assign Cleaner" width="400px">
      <div v-if="selectedRequirement" class="assign-info">
        <p><strong>Requirement #{{ selectedRequirement.id }}</strong></p>
        <p>{{ selectedRequirement.guest_name }} - {{ selectedRequirement.property_type }}</p>
      </div>
      <el-select v-model="selectedCleanerId" placeholder="Select username" style="width: 100%; margin-top: 16px">
        <el-option
          v-for="cleaner in cleaners"
          :key="cleaner.id"
          :label="`${cleanerUsername(cleaner)} · Pending: ${cleaner.pending_tasks}`"
          :value="cleaner.id"
        />
      </el-select>
      <template #footer>
        <el-button @click="showAssignDialog = false">Cancel</el-button>
        <el-button type="primary" @click="confirmAssign">Confirm</el-button>
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
.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
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
