import request from '../request'

// API endpoints for notification management
export const notificationApi = {
  // Get a paginated list of notifications
  paginated: (params) => request.get('/notification/paginated', { params }),
  // Get all notifications with optional query params
  list: (params) => request.get('/notification/', { params }),
  // Get the count of unread notifications
  getUnreadCount: () => request.get('/notification/unread-count'),
  // Mark a single notification as read by its ID
  markAsRead: (notificationId) => request.post(`/notification/${notificationId}/read`),
  // Mark all notifications as read
  markAllAsRead: () => request.post('/notification/read-all'),
  // Delete a notification by its ID
  delete: (notificationId) => request.delete(`/notification/${notificationId}`),
  // Create a new notification
  create: (data) => request.post('/notification/create', data)
}
