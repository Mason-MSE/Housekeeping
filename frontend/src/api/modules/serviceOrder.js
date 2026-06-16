import request from '../request'

// API endpoints for service order management
export const serviceOrderApi = {
  // Get all service orders
  list: () => request.get('/service-order/'),
  // Get a single service order by ID
  get: (id) => request.get(`/service-order/${id}`),
  // Create a new service order
  create: (data) => request.post('/service-order/', data),
  // Update an existing service order by ID
  update: (id, data) => request.put(`/service-order/${id}`, data),
  // Delete a service order by ID
  delete: (id) => request.delete(`/service-order/${id}`),
  // Assign a staff member to a service order
  assign: (orderId, staffId) => request.post(`/service-order/assign/${orderId}`, null, { params: { staff_id: staffId } }),
  // Start work on a service order
  start: (orderId) => request.post(`/service-order/start/${orderId}`),
  // Mark a service order as complete
  complete: (orderId) => request.post(`/service-order/complete/${orderId}`),
  // Cancel a service order with a reason
  cancel: (orderId, reason) => request.post(`/service-order/cancel/${orderId}`, { reason }),
  // Rate and comment on a completed service order
  rate: (orderId, rating, comment) => request.post(`/service-order/rate/${orderId}`, { rating, comment }, {
    headers: { 'Content-Type': 'application/json' }
  }),
  // Get a paginated list of service orders
  paginated: (params) => request.post('/service-order/paginated', params)
}
