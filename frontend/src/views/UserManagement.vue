<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import { userApi, roleApi, permissionApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import type { FormInstance, FormRules } from 'element-plus'

// User store instance
const userStore = useUserStore()
// Computed current user ID
const currentUserId = computed(() => userStore.userInfo?.id ?? userStore.userInfo?.userId)

// Loading state for data fetching
const loading = ref(false)
// List of users
const users = ref<any[]>([])
// List of roles
const roles = ref<any[]>([])
// Total count of users
const total = ref(0)
// Pagination page number
const page = ref(1)
// Pagination page size
const pageSize = ref(20)

// Current user's permission codes
const permissionCodes = ref<string[]>([])
// Computed whether the user has user:view
const canView = computed(() => permissionCodes.value.includes('user:view'))
// Computed whether the user has user:create
const canCreate = computed(() => permissionCodes.value.includes('user:create'))
// Computed whether the user has user:update
const canUpdate = computed(() => permissionCodes.value.includes('user:update'))
// Computed whether the user has user:delete
const canDelete = computed(() => permissionCodes.value.includes('user:delete'))

// Dialog visibility for role assignment
const showRoleDialog = ref(false)
// User selected for role assignment
const selectedUser = ref<any>(null)
// Selected role IDs for the user
const selectedRoles = ref<number[]>([])
// Loading state for role operations
const roleLoading = ref(false)

// Dialog visibility for create user
const showCreateDialog = ref(false)
// Dialog visibility for edit user
const showEditDialog = ref(false)
// Loading state for create submission
const createSubmitLoading = ref(false)
// Loading state for edit submission
const editSubmitLoading = ref(false)
// Form reference for create validation
const createFormRef = ref<FormInstance>()
// Form reference for edit validation
const editFormRef = ref<FormInstance>()

// Reactive form model for creating a user
const createForm = reactive({
  username: '',
  password: '',
  full_name: '',
  email: '',
  phone: '',
  status: 1,
  role_ids: [] as number[]
})

// Reactive form model for editing a user
const editForm = reactive({
  id: 0,
  username: '',
  password: '',
  full_name: '',
  email: '',
  phone: '',
  status: 1
})

const createRules: FormRules = {
  username: [{ required: true, message: 'Username required', trigger: 'blur' }],
  password: [{ required: true, message: 'Password required', trigger: 'blur' }]
}

const editRules: FormRules = {
  full_name: [{ required: true, message: 'Full name required', trigger: 'blur' }]
}

// Computed paginated slice of users
const pagedUsers = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return users.value.slice(start, start + pageSize.value)
})

// Load the current user's permission codes
const loadMyPermissions = async () => {
  try {
    const res = await permissionApi.getMyPermissions()
    permissionCodes.value = Array.isArray(res) ? res.map((p: any) => p.permission_code) : []
  } catch (e) {
    console.error('Failed to load my permissions:', e)
    permissionCodes.value = []
  }
}

// Load all users from the API
const loadUsers = async () => {
  loading.value = true
  try {
    const res = await userApi.list()
    users.value = Array.isArray(res) ? res : []
    total.value = users.value.length
    const maxPage = Math.max(1, Math.ceil(total.value / pageSize.value) || 1)
    if (page.value > maxPage) page.value = maxPage
  } catch (e: any) {
    console.error('Failed to load users:', e)
    ElMessage.error('Failed to load users')
  } finally {
    loading.value = false
  }
}

// Load all roles from the API
const loadRoles = async () => {
  try {
    const res = await roleApi.list()
    roles.value = res || []
  } catch (e) {
    console.error('Failed to load roles:', e)
  }
}

// Reset the create user form to defaults
const resetCreateForm = () => {
  createForm.username = ''
  createForm.password = ''
  createForm.full_name = ''
  createForm.email = ''
  createForm.phone = ''
  createForm.status = 1
  createForm.role_ids = []
  createFormRef.value?.resetFields()
}

// Open the create user dialog
const openCreate = () => {
  resetCreateForm()
  showCreateDialog.value = true
}

// Submit the create user form
const submitCreate = async () => {
  if (!createFormRef.value) return
  await createFormRef.value.validate(async (ok) => {
    if (!ok) return
    createSubmitLoading.value = true
    try {
      await userApi.createManaged({
        username: createForm.username.trim(),
        password: createForm.password,
        full_name: createForm.full_name.trim() || undefined,
        email: createForm.email.trim() || undefined,
        phone: createForm.phone.trim() || undefined,
        status: createForm.status,
        role_ids: createForm.role_ids
      })
      ElMessage.success('User created')
      showCreateDialog.value = false
      await loadUsers()
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.detail || 'Create failed')
    } finally {
      createSubmitLoading.value = false
    }
  })
}

// Open the edit user dialog with row data
const openEdit = (row: any) => {
  editForm.id = row.id
  editForm.username = row.username || ''
  editForm.password = ''
  editForm.full_name = row.full_name || ''
  editForm.email = row.email || ''
  editForm.phone = row.phone || ''
  editForm.status = row.status === 1 ? 1 : 0
  showEditDialog.value = true
}

// Submit the edit user form
const submitEdit = async () => {
  if (!editFormRef.value) return
  await editFormRef.value.validate(async (ok) => {
    if (!ok) return
    if (editForm.status !== 1 && Number(editForm.id) === Number(currentUserId.value)) {
      ElMessage.warning('You cannot disable your own account')
      return
    }
    editSubmitLoading.value = true
    try {
      const payload: Record<string, unknown> = {
        full_name: editForm.full_name.trim(),
        email: editForm.email.trim() || null,
        phone: editForm.phone.trim() || null,
        status: editForm.status
      }
      if (editForm.password.trim()) {
        payload.password = editForm.password
      }
      await userApi.update(editForm.id, payload)
      ElMessage.success('User updated')
      showEditDialog.value = false
      await loadUsers()
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.detail || 'Update failed')
    } finally {
      editSubmitLoading.value = false
    }
  })
}

// Soft-delete a user after confirmation
const confirmDelete = async (row: any) => {
  if (Number(row.id) === Number(currentUserId.value)) {
    ElMessage.warning('Cannot delete your own account')
    return
  }
  try {
    await ElMessageBox.confirm(
      `Soft-delete user "${row.username}"? They will no longer appear in lists.`,
      'Confirm',
      { type: 'warning' }
    )
    await userApi.delete(row.id)
    ElMessage.success('User deleted')
    await loadUsers()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e?.response?.data?.detail || 'Delete failed')
    }
  }
}

// Toggle a user's active/disabled status
const toggleUserStatus = async (row: any, active: boolean) => {
  const next = active ? 1 : 0
  if (next !== 1 && Number(row.id) === Number(currentUserId.value)) {
    ElMessage.warning('Cannot disable your own account')
    await loadUsers()
    return
  }
  try {
    await userApi.update(row.id, { status: next })
    ElMessage.success(active ? 'User enabled' : 'User disabled')
    await loadUsers()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Update failed')
    await loadUsers()
  }
}

// Open the dialog to assign roles to a user
const openRoleDialog = async (user: any) => {
  selectedUser.value = user
  selectedRoles.value = user.roles?.map((r: any) => r.id) || []
  showRoleDialog.value = true
}

// Save the role assignments for the selected user
const saveRoles = async () => {
  if (!selectedUser.value) return
  roleLoading.value = true
  try {
    await userApi.updateRoles(selectedUser.value.id, selectedRoles.value)
    ElMessage.success('Roles updated successfully')
    showRoleDialog.value = false
    loadUsers()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Failed to update roles')
  } finally {
    roleLoading.value = false
  }
}

// Get the Element tag type for a given user status
const getStatusType = (status: number) => {
  return status === 1 ? 'success' : 'info'
}

// Get the display label for a given user status
const getStatusLabel = (status: number) => {
  return status === 1 ? 'Active' : 'Disabled'
}

// Reset to page 1 when page size changes
const handlePageSizeChange = () => {
  page.value = 1
}

// Lifecycle hook: load permissions, users, and roles on mount
onMounted(() => {
  loadMyPermissions()
  loadUsers()
  loadRoles()
})
</script>

<template>
  <div class="user-management">
    <div class="header">
      <h2>User Management</h2>
      <el-button v-if="canCreate" type="primary" @click="openCreate">Add User</el-button>
    </div>

    <p v-if="!canView" class="hint warn">
      You need <strong>user:view</strong> to view and manage users.
    </p>

    <el-table v-if="canView" :data="pagedUsers" v-loading="loading" stripe size="small">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="username" label="Username" width="120" />
      <el-table-column prop="full_name" label="Full Name" width="140" />
      <el-table-column prop="email" label="Email" min-width="160" show-overflow-tooltip />
      <el-table-column prop="phone" label="Phone" width="120" />
      <el-table-column label="Status" width="200">
        <template #default="{ row }">
          <div class="status-cell">
            <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
            <el-switch
              v-if="canUpdate && Number(row.id) !== Number(currentUserId)"
              :model-value="row.status === 1"
              inline-prompt
              active-text="On"
              inactive-text="Off"
              style="margin-left: 8px"
              @change="(v: boolean) => toggleUserStatus(row, v)"
            />
          </div>
        </template>
      </el-table-column>
      <el-table-column label="Roles" min-width="150">
        <template #default="{ row }">
          <el-tag v-for="r in row.roles" :key="r.id" size="small" type="info" style="margin-right: 4px">
            {{ r.role_name }}
          </el-tag>
          <span v-if="!row.roles?.length" style="color: #999">-</span>
        </template>
      </el-table-column>
      <el-table-column label="Actions" width="280" fixed="right">
        <template #default="{ row }">
          <el-button v-if="canUpdate" size="small" type="primary" link @click="openEdit(row)">Edit</el-button>
          <el-button v-if="canUpdate" size="small" type="primary" link @click="openRoleDialog(row)">Roles</el-button>
          <el-button
            v-if="canDelete && Number(row.id) !== Number(currentUserId)"
            size="small"
            type="danger"
            link
            @click="confirmDelete(row)"
          >
            Delete
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-if="canView"
      class="pagination"
      v-model:current-page="page"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next"
      @size-change="handlePageSizeChange"
    />

    <el-dialog v-model="showCreateDialog" title="Add User" width="520px" destroy-on-close @closed="resetCreateForm">
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="110px">
        <el-form-item label="Username" prop="username">
          <el-input v-model="createForm.username" maxlength="50" show-word-limit autocomplete="off" />
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input v-model="createForm.password" type="password" show-password autocomplete="new-password" />
        </el-form-item>
        <el-form-item label="Full Name">
          <el-input v-model="createForm.full_name" maxlength="100" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="createForm.email" maxlength="100" />
        </el-form-item>
        <el-form-item label="Phone">
          <el-input v-model="createForm.phone" maxlength="20" />
        </el-form-item>
        <el-form-item label="Status">
          <el-radio-group v-model="createForm.status">
            <el-radio :value="1">Active</el-radio>
            <el-radio :value="0">Disabled</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Roles">
          <el-checkbox-group v-model="createForm.role_ids" class="role-checks">
            <el-checkbox v-for="r in roles" :key="r.id" :value="r.id">{{ r.role_name }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">Cancel</el-button>
        <el-button v-if="canCreate" type="primary" :loading="createSubmitLoading" @click="submitCreate">Create</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showEditDialog" title="Edit User" width="520px" destroy-on-close>
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-width="110px">
        <el-form-item label="Username">
          <el-input v-model="editForm.username" disabled />
        </el-form-item>
        <el-form-item label="New password">
          <el-input
            v-model="editForm.password"
            type="password"
            show-password
            placeholder="Leave blank to keep current"
            autocomplete="new-password"
          />
        </el-form-item>
        <el-form-item label="Full Name" prop="full_name">
          <el-input v-model="editForm.full_name" maxlength="100" />
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="editForm.email" maxlength="100" />
        </el-form-item>
        <el-form-item label="Phone">
          <el-input v-model="editForm.phone" maxlength="20" />
        </el-form-item>
        <el-form-item label="Status">
          <el-radio-group v-model="editForm.status" :disabled="Number(editForm.id) === Number(currentUserId)">
            <el-radio :value="1">Active</el-radio>
            <el-radio :value="0">Disabled</el-radio>
          </el-radio-group>
          <div v-if="Number(editForm.id) === Number(currentUserId)" class="hint">You cannot disable yourself.</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">Cancel</el-button>
        <el-button v-if="canUpdate" type="primary" :loading="editSubmitLoading" @click="submitEdit">Save</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showRoleDialog" title="Assign Roles" width="400px">
      <div v-if="selectedUser" class="user-info">
        <p><strong>{{ selectedUser.username }}</strong></p>
        <p>{{ selectedUser.full_name }}</p>
      </div>
      <el-checkbox-group v-model="selectedRoles" style="margin-top: 16px">
        <el-checkbox v-for="role in roles" :key="role.id" :value="role.id" style="display: block; margin: 8px 0">
          {{ role.role_name }}
        </el-checkbox>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="showRoleDialog = false">Cancel</el-button>
        <el-button v-if="canUpdate" type="primary" @click="saveRoles" :loading="roleLoading">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.user-management {
  padding: 16px;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}
.header h2 {
  margin: 0;
  font-size: 18px;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
.user-info {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}
.user-info p {
  margin: 4px 0;
  font-size: 14px;
}
.status-cell {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
}
.role-checks {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.hint {
  font-size: 12px;
  color: #909399;
  margin-top: 6px;
}
</style>
