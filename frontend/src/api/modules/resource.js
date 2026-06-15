import request from '../request'

export const resourceApi = {
  list: () => request.get('/resource/'),
  get: (id) => request.get(`/resource/${id}`),
  create: (data) => request.post('/resource/', data),
  update: (id, data) => request.put(`/resource/${id}`, data),
  delete: (id) => request.delete(`/resource/${id}`)
}
