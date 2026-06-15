import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { notificationApi } from '@/api'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref([])
  const unreadCount = ref(0)

  const unreadNotifications = computed(() =>
    notifications.value.filter((n) => n.is_read === 0 || n.is_read === false)
  )

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

  function addNotification(notification) {
    notifications.value.unshift(notification)
    if (notification.is_read === 0 || notification.is_read === false) {
      unreadCount.value += 1
    }
  }

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