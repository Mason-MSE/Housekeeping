import request from '../request'

export const complaintApi = {
  create: (data) => request.post('/complaint', data),
  myList: () => request.get('/complaint/my'),
  adminList: (params) => request.get('/complaint/admin', { params }),
  adminGet: (id) => request.get(`/complaint/admin/${id}`),
  adminResolve: (id, data) => request.post(`/complaint/admin/${id}/resolve`, data)
}
