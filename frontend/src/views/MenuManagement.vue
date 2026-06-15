<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue'
import { permissionApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const loading = ref(false)
const menus = ref<any[]>([])
const permissionCodes = ref<string[]>([])

const showDialog = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const submitLoading = ref(false)
const formRef = ref<FormInstance>()

const form = reactive({
  id: null as number | null,
  menu_name: '',
  path: '',
  component: '',
  parent_id: 0,
  sort: 0,
  icon: ''
})

const rules: FormRules = {
  menu_name: [{ required: true, message: 'Menu name required', trigger: 'blur' }]
}

const canCreate = computed(() => permissionCodes.value.includes('menu:create'))
const canUpdate = computed(() => permissionCodes.value.includes('menu:update'))
const canDelete = computed(() => permissionCodes.value.includes('menu:delete'))

const loadPermissions = async () => {
  try {
    const res = await permissionApi.getMyPermissions()
    permissionCodes.value = (res || []).map((p: any) => p.permission_code)
  } catch (e) {
    console.error(e)
    permissionCodes.value = []
  }
}

const loadMenus = async () => {
  loading.value = true
  try {
    const res = await permissionApi.getMenus()
    menus.value = Array.isArray(res) ? res : []
  } catch (e: any) {
    console.error(e)
    ElMessage.error(e?.response?.data?.detail || 'Failed to load menus')
    menus.value = []
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.id = null
  form.menu_name = ''
  form.path = ''
  form.component = ''
  form.parent_id = 0
  form.sort = 0
  form.icon = ''
  formRef.value?.resetFields()
}

const openCreate = () => {
  dialogMode.value = 'create'
  resetForm()
  showDialog.value = true
}

const openEdit = (row: any) => {
  dialogMode.value = 'edit'
  form.id = row.id
  form.menu_name = row.menu_name || ''
  form.path = row.path || ''
  form.component = row.component || ''
  form.parent_id = row.parent_id ?? 0
  form.sort = row.sort ?? 0
  form.icon = row.icon || ''
  showDialog.value = true
}

const submit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (ok) => {
    if (!ok) return
    submitLoading.value = true
    try {
      const payload = {
        menu_name: form.menu_name.trim(),
        path: form.path.trim() || undefined,
        component: form.component.trim() || undefined,
        parent_id: form.parent_id,
        sort: form.sort,
        icon: form.icon.trim() || undefined
      }
      if (dialogMode.value === 'create') {
        await permissionApi.createMenu(payload)
        ElMessage.success('Menu created')
      } else if (form.id != null) {
        await permissionApi.updateMenu(form.id, payload)
        ElMessage.success('Menu updated')
      }
      showDialog.value = false
      await loadMenus()
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.detail || 'Save failed')
    } finally {
      submitLoading.value = false
    }
  })
}

const confirmDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `Delete menu "${row.menu_name}"? It will be hidden from the sidebar; role assignments stay until edited.`,
      'Confirm delete',
      { type: 'warning', confirmButtonText: 'Delete', cancelButtonText: 'Cancel' }
    )
    await permissionApi.deleteMenu(row.id)
    ElMessage.success('Menu deleted')
    await loadMenus()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e?.response?.data?.detail || 'Delete failed')
    }
  }
}

onMounted(async () => {
  await loadPermissions()
  await loadMenus()
})
</script>

<template>
  <div class="menu-management">
    <div class="header">
      <h2>Menu Management</h2>
      <el-button v-if="canCreate" type="primary" @click="openCreate">Add Menu</el-button>
    </div>

    <el-table :data="menus" v-loading="loading" stripe size="small">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="menu_name" label="Name" min-width="140" />
      <el-table-column prop="path" label="Path" min-width="160" show-overflow-tooltip />
      <el-table-column prop="component" label="Component" min-width="140" show-overflow-tooltip />
      <el-table-column prop="parent_id" label="Parent ID" width="90" />
      <el-table-column prop="sort" label="Sort" width="70" />
      <el-table-column prop="icon" label="Icon" width="100" />
      <el-table-column label="Actions" width="160" fixed="right">
        <template #default="{ row }">
          <el-button v-if="canUpdate" type="primary" link size="small" @click="openEdit(row)">Edit</el-button>
          <el-button v-if="canDelete" type="danger" link size="small" @click="confirmDelete(row)">Delete</el-button>
        </template>
      </el-table-column>
    </el-table>

    <p v-if="!canCreate && !canUpdate && !canDelete" class="hint">
      You have view-only access. Assign menu:create, menu:update, and menu:delete to change menus.
    </p>

    <el-dialog
      v-model="showDialog"
      :title="dialogMode === 'create' ? 'Add Menu' : 'Edit Menu'"
      width="520px"
      destroy-on-close
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="Menu name" prop="menu_name">
          <el-input v-model="form.menu_name" maxlength="100" show-word-limit placeholder="e.g. Reports" />
        </el-form-item>
        <el-form-item label="Path" prop="path">
          <el-input v-model="form.path" maxlength="255" placeholder="e.g. /reports" />
        </el-form-item>
        <el-form-item label="Component" prop="component">
          <el-input v-model="form.component" maxlength="255" placeholder="Vue component name, e.g. Reports" />
        </el-form-item>
        <el-form-item label="Parent ID" prop="parent_id">
          <el-input-number v-model="form.parent_id" :min="0" :controls="true" />
        </el-form-item>
        <el-form-item label="Sort" prop="sort">
          <el-input-number v-model="form.sort" :min="0" :controls="true" />
        </el-form-item>
        <el-form-item label="Icon" prop="icon">
          <el-input v-model="form.icon" maxlength="100" placeholder="Element Plus icon name, e.g. House" />
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
  </div>
</template>

<style scoped>
.menu-management {
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
.hint {
  margin-top: 12px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
</style>
