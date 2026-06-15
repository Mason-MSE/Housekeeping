import request from '../request'

export const userApi = {
  list: () => request.get('/user/'),
  get: (id) => request.get(`/user/${id}`),
  create: (data) => request.post('/user/', data),
  /** Admin User Management: create with roles (requires auth). */
  createManaged: (data) => request.post('/user/manage', data),
  update: (id, data) => request.put(`/user/${id}`, data),
  delete: (id) => request.delete(`/user/${id}`),
  getByRole: (role) => request.get(`/user/role/${role}`),
  getRoleResources: () => request.get('/user/me/role-resources'),
  changePassword: (data) => request.post('/user/change-password', data),
  updateRoles: (userId, roleIds) => request.post(`/user/${userId}/roles`, { role_ids: roleIds })
}