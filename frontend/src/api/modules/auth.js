import request from '../request'

export const authApi = {
  login: (data) => request.post('/auth/login', data, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}