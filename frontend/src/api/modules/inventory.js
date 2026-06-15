import request from '../request'

export const inventoryApi = {
  list: () => request.get('/inventory/'),
  get: (id) => request.get(`/inventory/${id}`),
  create: (data) => request.post('/inventory/', data),
  update: (id, data) => request.put(`/inventory/${id}`, data),
  delete: (id) => request.delete(`/inventory/${id}`),
  restock: (id, quantity) => request.post(`/inventory/restock/${id}`, null, { params: { quantity } }),
  getLowStock: () => request.get('/inventory/low-stock/list'),
  paginated: (params) => request.post('/inventory/paginated', params)
}