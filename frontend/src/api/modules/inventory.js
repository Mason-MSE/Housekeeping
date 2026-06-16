import request from '../request'

// API endpoints for inventory management
export const inventoryApi = {
  // Get the full inventory list
  list: () => request.get('/inventory/'),
  // Get a single inventory item by ID
  get: (id) => request.get(`/inventory/${id}`),
  // Create a new inventory item
  create: (data) => request.post('/inventory/', data),
  // Update an existing inventory item by ID
  update: (id, data) => request.put(`/inventory/${id}`, data),
  // Delete an inventory item by ID
  delete: (id) => request.delete(`/inventory/${id}`),
  // Restock an inventory item by ID with a quantity
  restock: (id, quantity) => request.post(`/inventory/restock/${id}`, null, { params: { quantity } }),
  // Get a list of low-stock inventory items
  getLowStock: () => request.get('/inventory/low-stock/list'),
  // Get a paginated list of inventory items
  paginated: (params) => request.post('/inventory/paginated', params)
}
