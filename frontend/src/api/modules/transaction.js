import request from '../request'

// API endpoints for payment transactions
export const transactionApi = {
  // Process payment for an order
  pay: (orderId, paymentMethod = 'online') => request.post('/transaction/pay', { order_id: orderId, payment_method: paymentMethod }),
  // Get the transaction record for a specific order
  getByOrder: (orderId) => request.get(`/transaction/order/${orderId}`)
}

// API endpoints for order reviews
export const reviewApi = {
  // Submit a review (rating and comment) for a completed order
  submit: (orderId, rating, comment) => request.post('/transaction/review', { order_id: orderId, rating, comment })
}
