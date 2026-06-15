import request from '../request'

export const roleApi = {
  list: () => request.get('/roles'),
  get: (id) => request.get(`/role/${id}`),
  create: (data) => request.post('/role/', data),
  update: (id, data) => request.put(`/role/${id}`, data),
  delete: (id) => request.delete(`/role/${id}`),
  getRolePermissions: (roleId) => request.get(`/role/${roleId}/permissions`),
  assignPermissions: (roleId, permissionIds) => 
    request.post(`/role/${roleId}/permissions`, { permission_ids: permissionIds }),
  getRoleMenus: (roleId) => request.get(`/role/${roleId}/menus`),
  assignMenus: (roleId, menuIds) => 
    request.post(`/role/${roleId}/menus`, { menu_ids: menuIds })
}
