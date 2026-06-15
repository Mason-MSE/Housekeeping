import request from '../request'

export const transactionApi = {
  pay: (orderId, paymentMethod = 'online') => request.post('/transaction/pay', { order_id: orderId, payment_method: paymentMethod }),
  getByOrder: (orderId) => request.get(`/transaction/order/${orderId}`)
}

export const reviewApi = {
  submit: (orderId, rating, comment) => request.post('/transaction/review', { order_id: orderId, rating, comment })
}
