import request from '../request'

export const walletApi = {
  get: () => request.get('/wallet/'),
  recharge: (data) => request.post('/wallet/recharge', data),
  transactions: () => request.get('/wallet/transactions'),
  pay: (orderId) => request.post(`/wallet/pay/${orderId}`),
  settle: (orderId) => request.post(`/wallet/settle/${orderId}`),
  getCleanerEarnings: () => request.get('/wallet/cleaner-earnings')
}