import request from '../request'

// API endpoints for complaint management
export const complaintApi = {
  // Submit a new complaint
  create: (data) => request.post('/complaint', data),
  // Get the current user's complaints
  myList: () => request.get('/complaint/my'),
  // Admin: list all complaints with optional query params
  adminList: (params) => request.get('/complaint/admin', { params }),
  // Admin: get a single complaint by ID
  adminGet: (id) => request.get(`/complaint/admin/${id}`),
  // Admin: resolve a complaint by ID with resolution data
  adminResolve: (id, data) => request.post(`/complaint/admin/${id}/resolve`, data)
}
