<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { resourceApi } from '@/api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const resources = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)

const searchName = ref('')

const loadResources = async () => {
  loading.value = true
  try {
    const res = await resourceApi.list()
    resources.value = res || []
    total.value = res?.length || 0
  } catch (e: any) {
    console.error('Failed to load resources:', e)
    ElMessage.error('Failed to load resources')
  } finally {
    loading.value = false
  }
}

const filteredResources = () => {
  if (!searchName.value) return resources.value
  return resources.value.filter(r => 
    r.resource_name?.toLowerCase().includes(searchName.value.toLowerCase()) ||
    r.resource_link?.toLowerCase().includes(searchName.value.toLowerCase())
  )
}

const getMethodType = (method: string) => {
  const types: Record<string, string> = {
    'GET': 'success',
    'POST': 'primary',
    'PUT': 'warning',
    'DELETE': 'danger'
  }
  return types[method] || 'info'
}

onMounted(() => {
  loadResources()
})
</script>

<template>
  <div class="resource-management">
    <div class="header">
      <h2>Resource Management</h2>
      <el-input v-model="searchName" placeholder="Search resources..." clearable style="width: 200px" />
    </div>

    <el-table :data="filteredResources()" v-loading="loading" stripe size="small">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="resource_name" label="Resource Name" width="180" />
      <el-table-column prop="resource_link" label="API Path" min-width="250" />
      <el-table-column prop="resource_method" label="Method" width="80">
        <template #default="{ row }">
          <el-tag :type="getMethodType(row.resource_method)" size="small">{{ row.resource_method }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="create_time" label="Created" width="150" />
    </el-table>

    <el-pagination
      class="pagination"
      v-model:current-page="page"
      v-model:page-size="pageSize"
      :total="total"
      layout="total, prev, pager, next"
      @current-change="loadResources"
    />
  </div>
</template>

<style scoped>
.resource-management {
  padding: 16px;
}
.header {
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header h2 {
  margin: 0;
  font-size: 18px;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
