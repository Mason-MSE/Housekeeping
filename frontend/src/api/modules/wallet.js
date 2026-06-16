import request from '../request'

// API endpoints for wallet management
export const walletApi = {
  // Get the current user's wallet details
  get: () => request.get('/wallet/'),
  // Recharge the wallet with a given amount
  recharge: (data) => request.post('/wallet/recharge', data),
  // Get the transaction history for the wallet
  transactions: () => request.get('/wallet/transactions'),
  // Pay for an order using the wallet balance
  pay: (orderId) => request.post(`/wallet/pay/${orderId}`),
  // Settle earnings for a completed order
  settle: (orderId) => request.post(`/wallet/settle/${orderId}`),
  // Get earnings for the current cleaner user
  getCleanerEarnings: () => request.get('/wallet/cleaner-earnings')
}
