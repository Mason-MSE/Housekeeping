<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { roleApi, permissionApi } from '@/api'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'

const loading = ref(false)
const roles = ref<any[]>([])
const permissions = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const permissionCodes = ref<string[]>([])
const canView = computed(() => permissionCodes.value.includes('role:view'))
const canCreate = computed(() => permissionCodes.value.includes('role:create'))
const canUpdate = computed(() => permissionCodes.value.includes('role:update'))
const canDelete = computed(() => permissionCodes.value.includes('role:delete'))

const showPermissionDialog = ref(false)
const showMenuDialog = ref(false)
const showRoleDialog = ref(false)
const roleDialogMode = ref<'create' | 'edit'>('create')
const selectedRole = ref<any>(null)
const selectedPermissions = ref<number[]>([])
const selectedMenus = ref<number[]>([])
const allMenus = ref<any[]>([])
const loadingRef = ref(false)
const roleSubmitLoading = ref(false)

const roleFormRef = ref<FormInstance>()
const roleForm = reactive({
  id: null as number | null,
  role_name: '',
  role_code: '',
  description: ''
})

const roleRules: FormRules = {
  role_name: [{ required: true, message: 'Please enter role name', trigger: 'blur' }]
}

const pagedRoles = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return roles.value.slice(start, start + pageSize.value)
})

const loadRoles = async () => {
  loading.value = true
  try {
    const res = await roleApi.list()
    roles.value = Array.isArray(res) ? res : []
    total.value = roles.value.length
    const maxPage = Math.max(1, Math.ceil(total.value / pageSize.value) || 1)
    if (page.value > maxPage) page.value = maxPage
  } catch (e: any) {
    console.error('Failed to load roles:', e)
    ElMessage.error('Failed to load roles')
  } finally {
    loading.value = false
  }
}

const loadPermissions = async () => {
  try {
    const res = await permissionApi.list()
    permissions.value = res || []
  } catch (e) {
    console.error('Failed to load permissions:', e)
  }
}

const loadMenus = async () => {
  try {
    const res = await permissionApi.getMenus()
    allMenus.value = res || []
  } catch (e) {
    console.error('Failed to load menus:', e)
  }
}

const loadMyPermissions = async () => {
  try {
    const res = await permissionApi.getMyPermissions()
    permissionCodes.value = Array.isArray(res) ? res.map((p: any) => p.permission_code) : []
  } catch (e) {
    console.error('Failed to load my permissions:', e)
    permissionCodes.value = []
  }
}

const resetRoleForm = () => {
  roleForm.id = null
  roleForm.role_name = ''
  roleForm.role_code = ''
  roleForm.description = ''
  roleFormRef.value?.resetFields()
}

const openCreateRole = () => {
  roleDialogMode.value = 'create'
  resetRoleForm()
  showRoleDialog.value = true
}

const openEditRole = (row: any) => {
  roleDialogMode.value = 'edit'
  roleForm.id = row.id
  roleForm.role_name = row.role_name || ''
  roleForm.role_code = row.role_code || ''
  roleForm.description = row.description || ''
  showRoleDialog.value = true
}

const submitRole = async () => {
  if (!roleFormRef.value) return
  await roleFormRef.value.validate(async (valid) => {
    if (!valid) return
    roleSubmitLoading.value = true
    try {
      if (roleDialogMode.value === 'create') {
        const payload: Record<string, string | undefined> = {
          role_name: roleForm.role_name.trim()
        }
        const code = roleForm.role_code.trim()
        if (code) payload.role_code = code
        const desc = roleForm.description.trim()
        if (desc) payload.description = desc
        await roleApi.create(payload)
        ElMessage.success('Role created')
      } else if (roleForm.id != null) {
        const payload: Record<string, string | undefined> = {
          role_name: roleForm.role_name.trim(),
          role_code: roleForm.role_code.trim() || roleForm.role_name.trim(),
          description: roleForm.description.trim()
        }
        await roleApi.update(roleForm.id, payload)
        ElMessage.success('Role updated')
      }
      showRoleDialog.value = false
      await loadRoles()
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.detail || 'Save failed')
    } finally {
      roleSubmitLoading.value = false
    }
  })
}

const confirmDeleteRole = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `Delete role "${row.role_name}"? Users must be unassigned first.`,
      'Confirm delete',
      { type: 'warning', confirmButtonText: 'Delete', cancelButtonText: 'Cancel' }
    )
    await roleApi.delete(row.id)
    ElMessage.success('Role deleted')
    await loadRoles()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e?.response?.data?.detail || 'Delete failed')
    }
  }
}

const openPermissionDialog = async (role: any) => {
  selectedRole.value = role
  selectedPermissions.value = role.permissions?.map((p: any) => p.id) || []

  if (!selectedPermissions.value.length) {
    try {
      const res = await roleApi.getRolePermissions(role.id)
      selectedPermissions.value = res?.map((p: any) => p.id) || []
    } catch (e) {
      console.error('Failed to load role permissions:', e)
    }
  }

  showPermissionDialog.value = true
}

const openMenuDialog = async (role: any) => {
  selectedRole.value = role
  selectedMenus.value = []

  try {
    const res = await roleApi.getRoleMenus(role.id)
    selectedMenus.value = res?.map((m: any) => m.id) || []
  } catch (e) {
    console.error('Failed to load role menus:', e)
  }

  showMenuDialog.value = true
}

const savePermissions = async () => {
  if (!selectedRole.value) return
  loadingRef.value = true
  try {
    await roleApi.assignPermissions(selectedRole.value.id, selectedPermissions.value)
    ElMessage.success('Permissions updated successfully')
    showPermissionDialog.value = false
    loadRoles()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Failed to update permissions')
  } finally {
    loadingRef.value = false
  }
}

const saveMenus = async () => {
  if (!selectedRole.value) return
  loadingRef.value = true
  try {
    await roleApi.assignMenus(selectedRole.value.id, selectedMenus.value)
    ElMessage.success('Menus updated successfully')
    showMenuDialog.value = false
    await loadRoles()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Failed to update menus')
  } finally {
    loadingRef.value = false
  }
}

const handlePageSizeChange = () => {
  page.value = 1
}

onMounted(() => {
  loadMyPermissions()
  loadRoles()
  loadPermissions()
  loadMenus()
})
</script>

<template>
  <div class="role-management">
    <div class="header">
      <h2>Role Management</h2>
      <el-button v-if="canCreate" type="primary" @click="openCreateRole">Add Role</el-button>
    </div>

    <p v-if="!canView" class="hint warn">
      You need <strong>role:view</strong> to view and manage roles.
    </p>

    <el-table v-if="canView" :data="pagedRoles" v-loading="loading" stripe size="small">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="role_name" label="Role Name" min-width="120" />
      <el-table-column prop="role_code" label="Code" min-width="120">
        <template #default="{ row }">
          <span>{{ row.role_code || '—' }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="Description" min-width="160" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ row.description || '—' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="Permissions" min-width="160">
        <template #default="{ row }">
          <el-tag
            v-for="perm in row.permissions?.slice(0, 3)"
            :key="perm.id"
            size="small"
            type="info"
            style="margin-right: 4px; margin-bottom: 2px"
          >
            {{ perm.permission_name }}
          </el-tag>
          <el-tag v-if="row.permissions?.length > 3" size="small" type="info">
            +{{ row.permissions.length - 3 }}
          </el-tag>
          <span v-if="!row.permissions?.length" style="color: #999">—</span>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="Created" width="150" />
      <el-table-column label="Actions" width="280" fixed="right">
        <template #default="{ row }">
          <el-button v-if="canUpdate" size="small" type="primary" link @click="openEditRole(row)">Edit</el-button>
          <el-button v-if="canDelete" size="small" type="danger" link @click="confirmDeleteRole(row)">Delete</el-button>
          <el-button v-if="canUpdate" size="small" type="primary" link @click="openPermissionDialog(row)">Permissions</el-button>
          <el-button v-if="canUpdate" size="small" type="success" link @click="openMenuDialog(row)">Menus</el-button>
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

    <el-dialog
      v-model="showRoleDialog"
      :title="roleDialogMode === 'create' ? 'Add Role' : 'Edit Role'"
      width="480px"
      destroy-on-close
      @closed="resetRoleForm"
    >
      <el-form ref="roleFormRef" :model="roleForm" :rules="roleRules" label-width="110px">
        <el-form-item label="Role Name" prop="role_name">
          <el-input v-model="roleForm.role_name" placeholder="e.g. Supervisor" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="Role Code" prop="role_code">
          <el-input
            v-model="roleForm.role_code"
            placeholder="Optional; auto from name if empty"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input v-model="roleForm.description" type="textarea" :rows="3" maxlength="255" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRoleDialog = false">Cancel</el-button>
        <el-button
          v-if="roleDialogMode === 'create' ? canCreate : canUpdate"
          type="primary"
          :loading="roleSubmitLoading"
          @click="submitRole"
        >
          Save
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showPermissionDialog" title="Assign Permissions" width="600px">
      <div v-if="selectedRole" class="role-info">
        <p><strong>{{ selectedRole.role_name }}</strong></p>
      </div>
      <el-checkbox-group v-model="selectedPermissions" style="margin-top: 16px; max-height: 400px; overflow-y: auto">
        <el-checkbox
          v-for="perm in permissions"
          :key="perm.id"
          :value="perm.id"
          style="display: block; margin: 6px 0; width: 250px"
        >
          {{ perm.permission_name }} ({{ perm.permission_code }})
        </el-checkbox>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="showPermissionDialog = false">Cancel</el-button>
        <el-button v-if="canUpdate" type="primary" @click="savePermissions" :loading="loadingRef">Save</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showMenuDialog" title="Assign Menus" width="500px">
      <div v-if="selectedRole" class="role-info">
        <p><strong>{{ selectedRole.role_name }}</strong></p>
      </div>
      <el-checkbox-group v-model="selectedMenus" style="margin-top: 16px; max-height: 400px; overflow-y: auto">
        <el-checkbox
          v-for="menu in allMenus"
          :key="menu.id"
          :value="menu.id"
          style="display: block; margin: 6px 0; width: 200px"
        >
          {{ menu.menu_name }}
        </el-checkbox>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="showMenuDialog = false">Cancel</el-button>
        <el-button v-if="canUpdate" type="primary" @click="saveMenus" :loading="loadingRef">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.role-management {
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
.role-info {
  padding: 12px;
  background: #f5f7fa;
  border-radius: 4px;
}
.role-info p {
  margin: 4px 0;
  font-size: 14px;
}
</style>
