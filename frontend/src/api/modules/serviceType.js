import request from '../request'

// API endpoints for service type management
export const serviceTypeApi = {
  // Use trailing slash: backend registers /api/service-type/; without it Starlette
  // redirects and axios may drop Authorization on redirect → 401 and forced logout.
  // Get all service types
  list: () => request.get('/service-type/'),
  // Get a single service type by ID
  get: (typeId) => request.get(`/service-type/${typeId}`),
  // Create a new service type
  create: (data) => request.post('/service-type/', data),
  // Update an existing service type by ID
  update: (typeId, data) => request.put(`/service-type/${typeId}`, data),
  // Delete a service type by ID
  delete: (typeId) => request.delete(`/service-type/${typeId}`)
}
