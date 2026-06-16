import request from '../request'

// API endpoints for authentication
export const authApi = {
  // Log in with username and password (form-urlencoded)
  login: (data) => request.post('/auth/login', data, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  })
}
