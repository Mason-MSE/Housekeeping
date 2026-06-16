<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { serviceTypeApi, permissionApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

// Loading state for the data table
const loading = ref(false)
// List of service type items
const items = ref<any[]>([])
// Current user's permission code list
const permissionCodes = ref<string[]>([])

// Dialog visibility for create/edit form
const dialogVisible = ref(false)
// ID of the service being edited, null when creating
const editingId = ref<number | null>(null)
// Form data for creating/editing a service type
const form = ref({
  type_name: '',
  description: '',
  price: 0 as number,
  market_price: null as number | null
})

// Whether user has permission to view service types
const canView = computed(() => permissionCodes.value.includes('cleaning_service:view'))
// Whether user has permission to create service types
const canCreate = computed(() => permissionCodes.value.includes('cleaning_service:create'))
// Whether user has permission to update service types
const canUpdate = computed(() => permissionCodes.value.includes('cleaning_service:update'))
// Whether user has permission to delete service types
const canDelete = computed(() => permissionCodes.value.includes('cleaning_service:delete'))

// Hide Actions column when user has neither update nor delete
const showActionsColumn = computed(() => canUpdate.value || canDelete.value)

// Dialog primary action: create needs create perm, edit needs update perm
const canSaveInDialog = computed(() => {
  if (editingId.value == null) {
    return canCreate.value
  }
  return canUpdate.value
})

// Load the current user's permission codes from the API
const loadMyPermissions = async () => {
  try {
    const res: unknown = await permissionApi.getMyPermissions()
    permissionCodes.value = Array.isArray(res)
      ? res.map((p: { permission_code?: string }) => p.permission_code).filter(Boolean) as string[]
      : []
  } catch {
    permissionCodes.value = []
  }
}

// Fetch the list of service types from the API
const loadList = async () => {
  if (!canView.value) return
  loading.value = true
  try {
    const res = await serviceTypeApi.list()
    items.value = Array.isArray(res) ? res : []
  } catch (e: any) {
    console.error(e)
    ElMessage.error(e?.response?.data?.detail || 'Failed to load service types')
  } finally {
    loading.value = false
  }
}

// Open the dialog for creating a new service type
const openCreate = () => {
  if (!canCreate.value) {
    ElMessage.warning('No permission to create')
    return
  }
  editingId.value = null
  form.value = { type_name: '', description: '', price: 0, market_price: null }
  dialogVisible.value = true
}

// Open the dialog for editing an existing service type
const openEdit = (row: any) => {
  if (!canUpdate.value) {
    ElMessage.warning('No permission to update')
    return
  }
  editingId.value = row.id ?? row.type_id
  form.value = {
    type_name: row.type_name || '',
    description: row.description || '',
    price: Number(row.price) || 0,
    market_price: row.market_price != null ? Number(row.market_price) : null
  }
  dialogVisible.value = true
}

// Save (create or update) a service type via the API
const save = async () => {
  if (editingId.value != null && !canUpdate.value) {
    ElMessage.warning('No permission to update')
    return
  }
  if (editingId.value == null && !canCreate.value) {
    ElMessage.warning('No permission to create')
    return
  }
  if (!form.value.type_name?.trim()) {
    ElMessage.warning('Name is required')
    return
  }
  const payload: any = {
    type_name: form.value.type_name.trim(),
    description: form.value.description?.trim() || null,
    price: Number(form.value.price) || 0,
    market_price:
      form.value.market_price != null && form.value.market_price !== ('' as unknown as number)
        ? Number(form.value.market_price)
        : null
  }
  try {
    if (editingId.value != null) {
      await serviceTypeApi.update(editingId.value, {
        type_name: payload.type_name,
        description: payload.description,
        price: payload.price,
        market_price: payload.market_price
      })
      ElMessage.success('Updated')
    } else {
      await serviceTypeApi.create(payload)
      ElMessage.success('Created')
    }
    dialogVisible.value = false
    await loadList()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Save failed')
  }
}

// Soft-delete a service type after user confirmation
const remove = async (row: any) => {
  if (!canDelete.value) {
    ElMessage.warning('No permission to delete')
    return
  }
  const id = row.id ?? row.type_id
  try {
    await ElMessageBox.confirm('Soft-delete this service type?', 'Confirm', { type: 'warning' })
    await serviceTypeApi.delete(id)
    ElMessage.success('Deleted')
    await loadList()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e?.response?.data?.detail || 'Delete failed')
    }
  }
}

// Format a numeric value as a currency string with 2 decimal places
const formatMoney = (v: unknown) => {
  const n = Number(v)
  return Number.isFinite(n) ? n.toFixed(2) : '—'
}

// Lifecycle hook: load permissions and service types on mount
onMounted(async () => {
  await loadMyPermissions()
  await loadList()
})
</script>

<template>
  <div class="admin-cleaning-services">
    <div class="page-header">
      <h2>Cleaning services (portal)</h2>
      <p class="subtitle">
        Maintain service names, descriptions, <strong>market price</strong> (reference) and
        <strong>current / promo price</strong> shown on the public portal and used for billing.
      </p>
    </div>

    <el-card v-if="!canView">
      <el-empty description="No permission (cleaning_service:view). Assign it in Role Management." />
    </el-card>

    <el-card v-else>
      <div class="toolbar">
        <el-button v-if="canCreate" type="primary" @click="openCreate">Add service</el-button>
        <el-button @click="loadList">Refresh</el-button>
      </div>

      <el-table v-loading="loading" :data="items" stripe style="width: 100%; margin-top: 16px">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="type_name" label="Name" min-width="160" />
        <el-table-column prop="description" label="Description" min-width="220" show-overflow-tooltip />
        <el-table-column label="Market" width="110">
          <template #default="{ row }">
            <span class="market">${{ formatMoney(row.market_price) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="Current / promo" width="130">
          <template #default="{ row }">
            <span class="promo">${{ formatMoney(row.price) }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="showActionsColumn" label="Actions" width="160" fixed="right">
          <template #default="{ row }">
            <el-button v-if="canUpdate" size="small" @click="openEdit(row)">Edit</el-button>
            <el-button v-if="canDelete" size="small" type="danger" plain @click="remove(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="editingId != null ? 'Edit service' : 'New service'"
      width="520px"
      destroy-on-close
    >
      <el-form label-position="top">
        <el-form-item label="Service name" required>
          <el-input v-model="form.type_name" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="form.description" type="textarea" :rows="3" maxlength="500" show-word-limit />
        </el-form-item>
        <el-form-item label="Market price (reference, optional)">
          <el-input-number v-model="form.market_price" :min="0" :step="5" :precision="2" style="width: 100%" />
          <div class="hint">Shown struck-through on the portal when higher than current price.</div>
        </el-form-item>
        <el-form-item label="Current / promo price (billing)" required>
          <el-input-number v-model="form.price" :min="0" :step="5" :precision="2" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button v-if="canSaveInDialog" type="primary" @click="save">Save</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.admin-cleaning-services {
  padding: 24px;
}
.page-header h2 {
  margin: 0 0 8px 0;
}
.subtitle {
  margin: 0 0 16px 0;
  color: #909399;
  line-height: 1.5;
}
.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
}
.market {
  color: #909399;
  text-decoration: line-through;
  font-size: 13px;
}
.promo {
  color: #00a885;
  font-weight: 600;
}
.hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
