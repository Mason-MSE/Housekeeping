<script setup lang="ts">
import { ref, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'

const props = defineProps<{
  visible: boolean
  cleaners: any[]
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'select', cleaner: any): void
  (e: 'search'): void
}>()

const search = ref('')
const sortBy = ref('')

watch(() => props.visible, (val) => {
  if (val) {
    search.value = ''
    sortBy.value = ''
  }
})

const handleSearch = () => {
  emit('search', { search: search.value, sort_by: sortBy.value })
}

const selectCleaner = (cleaner: any) => {
  emit('select', cleaner)
}

const closeDialog = () => {
  emit('update:visible', false)
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="emit('update:visible', $event)"
    title="Select Your Cleaner"
    width="700px"
  >
    <div class="cleaner-filters">
      <el-input
        v-model="search"
        placeholder="Search by name..."
        clearable
        style="width: 200px; margin-right: 10px"
        @clear="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select
        v-model="sortBy"
        placeholder="Sort by"
        style="width: 180px; margin-right: 10px"
        @change="handleSearch"
      >
        <el-option label="Default" value="" />
        <el-option label="Rating (High to Low)" value="rating_desc" />
        <el-option label="Rating (Low to High)" value="rating_asc" />
        <el-option label="Most Orders" value="orders_desc" />
        <el-option label="Least Orders" value="orders_asc" />
      </el-select>
      <el-button type="primary" @click="handleSearch">Search</el-button>
    </div>
    <div class="cleaner-list" style="margin-top: 15px">
      <div 
        v-for="cleaner in cleaners" 
        :key="cleaner.id" 
        class="cleaner-card"
        @click="selectCleaner(cleaner)"
      >
        <el-avatar :size="60" class="cleaner-avatar">
          {{ cleaner.full_name?.charAt(0) || 'C' }}
        </el-avatar>
        <div class="cleaner-info">
          <div class="cleaner-name">{{ cleaner.full_name }}</div>
          <div class="cleaner-stats">
            <el-rate 
              :model-value="cleaner.star_level" 
              disabled 
              :max="5"
              size="small"
            />
            <span class="orders-count">{{ cleaner.total_orders }} orders</span>
            <span class="rating-score">{{ cleaner.total_rating }} rating</span>
          </div>
        </div>
      </div>
      <el-empty v-if="cleaners.length === 0" description="No cleaners found" />
    </div>
  </el-dialog>
</template>

<style scoped>
.cleaner-filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.cleaner-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 400px;
  overflow-y: auto;
}

.cleaner-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.cleaner-card:hover {
  border-color: #409eff;
  background: #f0f9ff;
}

.cleaner-avatar {
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
}

.cleaner-info {
  flex: 1;
}

.cleaner-name {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.cleaner-stats {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.orders-count, .rating-score {
  color: #67c23a;
}
</style>
