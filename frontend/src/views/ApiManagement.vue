<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { request, permissionApi } from '@/api'

const loading = ref(false)
const apis = ref<any[]>([])
const permissions = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const filters = ref({
  method: '',
  permission_id: null as number | null,
  api_path: ''
})

const showDialog = ref(false)
const isEdit = ref(false)
const formData = ref<any>({
  id: null,
  api_path: '',
  api_method: 'GET',
  permission_id: null,
  description: ''
})

const methodOptions = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']

const permissionCodes = ref<string[]>([])
const hasApiPermissions = computed(() =>
  permissionCodes.value.some((c) => typeof c === 'string' && c.startsWith('api:')),
)
// 如果当前角色没有任何 api:* 权限条目，保持原行为（不把页面“隐藏成空白”）
const canView = computed(() => !hasApiPermissions.value || permissionCodes.value.includes('api:view'))
const canCreate = computed(() => !hasApiPermissions.value || permissionCodes.value.includes('api:create'))
const canUpdate = computed(() => !hasApiPermissions.value || permissionCodes.value.includes('api:update'))
const canDelete = computed(() => !hasApiPermissions.value || permissionCodes.value.includes('api:delete'))

const loadMyPermissions = async () => {
  try {
    const res = await permissionApi.getMyPermissions()
    permissionCodes.value = Array.isArray(res) ? res.map((p: any) => p.permission_code) : []
  } catch (e) {
    console.error('Failed to load my permissions:', e)
    permissionCodes.value = []
  }
}

const loadApis = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    params.append('page', String(page.value))
    params.append('page_size', String(pageSize.value))
    if (filters.value.method) params.append('method', filters.value.method)
    if (filters.value.permission_id) params.append('permission_id', String(filters.value.permission_id))
    if (filters.value.api_path) params.append('api_path', filters.value.api_path)
    
    const res = await fetch(`/api/rbac/apis?${params}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    const data = await res.json()
    apis.value = data?.items || []
    total.value = data?.total || 0
  } catch (e: any) {
    console.error('Failed to load APIs:', e)
    ElMessage.error('Failed to load APIs')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  loadApis()
}

const handleReset = () => {
  filters.value = {
    method: '',
    permission_id: null,
    api_path: ''
  }
  page.value = 1
  loadApis()
}

const handlePageChange = (newPage: number) => {
  page.value = newPage
  loadApis()
}

const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  page.value = 1
  loadApis()
}

const loadPermissions = async () => {
  try {
    // Use rbac picklist (not GET /api/permissions — that requires permission:view)
    const data = await request.get('/rbac/permissions/options')
    permissions.value = Array.isArray(data) ? data : []
  } catch (e: any) {
    console.error('Failed to load permissions:', e)
    permissions.value = []
  }
}

const handleAdd = () => {
  isEdit.value = false
  formData.value = {
    id: null,
    api_path: '',
    api_method: 'GET',
    permission_id: null,
    description: ''
  }
  showDialog.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  formData.value = { ...row }
  showDialog.value = true
}

const handleSave = async () => {
  try {
    const url = isEdit.value ? `/api/rbac/apis/${formData.value.id}` : '/api/rbac/apis'
    const method = isEdit.value ? 'PUT' : 'POST'
    
    const res = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(formData.value)
    })
    
    if (res.ok) {
      ElMessage.success(isEdit.value ? 'API updated' : 'API created')
      showDialog.value = false
      loadApis()
    } else {
      ElMessage.error('Operation failed')
    }
  } catch (e: any) {
    ElMessage.error('Operation failed')
  }
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('Are you sure you want to delete this API?', 'Warning', {
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      type: 'warning'
    })
    
    const res = await fetch(`/api/rbac/apis/${row.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (res.ok) {
      ElMessage.success('API deleted')
      loadApis()
    } else {
      ElMessage.error('Delete failed')
    }
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('Delete failed')
    }
  }
}

const getPermissionName = (permissionId: number | null | undefined) => {
  if (permissionId == null) return '—'
  const perm = permissions.value.find((p) => p.id === permissionId)
  return perm ? perm.permission_name : `ID ${permissionId}`
}

onMounted(() => {
  loadMyPermissions()
  loadApis()
  loadPermissions()
})
</script>

<template>
  <div class="api-management">
    <div class="page-header">
      <h2>API Management</h2>
      <p class="subtitle">Manage system APIs and their permissions</p>
    </div>
    
    <p v-if="!canView" class="hint warn">
      You need <strong>api:view</strong> to view and manage APIs.
    </p>

    <el-card v-if="canView" class="filter-card">
      <div class="filters">
        <el-select v-model="filters.method" placeholder="Method" clearable style="width: 120px">
          <el-option v-for="m in methodOptions" :key="m" :label="m" :value="m" />
        </el-select>
        <el-input v-model="filters.api_path" placeholder="API Path" clearable style="width: 200px" />
        <el-select v-model="filters.permission_id" placeholder="Permission" clearable style="width: 180px">
          <el-option v-for="p in permissions" :key="p.id" :label="p.permission_name" :value="p.id" />
        </el-select>
        <el-button type="primary" @click="handleSearch">Search</el-button>
        <el-button @click="handleReset">Reset</el-button>
        <el-button v-if="canCreate" type="primary" @click="handleAdd">Add API</el-button>
      </div>
    </el-card>
    
    <el-card v-if="canView" class="data-card">
      <el-table :data="apis" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="api_path" label="API Path" min-width="200" />
        <el-table-column prop="api_method" label="Method" width="100">
          <template #default="{ row }">
            <el-tag :type="row.api_method === 'GET' ? 'success' : row.api_method === 'POST' ? 'primary' : row.api_method === 'DELETE' ? 'danger' : 'warning'" size="small">
              {{ row.api_method }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="permission_id" label="Permission" width="150">
          <template #default="{ row }">
            {{ getPermissionName(row.permission_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="Description" min-width="150" />
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button v-if="canUpdate" size="small" type="primary" link @click="handleEdit(row)">Edit</el-button>
            <el-button v-if="canDelete" size="small" type="danger" link @click="handleDelete(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-if="canView"
        class="pagination"
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>
    
    <el-dialog v-model="showDialog" :title="isEdit ? 'Edit API' : 'Add API'" width="500px">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="API Path">
          <el-input v-model="formData.api_path" placeholder="/api/example" />
        </el-form-item>
        <el-form-item label="Method">
          <el-select v-model="formData.api_method" style="width: 100%">
            <el-option v-for="m in methodOptions" :key="m" :label="m" :value="m" />
          </el-select>
        </el-form-item>
        <el-form-item label="Permission">
          <el-select v-model="formData.permission_id" placeholder="Select permission" style="width: 100%" clearable>
            <el-option v-for="p in permissions" :key="p.id" :label="p.permission_name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="formData.description" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">Cancel</el-button>
        <el-button v-if="isEdit ? canUpdate : canCreate" type="primary" @click="handleSave">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.api-management {
  padding: 24px;
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

.filter-card {
  margin-bottom: 16px;
}

.filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.toolbar {
  display: flex;
  justify-content: flex-start;
}

.data-card {
  margin-bottom: 16px;
}

.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
