import request from '../request'

export const orderPhotoApi = {
  getByOrder: (orderId) => request.get(`/order-photo/order/${orderId}`),
  create: (data) => request.post('/order-photo/', data),
  reorder: (photoIds) => request.post('/order-photo/reorder', { photo_ids: photoIds }),
  delete: (photoId) => request.delete(`/order-photo/${photoId}`)
}