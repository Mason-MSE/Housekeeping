<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import { permissionApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

// Loading state for data fetching
const loading = ref(false)
// Full list of permissions
const permissions = ref<any[]>([])
// Permission codes the current user has
const permissionCodes = ref<string[]>([])

// Search keyword
const keyword = ref('')
// Pagination page number
const page = ref(1)
// Pagination page size
const pageSize = ref(20)

// Dialog visibility for create/edit
const showDialog = ref(false)
// Dialog visibility for viewing detail
const showViewDialog = ref(false)
// Dialog mode (create or edit)
const dialogMode = ref<'create' | 'edit'>('create')
// Loading state for form submission
const submitLoading = ref(false)
// Form reference for validation
const formRef = ref<FormInstance>()
// Detail data for view dialog
const viewDetail = ref<any>(null)
// Original permission code before edit
const editOriginalCode = ref('')

// Reactive form model for create/edit
const form = reactive({
  id: null as number | null,
  permission_code: '',
  permission_name: '',
  description: ''
})

const rules: FormRules = {
  permission_code: [{ required: true, message: 'Code required', trigger: 'blur' }],
  permission_name: [{ required: true, message: 'Name required', trigger: 'blur' }]
}

// Computed whether the user has permission:view
const canView = computed(() => permissionCodes.value.includes('permission:view'))
// Computed whether the user has permission:create
const canCreate = computed(() => permissionCodes.value.includes('permission:create'))
// Computed whether the user has permission:update
const canUpdate = computed(() => permissionCodes.value.includes('permission:update'))
// Computed whether the user has permission:delete
const canDelete = computed(() => permissionCodes.value.includes('permission:delete'))

// Computed list of permissions filtered by keyword
const filteredPermissions = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  if (!q) return permissions.value
  return permissions.value.filter((p) => {
    const code = (p.permission_code || '').toLowerCase()
    const name = (p.permission_name || '').toLowerCase()
    const desc = (p.description || '').toLowerCase()
    return code.includes(q) || name.includes(q) || desc.includes(q)
  })
})

// Computed total count after filtering
const totalFiltered = computed(() => filteredPermissions.value.length)

// Computed paginated slice of filtered permissions
const pagedPermissions = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredPermissions.value.slice(start, start + pageSize.value)
})

// Load the current user's permission codes
const loadMyPermissions = async () => {
  try {
    const res = await permissionApi.getMyPermissions()
    permissionCodes.value = (res || []).map((p: any) => p.permission_code)
  } catch (e) {
    console.error(e)
    permissionCodes.value = []
  }
}

// Load all permissions from the API
const loadPermissions = async () => {
  if (!canView.value) {
    permissions.value = []
    return
  }
  loading.value = true
  try {
    const res = await permissionApi.list()
    permissions.value = Array.isArray(res) ? res : []
  } catch (e: any) {
    console.error(e)
    ElMessage.error(e?.response?.data?.detail || 'Failed to load permissions')
    permissions.value = []
  } finally {
    loading.value = false
  }
}

// Handle search: reset to page 1
const handleSearch = () => {
  page.value = 1
}

// Reset search keyword and page
const handleResetFilter = () => {
  keyword.value = ''
  page.value = 1
}

// Reset to page 1 when page size changes
const handlePageSizeChange = () => {
  page.value = 1
}

// Reset the create/edit form to defaults
const resetForm = () => {
  form.id = null
  form.permission_code = ''
  form.permission_name = ''
  form.description = ''
  editOriginalCode.value = ''
  formRef.value?.resetFields()
}

// Open the create permission dialog
const openCreate = () => {
  dialogMode.value = 'create'
  resetForm()
  showDialog.value = true
}

// Open the edit permission dialog with row data
const openEdit = (row: any) => {
  dialogMode.value = 'edit'
  form.id = row.id
  form.permission_code = row.permission_code || ''
  form.permission_name = row.permission_name || ''
  form.description = row.description || ''
  editOriginalCode.value = (row.permission_code || '').trim()
  showDialog.value = true
}

// Open the permission detail dialog
const openView = async (row: any) => {
  viewDetail.value = null
  showViewDialog.value = true
  try {
    const res = await permissionApi.getById(row.id)
    viewDetail.value = res
  } catch (e: any) {
    console.error(e)
    viewDetail.value = { ...row }
    if (e?.response?.status !== 404) {
      ElMessage.warning(e?.response?.data?.detail || 'Could not refresh detail; showing list data')
    }
  }
}

// Submit the create/edit permission form
const submit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (ok) => {
    if (!ok) return

    const newCode = form.permission_code.trim()
    if (
      dialogMode.value === 'edit' &&
      canUpdate.value &&
      newCode !== editOriginalCode.value
    ) {
      try {
        await ElMessageBox.confirm(
          'You changed the permission code. Role/API bindings use numeric IDs and stay valid; only the code string changes. Continue?',
          'Confirm code change',
          { type: 'warning', confirmButtonText: 'Save', cancelButtonText: 'Cancel' }
        )
      } catch {
        return
      }
    }

    submitLoading.value = true
    try {
      const payload = {
        permission_code: newCode,
        permission_name: form.permission_name.trim(),
        description: form.description.trim() || undefined
      }
      if (dialogMode.value === 'create') {
        await permissionApi.create(payload)
        ElMessage.success('Permission created')
      } else if (form.id != null) {
        await permissionApi.update(form.id, payload)
        ElMessage.success('Permission updated')
      }
      showDialog.value = false
      await loadPermissions()
      await loadMyPermissions()
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.detail || 'Save failed')
    } finally {
      submitLoading.value = false
    }
  })
}

// Delete a permission after confirmation
const confirmDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `Delete permission "${row.permission_code}"? Role and menu links to it will be removed.`,
      'Confirm delete',
      { type: 'warning', confirmButtonText: 'Delete', cancelButtonText: 'Cancel' }
    )
    await permissionApi.delete(row.id)
    ElMessage.success('Permission deleted')
    await loadPermissions()
    await loadMyPermissions()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e?.response?.data?.detail || 'Delete failed')
    }
  }
}

// Lifecycle hook: load permissions and user permissions on mount
onMounted(async () => {
  await loadMyPermissions()
  await loadPermissions()
})
</script>

<template>
  <div class="permission-management">
    <div class="header">
      <h2>Permission Management</h2>
      <div class="header-actions">
        <el-button v-if="canView" @click="loadPermissions">Refresh</el-button>
        <el-button v-if="canCreate" type="primary" @click="openCreate">Add Permission</el-button>
      </div>
    </div>

    <el-card v-if="canView" class="filter-card" shadow="never">
      <div class="filters">
        <el-input
          v-model="keyword"
          placeholder="Search code, name, or description"
          clearable
          style="width: 280px"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        />
        <el-button type="primary" @click="handleSearch">Search</el-button>
        <el-button @click="handleResetFilter">Reset</el-button>
      </div>
    </el-card>

    <p v-if="!canView" class="hint warn">
      You need <strong>permission:view</strong> to list and view permissions.
    </p>

    <el-table v-if="canView" :data="pagedPermissions" v-loading="loading" stripe size="small">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="permission_code" label="Code" min-width="160" show-overflow-tooltip />
      <el-table-column prop="permission_name" label="Name" min-width="160" show-overflow-tooltip />
      <el-table-column prop="description" label="Description" min-width="200" show-overflow-tooltip />
      <el-table-column label="Actions" width="220" fixed="right">
        <template #default="{ row }">
          <el-button v-if="canView" type="info" link size="small" @click="openView(row)">View</el-button>
          <el-button v-if="canUpdate" type="primary" link size="small" @click="openEdit(row)">Edit</el-button>
          <el-button v-if="canDelete" type="danger" link size="small" @click="confirmDelete(row)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-if="canView"
      class="pagination"
      v-model:current-page="page"
      v-model:page-size="pageSize"
      :total="totalFiltered"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next"
      @size-change="handlePageSizeChange"
    />

    <p v-if="canView && !canCreate && !canUpdate && !canDelete" class="hint">
      View only. Assign permission:create / permission:update / permission:delete to manage records.
    </p>

    <el-dialog
      v-model="showDialog"
      :title="dialogMode === 'create' ? 'Add Permission' : 'Edit Permission'"
      width="520px"
      destroy-on-close
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="130px">
        <el-form-item label="Permission code" prop="permission_code">
          <el-input
            v-model="form.permission_code"
            maxlength="100"
            show-word-limit
            placeholder="e.g. report:view"
          />
        </el-form-item>
        <el-form-item label="Display name" prop="permission_name">
          <el-input v-model="form.permission_name" maxlength="100" show-word-limit placeholder="e.g. View reports" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" maxlength="255" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">Cancel</el-button>
        <el-button
          v-if="dialogMode === 'create' ? canCreate : canUpdate"
          type="primary"
          :loading="submitLoading"
          @click="submit"
        >
          Save
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showViewDialog" title="Permission detail" width="480px" destroy-on-close>
      <template v-if="viewDetail">
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="ID">{{ viewDetail.id }}</el-descriptions-item>
          <el-descriptions-item label="Code">{{ viewDetail.permission_code }}</el-descriptions-item>
          <el-descriptions-item label="Name">{{ viewDetail.permission_name }}</el-descriptions-item>
          <el-descriptions-item label="Description">{{ viewDetail.description || '—' }}</el-descriptions-item>
        </el-descriptions>
      </template>
      <template v-else>
        <p class="hint">Loading…</p>
      </template>
      <template #footer>
        <el-button type="primary" @click="showViewDialog = false">Close</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.permission-management {
  padding: 16px;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}
.header h2 {
  margin: 0;
  font-size: 18px;
}
.header-actions {
  display: flex;
  gap: 8px;
}
.filter-card {
  margin-bottom: 16px;
}
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
.hint {
  margin-top: 12px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
.hint.warn {
  color: var(--el-color-warning);
}
</style>
