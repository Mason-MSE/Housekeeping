<script lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { notificationApi } from '@/api'

export default {
  name: 'Notifications',
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    
    // List of notifications
    const notifications = ref([])
    // Loading state for data fetching
    const loading = ref(false)
    // Array of selected notification IDs
    const selectedIds = ref([])
    // Pagination current page
    const currentPage = ref(1)
    // Pagination page size
    const pageSize = ref(10)
    // Total count of notifications
    const total = ref(0)
    // Filter form model
    const filterForm = ref({
      type: null,
      is_read: null,
      title: ''
    })
    
    const typeOptions = [
      { value: null, label: 'All' },
      { value: 'info', label: 'Info' },
      { value: 'warning', label: 'Warning' },
      { value: 'success', label: 'Success' }
    ]
    
    const isReadOptions = [
      { value: null, label: 'All' },
      { value: 0, label: 'Unread' },
      { value: 1, label: 'Read' }
    ]
    
    // Fetch notifications from the API with pagination and filters
    const fetchNotifications = async () => {
      try {
        loading.value = true
        const params = {
          page: currentPage.value,
          page_size: pageSize.value,
          type: filterForm.value.type ?? undefined,
          is_read: filterForm.value.is_read ?? undefined,
          title: filterForm.value.title || undefined
        }
        const res = await notificationApi.paginated(params)
        notifications.value = res?.items ?? []
        total.value = res?.total ?? 0
      } catch (e) {
        console.error('Failed to fetch notifications', e)
        ElMessage.error('Failed to fetch notifications')
      } finally {
        loading.value = false
      }
    }
    
    // Mark a single notification as read
    const handleRead = async (id: number) => {
      try {
        await notificationApi.markAsRead(id)
        const notification = notifications.value.find(n => n.id === id)
        if (notification) {
          notification.is_read = 1
        }
        ElMessage.success('Marked as read')
        fetchNotifications()
      } catch (e) {
        console.error('Failed to mark as read', e)
        ElMessage.error('Failed to mark as read')
      }
    }
    
    // Mark all notifications as read
    const handleReadAll = async () => {
      try {
        await notificationApi.markAllAsRead()
        notifications.value.forEach(n => n.is_read = 1)
        ElMessage.success('All notifications marked as read')
        fetchNotifications()
      } catch (e) {
        console.error('Failed to mark all as read', e)
        ElMessage.error('Failed to mark all as read')
      }
    }
    
    // Delete a single notification after confirmation
    const handleDelete = async (id: number) => {
      try {
        await ElMessageBox.confirm('Are you sure to delete this notification?', 'Confirm', {
          confirmButtonText: 'Delete',
          cancelButtonText: 'Cancel',
          type: 'warning'
        })
        
        await notificationApi.delete(id)
        ElMessage.success('Notification deleted')
        fetchNotifications()
      } catch (e) {
        if (e !== 'cancel') {
          console.error('Failed to delete notification', e)
          ElMessage.error('Failed to delete notification')
        }
      }
    }
    
    // Delete all selected notifications after confirmation
    const handleDeleteSelected = async () => {
      if (selectedIds.value.length === 0) {
        ElMessage.warning('No notifications selected')
        return
      }
      
      try {
        await ElMessageBox.confirm('Are you sure to delete selected notifications?', 'Confirm', {
          confirmButtonText: 'Delete',
          cancelButtonText: 'Cancel',
          type: 'warning'
        })
        
        await Promise.all(selectedIds.value.map(id => notificationApi.delete(id)))
        ElMessage.success('Notifications deleted')
        selectedIds.value = []
        fetchNotifications()
      } catch (e) {
        if (e !== 'cancel') {
          console.error('Failed to delete notifications', e)
          ElMessage.error('Failed to delete notifications')
        }
      }
    }
    
    // Mark all selected notifications as read
    const handleReadSelected = async () => {
      if (selectedIds.value.length === 0) {
        ElMessage.warning('No notifications selected')
        return
      }
      
      try {
        await Promise.all(selectedIds.value.map(id => notificationApi.markAsRead(id)))
        ElMessage.success('Notifications marked as read')
        
        notifications.value.forEach(n => {
          if (selectedIds.value.includes(n.id)) {
            n.is_read = 1
          }
        })
        selectedIds.value = []
        fetchNotifications()
      } catch (e) {
        console.error('Failed to mark as read', e)
        ElMessage.error('Failed to mark as read')
      }
    }
    
    // Toggle a single notification selection by ID
    const toggleSelection = (row: any) => {
      const index = selectedIds.value.indexOf(row.id)
      if (index > -1) {
        selectedIds.value.splice(index, 1)
      } else {
        selectedIds.value.push(row.id)
      }
    }
    
    // Handle select-all checkbox change
    const selectAll = (selection: any) => {
      if (selection.length > 0) {
        selectedIds.value = notifications.value.map(n => n.id)
      } else {
        selectedIds.value = []
      }
    }
    
    // Format a date string into a human-readable relative time
    const formatTime = (time: string) => {
      if (!time) return ''
      const date = new Date(time)
      const now = new Date()
      const diff = now.getTime() - date.getTime()
      const minutes = Math.floor(diff / 60000)
      const hours = Math.floor(diff / 3600000)
      const days = Math.floor(diff / 86400000)
      
      if (minutes < 1) return 'Just now'
      if (minutes < 60) return `${minutes}m ago`
      if (hours < 24) return `${hours}h ago`
      if (days < 7) return `${days}d ago`
      return date.toLocaleDateString()
    }
    
    // Get the icon name for a given notification type
    const getNotificationIcon = (type: string) => {
      switch (type) {
        case 'warning':
          return 'Warning'
        case 'success':
          return 'CircleCheck'
        default:
          return 'Bell'
      }
    }
    
    // Get the color for a given notification type
    const getNotificationColor = (type: string) => {
      switch (type) {
        case 'warning':
          return '#e6a23c'
        case 'success':
          return '#67c23a'
        default:
          return '#909399'
      }
    }
    
    // Get the count of unread notifications
    const getUnreadCount = () => {
      return notifications.value.filter(n => n.is_read === 0).length
    }
    
    // Handle pagination page change
    const handlePageChange = (page: number) => {
      currentPage.value = page
      fetchNotifications()
    }
    
    // Handle pagination page size change
    const handleSizeChange = (size: number) => {
      pageSize.value = size
      currentPage.value = 1
      fetchNotifications()
    }
    
    // Apply filters and reload notifications
    const handleFilter = () => {
      currentPage.value = 1
      fetchNotifications()
    }
    
    // Reset all filters to default and reload
    const handleReset = () => {
      filterForm.value = { type: null, is_read: null, title: '' }
      currentPage.value = 1
      fetchNotifications()
    }
    
    // Lifecycle hook: fetch notifications on component mount
    onMounted(() => {
      fetchNotifications()
    })
    
    return {
      notifications,
      loading,
      selectedIds,
      currentPage,
      pageSize,
      total,
      filterForm,
      typeOptions,
      isReadOptions,
      handleRead,
      handleReadAll,
      handleDelete,
      handleDeleteSelected,
      handleReadSelected,
      toggleSelection,
      selectAll,
      formatTime,
      getNotificationIcon,
      getNotificationColor,
      getUnreadCount,
      handlePageChange,
      handleSizeChange,
      handleFilter,
      handleReset
    }
  }
}
</script>

<template>
  <div class="notifications-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>Notifications</span>
          <div>
            <el-button type="primary" link @click="handleReadAll">Mark All Read</el-button>
            <el-button type="danger" link @click="handleDeleteSelected" :disabled="selectedIds.length === 0">
              Delete Selected
            </el-button>
            <el-button type="success" link @click="handleReadSelected" :disabled="selectedIds.length === 0">
              Mark Selected Read
            </el-button>
          </div>
        </div>
      </template>
      
      <el-row :gutter="16" class="filter-row">
        <el-col :span="6">
          <el-input v-model="filterForm.title" placeholder="Search title" clearable @keyup.enter="handleFilter" />
        </el-col>
        <el-col :span="5">
          <el-select v-model="filterForm.type" placeholder="Type" clearable style="width: 100%">
            <el-option v-for="opt in typeOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-col>
        <el-col :span="5">
          <el-select v-model="filterForm.is_read" placeholder="Status" clearable style="width: 100%">
            <el-option v-for="opt in isReadOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" @click="handleFilter">Search</el-button>
          <el-button @click="handleReset">Reset</el-button>
        </el-col>
      </el-row>
      
      <el-table :data="notifications" v-loading="loading" style="width: 100%" @selection-change="selectAll">
        <el-table-column type="selection" width="50" />
        <el-table-column prop="title" label="Title" min-width="150" />
        <el-table-column prop="content" label="Content" min-width="200" />
        <el-table-column prop="type" label="Type" width="100">
          <template #default="{ row }">
            <el-tag :color="getNotificationColor(row.type)" effect="dark" size="small">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_read" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_read === 1 ? 'success' : 'warning'" size="small">
              {{ row.is_read === 1 ? 'Read' : 'Unread' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="Time" width="150">
          <template #default="{ row }">
            {{ formatTime(row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleRead(row.id)" v-if="row.is_read === 0">Read</el-button>
            <el-button type="danger" link @click="handleDelete(row.id)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.notifications-page {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.filter-row {
  margin-bottom: 16px;
}
.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
