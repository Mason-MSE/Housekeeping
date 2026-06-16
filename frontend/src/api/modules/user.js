import request from '../request'

// API endpoints for user management
export const userApi = {
  // Get all users
  list: () => request.get('/user/'),
  // Get a single user by ID
  get: (id) => request.get(`/user/${id}`),
  // Create a new user
  create: (data) => request.post('/user/', data),
  /** Admin User Management: create with roles (requires auth). */
  createManaged: (data) => request.post('/user/manage', data),
  // Update an existing user by ID
  update: (id, data) => request.put(`/user/${id}`, data),
  // Delete a user by ID
  delete: (id) => request.delete(`/user/${id}`),
  // Get users filtered by role
  getByRole: (role) => request.get(`/user/role/${role}`),
  // Get the current user's role-based resources
  getRoleResources: () => request.get('/user/me/role-resources'),
  // Change the current user's password
  changePassword: (data) => request.post('/user/change-password', data),
  // Update the roles assigned to a user
  updateRoles: (userId, roleIds) => request.post(`/user/${userId}/roles`, { role_ids: roleIds })
}
