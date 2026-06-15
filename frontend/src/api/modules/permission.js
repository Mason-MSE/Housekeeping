import request from '../request'

export const permissionApi = {
  list: () => request.get('/permissions'),
  getMenus: () => request.get('/menus'),
  getMyMenus: () => request.get('/my/menus'),
  getMyPermissions: () => request.get('/my/permissions'),
  getRolePermissions: (roleId) => request.get(`/role/${roleId}/permissions`),
  assignPermissions: (roleId, permissionIds) => 
    request.post(`/role/${roleId}/permissions`, { permission_ids: permissionIds }),
  getRoleMenus: (roleId) => request.get(`/role/${roleId}/menus`),
  assignMenus: (roleId, menuIds) => 
    request.post(`/role/${roleId}/menus`, { menu_ids: menuIds }),
  
  // Permission CRUD
  getById: (id) => request.get(`/permissions/${id}`),
  create: (data) => request.post('/permissions', data),
  update: (id, data) => request.put(`/permissions/${id}`, data),
  delete: (id) => request.delete(`/permissions/${id}`),
  
  // Menu CRUD
  createMenu: (data) => request.post('/menus', data),
  updateMenu: (id, data) => request.put(`/menus/${id}`, data),
  deleteMenu: (id) => request.delete(`/menus/${id}`)
}
