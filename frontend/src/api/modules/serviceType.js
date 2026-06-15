import request from '../request'

export const serviceTypeApi = {
  // Use trailing slash: backend registers /api/service-type/; without it Starlette
  // redirects and axios may drop Authorization on redirect → 401 and forced logout.
  list: () => request.get('/service-type/'),
  get: (typeId) => request.get(`/service-type/${typeId}`),
  create: (data) => request.post('/service-type/', data),
  update: (typeId, data) => request.put(`/service-type/${typeId}`, data),
  delete: (typeId) => request.delete(`/service-type/${typeId}`)
}