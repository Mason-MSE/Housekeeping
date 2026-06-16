import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificationApi } from '@/api'

// Pinia store managing notification state (list, unread count)
export const useNotificationStore = defineStore('notification', () => {
  // List of all notifications
  const notifications = ref([])
  // Count of unread notifications
  const unreadCount = ref(0)

  // Computed list of notifications that are not yet read
  const unreadNotifications = computed(() =>
    notifications.value.filter((n) => n.is_read === 0 || n.is_read === false)
  )

  // Fetch notifications from the API with optional parameters
  async function fetchNotifications(params) {
    try {
      const response = await notificationApi.list(params)
      notifications.value = Array.isArray(response)
        ? response
        : (response?.items ?? [])
      return response
    } catch (error) {
      console.error('Failed to fetch notifications:', error)
      throw error
    }
  }

  // Fetch the count of unread notifications from the API
  async function fetchUnreadCount() {
    try {
      const response = await notificationApi.getUnreadCount()
      unreadCount.value =
        typeof response?.count === 'number' ? response.count : Number(response) || 0
      return response
    } catch (error) {
      console.error('Failed to fetch unread count:', error)
      throw error
    }
  }

  // Mark a single notification as read by its ID
  async function markAsRead(id) {
    try {
      const notification = notifications.value.find(n => n.id === id)
      const wasUnread = notification && notification.is_read === 0
      await notificationApi.markAsRead(id)
      if (notification) {
        notification.is_read = 1
      }
      if (wasUnread) {
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
      return true
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
      throw error
    }
  }

  // Mark all notifications as read
  async function markAllAsRead() {
    try {
      await notificationApi.markAllAsRead()
      notifications.value.forEach(notification => {
        notification.is_read = 1
      })
      unreadCount.value = 0
      return true
    } catch (error) {
      console.error('Failed to mark all notifications as read:', error)
      throw error
    }
  }

  // Delete a notification by its ID and update local state
  async function deleteNotification(id) {
    try {
      await notificationApi.delete(id)
      const index = notifications.value.findIndex(n => n.id === id)
      if (index !== -1) {
        const removed = notifications.value[index]
        notifications.value.splice(index, 1)
        if (removed && removed.is_read === 0) {
          unreadCount.value = Math.max(0, unreadCount.value - 1)
        }
      }
      return true
    } catch (error) {
      console.error('Failed to delete notification:', error)
      throw error
    }
  }

  // Add a notification to the beginning of the list and update unread count
  function addNotification(notification) {
    notifications.value.unshift(notification)
    if (notification.is_read === 0 || notification.is_read === false) {
      unreadCount.value += 1
    }
  }

  // Clear all notifications and reset the unread count
  function clearNotifications() {
    notifications.value = []
    unreadCount.value = 0
  }

  return {
    notifications,
    unreadCount,
    unreadNotifications,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    addNotification,
    clearNotifications
  }
})
