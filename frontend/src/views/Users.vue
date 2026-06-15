<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { userApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const userRoles = computed(() => userStore.userInfo?.roles || [userStore.userInfo?.role || 'guest'])

onMounted(() => {
  if (!userRoles.value.includes('admin')) {
    ElMessage.warning('Access denied')
    router.push('/')
  }
})

const loading = ref(false)
const userList = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('')
const formData = ref({
  id: null,
  username: '',
  password: '',
  full_name: '',
  email: '',
  phone: '',
  role: 'guest'
})

const rules = {
  username: [{ required: true, message: 'Please enter username', trigger: 'blur' }],
  full_name: [{ required: true, message: 'Please enter full name', trigger: 'blur' }],
  role: [{ required: true, message: 'Please select role', trigger: 'change' }]
}

const roleOptions = [
  { value: 'admin', label: 'Admin' },
  { value: 'guest', label: 'Guest' },
  { value: 'cleaner', label: 'Cleaner' }
]

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await userApi.list()
    userList.value = res || []
  } catch (error) {
    console.error('Failed to fetch users:', error)
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = 'Add User'
  formData.value = { id: null, username: '', password: '', full_name: '', email: '', phone: '', role: 'guest' }
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  dialogTitle.value = 'Edit User'
  formData.value = { ...row, password: '' }
  dialogVisible.value = true
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('Are you sure to delete this user?', 'Confirm', {
      confirmButtonText: 'Yes',
      cancelButtonText: 'Cancel',
      type: 'warning'
    })
    await userApi.delete(row.id)
    ElMessage.success('Deleted successfully')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Delete failed')
    }
  }
}

const handleSubmit = async () => {
  try {
    const data = { ...formData.value }
    if (!data.password) {
      delete data.password
    }
    if (data.id) {
      await userApi.update(data.id, data)
      ElMessage.success('Updated successfully')
    } else {
      await userApi.create(data)
      ElMessage.success('Created successfully')
    }
    dialogVisible.value = false
    fetchUsers()
  } catch (error) {
    ElMessage.error('Operation failed')
  }
}

onMounted(() => {
  fetchUsers()
})

const getRoleType = (role: string) => {
  const map: Record<string, string> = {
    admin: 'danger',
    guest: 'success',
    cleaner: 'warning'
  }
  return map[role] || 'info'
}
</script>

<template>
  <div class="users-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>User List</span>
          <el-button type="primary" @click="handleAdd">Add User</el-button>
        </div>
      </template>

      <el-table :data="userList" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="Username" width="120" />
        <el-table-column prop="full_name" label="Full Name" width="120" />
        <el-table-column prop="role" label="Role" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">
              {{ roleOptions.find(r => r.value === row.role)?.label || row.role }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="Email" min-width="180" />
        <el-table-column prop="phone" label="Phone" width="130" />
        <el-table-column prop="status" label="Status" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? 'Active' : 'Disabled' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Action" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">Edit</el-button>
            <el-button type="danger" link @click="handleDelete(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" destroy-on-close>
      <el-form :model="formData" :rules="rules" label-width="80px">
        <el-form-item label="Username" prop="username">
          <el-input v-model="formData.username" :disabled="!!formData.id" />
        </el-form-item>
        <el-form-item v-if="!formData.id" label="Password" prop="password">
          <el-input v-model="formData.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="Full Name" prop="full_name">
          <el-input v-model="formData.full_name" />
        </el-form-item>
        <el-form-item label="Role" prop="role">
          <el-select v-model="formData.role" style="width: 100%">
            <el-option v-for="r in roleOptions" :key="r.value" :label="r.label" :value="r.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Email">
          <el-input v-model="formData.email" />
        </el-form-item>
        <el-form-item label="Phone">
          <el-input v-model="formData.phone" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleSubmit">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
