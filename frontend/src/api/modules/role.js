import request from '../request'

// API endpoints for role management
export const roleApi = {
  // Get all roles
  list: () => request.get('/roles'),
  // Get a single role by ID
  get: (id) => request.get(`/role/${id}`),
  // Create a new role
  create: (data) => request.post('/role/', data),
  // Update an existing role by ID
  update: (id, data) => request.put(`/role/${id}`, data),
  // Delete a role by ID
  delete: (id) => request.delete(`/role/${id}`),
  // Get permissions assigned to a role
  getRolePermissions: (roleId) => request.get(`/role/${roleId}/permissions`),
  // Assign permissions to a role
  assignPermissions: (roleId, permissionIds) => 
    request.post(`/role/${roleId}/permissions`, { permission_ids: permissionIds }),
  // Get menus assigned to a role
  getRoleMenus: (roleId) => request.get(`/role/${roleId}/menus`),
  // Assign menus to a role
  assignMenus: (roleId, menuIds) => 
    request.post(`/role/${roleId}/menus`, { menu_ids: menuIds })
}
