<template>
  <div class="data-table">
    <!-- 表格工具栏 -->
    <div class="table-toolbar" v-if="showToolbar">
      <div class="toolbar-left">
        <slot name="toolbar-left"></slot>
      </div>
      <div class="toolbar-right">
        <slot name="toolbar-right"></slot>
        <el-button 
          v-if="showRefresh" 
          :icon="Refresh" 
          @click="handleRefresh"
          :loading="loading"
        >
          Refresh
        </el-button>
      </div>
    </div>

    <!-- 表格主体 -->
    <el-table
      :data="tableData"
      :loading="loading"
      :border="border"
      :stripe="stripe"
      :height="height"
      @selection-change="handleSelectionChange"
      @sort-change="handleSortChange"
    >
      <slot></slot>
    </el-table>

    <!-- 分页 -->
    <div class="table-pagination" v-if="showPagination && pagination">
      <el-pagination
        v-model:current-page="pagination.current_page"
        v-model:page-size="pagination.page_size"
        :page-sizes="pageSizes"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Refresh } from '@element-plus/icons-vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  pagination: {
    type: Object,
    default: null
  },
  border: {
    type: Boolean,
    default: true
  },
  stripe: {
    type: Boolean,
    default: true
  },
  height: {
    type: [String, Number],
    default: 'auto'
  },
  showToolbar: {
    type: Boolean,
    default: true
  },
  showRefresh: {
    type: Boolean,
    default: true
  },
  showPagination: {
    type: Boolean,
    default: true
  },
  pageSizes: {
    type: Array,
    default: () => [10, 20, 50, 100]
  }
})

const emit = defineEmits([
  'refresh', 
  'selection-change', 
  'sort-change', 
  'page-size-change', 
  'current-change'
])

const tableData = computed(() => props.data)

function handleRefresh() {
  emit('refresh')
}

function handleSelectionChange(selection) {
  emit('selection-change', selection)
}

function handleSortChange(sort) {
  emit('sort-change', sort)
}

function handleSizeChange(size) {
  emit('page-size-change', size)
}

function handleCurrentChange(page) {
  emit('current-change', page)
}
</script>

<style scoped>
.data-table {
  width: 100%;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 0 10px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>