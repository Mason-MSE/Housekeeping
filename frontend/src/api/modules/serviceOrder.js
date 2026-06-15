import request from '../request'

export const serviceOrderApi = {
  list: () => request.get('/service-order/'),
  get: (id) => request.get(`/service-order/${id}`),
  create: (data) => request.post('/service-order/', data),
  update: (id, data) => request.put(`/service-order/${id}`, data),
  delete: (id) => request.delete(`/service-order/${id}`),
  assign: (orderId, staffId) => request.post(`/service-order/assign/${orderId}`, null, { params: { staff_id: staffId } }),
  start: (orderId) => request.post(`/service-order/start/${orderId}`),
  complete: (orderId) => request.post(`/service-order/complete/${orderId}`),
  cancel: (orderId, reason) => request.post(`/service-order/cancel/${orderId}`, { reason }),
  rate: (orderId, rating, comment) => request.post(`/service-order/rate/${orderId}`, { rating, comment }, {
    headers: { 'Content-Type': 'application/json' }
  }),
  paginated: (params) => request.post('/service-order/paginated', params)
}