import request from '../request'

// API endpoints for permissions and menus
export const permissionApi = {
  // Get all permissions
  list: () => request.get('/permissions'),
  // Get all menus
  getMenus: () => request.get('/menus'),
  // Get the current user's menus
  getMyMenus: () => request.get('/my/menus'),
  // Get the current user's permissions
  getMyPermissions: () => request.get('/my/permissions'),
  // Get permissions assigned to a specific role
  getRolePermissions: (roleId) => request.get(`/role/${roleId}/permissions`),
  // Assign permissions to a role
  assignPermissions: (roleId, permissionIds) => 
    request.post(`/role/${roleId}/permissions`, { permission_ids: permissionIds }),
  // Get menus assigned to a specific role
  getRoleMenus: (roleId) => request.get(`/role/${roleId}/menus`),
  // Assign menus to a role
  assignMenus: (roleId, menuIds) => 
    request.post(`/role/${roleId}/menus`, { menu_ids: menuIds }),
  
  // Permission CRUD
  // Get a single permission by ID
  getById: (id) => request.get(`/permissions/${id}`),
  // Create a new permission
  create: (data) => request.post('/permissions', data),
  // Update an existing permission by ID
  update: (id, data) => request.put(`/permissions/${id}`, data),
  // Delete a permission by ID
  delete: (id) => request.delete(`/permissions/${id}`),
  
  // Menu CRUD
  // Create a new menu
  createMenu: (data) => request.post('/menus', data),
  // Update an existing menu by ID
  updateMenu: (id, data) => request.put(`/menus/${id}`, data),
  // Delete a menu by ID
  deleteMenu: (id) => request.delete(`/menus/${id}`)
}
