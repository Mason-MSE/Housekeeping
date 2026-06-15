import request from '../request'

export const notificationApi = {
  paginated: (params) => request.get('/notification/paginated', { params }),
  list: (params) => request.get('/notification/', { params }),
  getUnreadCount: () => request.get('/notification/unread-count'),
  markAsRead: (notificationId) => request.post(`/notification/${notificationId}/read`),
  markAllAsRead: () => request.post('/notification/read-all'),
  delete: (notificationId) => request.delete(`/notification/${notificationId}`),
  create: (data) => request.post('/notification/create', data)
}