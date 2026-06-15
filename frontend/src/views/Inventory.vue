<script setup lang="ts">
import { ref, onMounted } from 'vue'

const inventoryList = ref<any[]>([])
const loading = ref(false)

onMounted(() => {
  loading.value = true
  setTimeout(() => {
    inventoryList.value = [
      { id: 1, name: 'Cleaning Supplies', quantity: 50, status: 'In Stock' },
      { id: 2, name: 'Towels', quantity: 100, status: 'In Stock' },
      { id: 3, name: 'Soap', quantity: 30, status: 'Low Stock' }
    ]
    loading.value = false
  }, 500)
})
</script>

<template>
  <div class="inventory-container">
    <h2>Inventory Management</h2>
    <el-table :data="inventoryList" v-loading="loading" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="Item Name" />
      <el-table-column prop="quantity" label="Quantity" width="150" />
      <el-table-column prop="status" label="Status" width="150">
        <template #default="{ row }">
          <el-tag :type="row.status === 'In Stock' ? 'success' : 'warning'">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.inventory-container {
  padding: 20px;
}
</style>
