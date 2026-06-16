import request from '../request'

// API endpoints for resource management
export const resourceApi = {
  // Get all resources
  list: () => request.get('/resource/'),
  // Get a single resource by ID
  get: (id) => request.get(`/resource/${id}`),
  // Create a new resource
  create: (data) => request.post('/resource/', data),
  // Update an existing resource by ID
  update: (id, data) => request.put(`/resource/${id}`, data),
  // Delete a resource by ID
  delete: (id) => request.delete(`/resource/${id}`)
}
