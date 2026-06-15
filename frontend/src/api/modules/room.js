import request from '../request'

export const roomApi = {
  list: () => request.get('/room/'),
  get: (id) => request.get(`/room/${id}`),
  create: (data) => request.post('/room/', data),
  update: (id, data) => request.put(`/room/${id}`, data),
  delete: (id) => request.delete(`/room/${id}`),
  getAvailable: () => request.get('/room/available/list'),
  updateStatus: (id, status) => request.put(`/room/${id}/status`, null, { params: { status } }),
  paginated: (params) => request.post('/room/paginated', params)
}