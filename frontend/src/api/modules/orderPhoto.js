import request from '../request'

// API endpoints for order photo management
export const orderPhotoApi = {
  // Get all photos for a given order
  getByOrder: (orderId) => request.get(`/order-photo/order/${orderId}`),
  // Upload a new photo to an order
  create: (data) => request.post('/order-photo/', data),
  // Reorder photos by providing an ordered array of photo IDs
  reorder: (photoIds) => request.post('/order-photo/reorder', { photo_ids: photoIds }),
  // Delete a photo by its ID
  delete: (photoId) => request.delete(`/order-photo/${photoId}`)
}
