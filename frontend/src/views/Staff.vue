<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { serviceOrderApi } from '@/api'

const loading = ref(false)
const staffList = ref([
  { id: 1, name: 'Zhang San', employee_no: 'EMP001', position: 'Room Cleaner', phone: '13800138001', status: 1 },
  { id: 2, name: 'Li Si', employee_no: 'EMP002', position: 'Room Cleaner', phone: '13800138002', status: 1 },
  { id: 3, name: 'Wang Wu', employee_no: 'EMP003', position: 'Supervisor', phone: '13800138003', status: 1 },
  { id: 4, name: 'Zhao Liu', employee_no: 'EMP004', position: 'Room Cleaner', phone: '13800138004', status: 0 },
  { id: 5, name: 'Qi Qian', employee_no: 'EMP005', position: 'Logistics', phone: '13800138005', status: 1 }
])

const positionOptions = ['Room Cleaner', 'Supervisor', 'Logistics', 'Manager']
const dialogVisible = ref(false)
const formData = ref({
  id: null,
  name: '',
  employee_no: '',
  position: '',
  phone: ''
})

const assignDialogVisible = ref(false)
const assignStaffId = ref(null)
const assignStaffName = ref('')
const pendingOrders = ref([])
const selectedOrderId = ref(null)
const assignLoading = ref(false)

const handleAdd = () => {
  formData.value = { id: null, name: '', employee_no: '', position: '', phone: '' }
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  formData.value = { ...row }
  dialogVisible.value = true
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm(`Are you sure you want to delete staff ${row.name}?`, 'Confirm', {
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    type: 'warning'
  }).then(() => {
    ElMessage.success('Deleted successfully')
  })
}

const handleSubmit = () => {
  ElMessage.success(formData.value.id ? 'Updated successfully' : 'Created successfully')
  dialogVisible.value = false
}

const handleAssignTask = async (row: any) => {
  assignStaffId.value = row.id
  assignStaffName.value = row.name
  selectedOrderId.value = null
  assignLoading.value = true
  try {
    const res = await serviceOrderApi.paginated({ page: 1, page_size: 100, filters: { status: 0 } })
    pendingOrders.value = res.items || []
    assignDialogVisible.value = true
  } catch (error) {
    console.error('Failed to fetch pending orders:', error)
    ElMessage.error('Failed to load orders')
  } finally {
    assignLoading.value = false
  }
}

const confirmAssignTask = async () => {
  if (!selectedOrderId.value) {
    ElMessage.warning('Please select an order')
    return
  }
  try {
    await serviceOrderApi.assign(selectedOrderId.value, assignStaffId.value)
    ElMessage.success(`Order assigned to ${assignStaffName.value}`)
    assignDialogVisible.value = false
  } catch (error: any) {
    console.error('Assign error:', error)
    ElMessage.error(error?.response?.data?.detail || 'Failed to assign')
  }
}
</script>

<template>
  <div class="staff-page">
    <el-row :gutter="20" class="stat-cards">
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-info">
            <div class="stat-value">{{ staffList.filter(s => s.status === 1).length }}</div>
            <div class="stat-label">Active Staff</div>
          </div>
          <el-icon class="stat-icon" color="#67c23a"><UserFilled /></el-icon>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-info">
            <div class="stat-value">{{ staffList.filter(s => s.position === 'Room Cleaner').length }}</div>
            <div class="stat-label">Cleaners</div>
          </div>
          <el-icon class="stat-icon" color="#409eff"><Cleaning /></el-icon>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="8">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-info">
            <div class="stat-value">{{ staffList.filter(s => s.position === 'Supervisor').length }}</div>
            <div class="stat-label">Managers</div>
          </div>
          <el-icon class="stat-icon" color="#e6a23c"><Avatar /></el-icon>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>Staff List</span>
          <el-button type="primary" @click="handleAdd">Add Staff</el-button>
        </div>
      </template>

      <el-table :data="staffList" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="employee_no" label="Employee No" width="100" />
        <el-table-column prop="name" label="Name" width="120" />
        <el-table-column prop="position" label="Position" width="120" />
        <el-table-column prop="phone" label="Phone" width="130" />
        <el-table-column prop="status" label="Status" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? 'Active' : 'Inactive' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">Edit</el-button>
            <el-button type="success" link @click="handleAssignTask(row)">Assign Task</el-button>
            <el-button type="danger" link @click="handleDelete(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="Staff Information" width="500px" destroy-on-close>
      <el-form :model="formData" label-width="100px">
        <el-form-item label="Name">
          <el-input v-model="formData.name" placeholder="Enter name" />
        </el-form-item>
        <el-form-item label="Employee No">
          <el-input v-model="formData.employee_no" placeholder="Enter employee number" />
        </el-form-item>
        <el-form-item label="Position">
          <el-select v-model="formData.position" placeholder="Select position" style="width: 100%">
            <el-option v-for="p in positionOptions" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>
        <el-form-item label="Phone">
          <el-input v-model="formData.phone" placeholder="Enter phone number" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSubmit">Confirm</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="assignDialogVisible" title="Assign Order to Staff" width="450px" destroy-on-close>
      <div style="margin-bottom: 16px">
        <strong>Staff:</strong> {{ assignStaffName }}
      </div>
      <el-form label-width="80px">
        <el-form-item label="Select Order">
          <el-select v-model="selectedOrderId" placeholder="Select pending order" style="width: 100%">
            <el-option
              v-for="order in pendingOrders"
              :key="order.order_id"
              :label="order.order_no + ' - Room ' + order.room_id"
              :value="order.order_id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="confirmAssignTask">Confirm</el-button>
      </template>
    </el-dialog>
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
  font-size: 32px;
  font-weight: 600;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.stat-icon {
  font-size: 48px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
