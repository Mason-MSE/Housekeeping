<template>
  <div class="notification-container">
    <el-badge :value="unreadCount" :max="99" v-if="unreadCount > 0">
      <el-button 
        type="primary" 
        icon="Bell" 
        circle 
        @click="showNotifications"
      />
    </el-badge>
    <el-button 
      v-else
      type="primary" 
      icon="Bell" 
      circle 
      @click="showNotifications"
    />

    <el-drawer
      v-model="drawerVisible"
      title="Notifications"
      direction="rtl"
      size="40%"
    >
      <div class="notification-list">
        <div 
          v-for="notification in notifications" 
          :key="notification.id"
          class="notification-item"
          :class="{ unread: notification.is_read === 0 }"
          @click="markAsRead(notification.id)"
        >
          <div class="notification-header">
            <span class="notification-title">{{ notification.title }}</span>
            <span class="notification-time">{{ formatTime(notification.create_time) }}</span>
          </div>
          <div class="notification-content">{{ notification.content }}</div>
          <div class="notification-footer">
            <el-tag 
              :type="getTagType(notification.type)"
              size="small"
            >
              {{ notification.type }}
            </el-tag>
          </div>
        </div>
        <div v-if="notifications.length === 0" class="no-notifications">
          No notifications
        </div>
      </div>
      
      <template #footer>
        <div class="drawer-footer">
          <el-button @click="markAllAsRead" :disabled="unreadCount === 0">
            Mark all as read
          </el-button>
          <el-button type="primary" @click="refresh">Refresh</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useNotificationStore } from '@/stores/modules/notification'
import { ElMessage } from 'element-plus'

const notificationStore = useNotificationStore()
// Whether the notification drawer is open
const drawerVisible = ref(false)

// Returns the list of notifications from the store
const notifications = computed(() => notificationStore.notifications)
// Returns the unread notification count from the store
const unreadCount = computed(() => notificationStore.unreadCount)

// Timer interval for periodic notification refresh
let refreshInterval = null

// Lifecycle hook: starts periodic notification refresh on mount
onMounted(() => {
  // Refresh notifications every 30 seconds
  refreshInterval = setInterval(refresh, 30000)
  refresh()
})

// Lifecycle hook: clears the refresh interval on unmount
onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})

// Fetches the latest notifications and unread count from the server
async function refresh() {
  try {
    await notificationStore.fetchNotifications({ page: 1, page_size: 20 })
    await notificationStore.fetchUnreadCount()
  } catch (error) {
    console.error('Failed to refresh notifications:', error)
    ElMessage.error('Failed to load notifications')
  }
}

// Opens the notification drawer
function showNotifications() {
  drawerVisible.value = true
}

// Marks a single notification as read by its ID
async function markAsRead(id) {
  try {
    await notificationStore.markAsRead(id)
  } catch (error) {
    console.error('Failed to mark notification as read:', error)
    ElMessage.error('Failed to mark as read')
  }
}

// Marks all notifications as read
async function markAllAsRead() {
  try {
    await notificationStore.markAllAsRead()
    ElMessage.success('All notifications marked as read')
  } catch (error) {
    console.error('Failed to mark all notifications as read:', error)
    ElMessage.error('Failed to mark all as read')
  }
}

// Formats a timestamp string into a locale date string
function formatTime(timeString) {
  const date = new Date(timeString)
  return date.toLocaleString()
}

// Maps notification type to the corresponding Element Plus tag type
function getTagType(type) {
  const typeMap = {
    'info': '',
    'success': 'success',
    'warning': 'warning',
    'error': 'danger'
  }
  return typeMap[type] || ''
}
</script>

<style scoped>
.notification-container {
  position: relative;
}

.notification-list {
  height: calc(100vh - 200px);
  overflow-y: auto;
}

.notification-item {
  padding: 16px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.3s;
}

.notification-item:hover {
  background-color: #f5f7fa;
}

.notification-item.unread {
  background-color: #ecf5ff;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.notification-title {
  font-weight: bold;
  font-size: 16px;
}

.notification-time {
  font-size: 12px;
  color: #999;
}

.notification-content {
  margin-bottom: 8px;
  color: #666;
}

.notification-footer {
  text-align: right;
}

.no-notifications {
  text-align: center;
  color: #999;
  padding: 40px 0;
}

.drawer-footer {
  display: flex;
  justify-content: space-between;
}
</style>