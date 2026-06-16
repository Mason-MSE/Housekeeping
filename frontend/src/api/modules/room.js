import request from '../request'

// API endpoints for room management
export const roomApi = {
  // Get all rooms
  list: () => request.get('/room/'),
  // Get a single room by ID
  get: (id) => request.get(`/room/${id}`),
  // Create a new room
  create: (data) => request.post('/room/', data),
  // Update an existing room by ID
  update: (id, data) => request.put(`/room/${id}`, data),
  // Delete a room by ID
  delete: (id) => request.delete(`/room/${id}`),
  // Get a list of available rooms
  getAvailable: () => request.get('/room/available/list'),
  // Update the status of a room
  updateStatus: (id, status) => request.put(`/room/${id}/status`, null, { params: { status } }),
  // Get a paginated list of rooms
  paginated: (params) => request.post('/room/paginated', params)
}
