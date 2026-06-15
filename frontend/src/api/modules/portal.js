import request from '../request'

export const portalApi = {
  // 服务类型相关
  getServices: () => request.get('/portal/services'),
  getServiceDetail: (typeId) => request.get(`/portal/services/${typeId}`),
  
  // 房间相关
  getRooms: () => request.get('/portal/rooms'),
  
  // 订单相关
  createOrder: (data) => request.post('/portal/order', data),
  getOrdersByPhone: (phone) => request.get(`/portal/orders/${phone}`),
  
  // 统计数据
  getStats: () => request.get('/portal/stats'),
  getCompanyInfo: () => request.get('/portal/company-info'),
  
  // 评论相关
  getReviews: (limit = 10, offset = 0) => request.get('/portal/reviews', { params: { limit, offset } }),
  getReviewCount: () => request.get('/portal/reviews/count'),
  getReviewDetail: (reviewId) => request.get(`/portal/reviews/${reviewId}`),
  
  // 清洁工相关
  getCleaners: (params) => request.get('/portal/cleaners', { params }),
  getCleanerDetail: (cleanerId) => request.get(`/portal/cleaners/${cleanerId}`),
  
  // 清洁工任务相关
  getCleanerTasks: (cleanerId, status = null) => request.get(`/portal/cleaner/tasks/${cleanerId}`, { params: { status } }),
  getCleanerApplications: (cleanerId) => request.get(`/portal/my-applications/${cleanerId}`),
  getCleanerRequirements: (cleanerId, params = {}) => request.get(`/portal/cleaner/my-requirements/${cleanerId}`, { params }),
  
  // 管理员需求管理
  getAdminRequirements: (params = {}) => request.get('/portal/admin/requirements', { params }),
  getAdminCleaners: () => request.get('/portal/admin/cleaners'),
  assignRequirementToCleaner: (requirementId, cleanerId) => request.post(`/portal/admin/assign-requirement?requirement_id=${requirementId}&cleaner_id=${cleanerId}`),
  deleteRequirement: (requirementId) => request.delete(`/portal/admin/requirement/${requirementId}`),
  hideRequirement: (requirementId) => request.post(`/portal/admin/requirement/${requirementId}/hide`),
  
  // 管理员任务管理
  getAdminTasks: (params = {}) => request.get('/portal/admin/tasks', { params }),
  
  // 客户需求相关
  createRequirement: (data) => request.post('/portal/requirement', data),
  getRequirements: (params) => request.get('/portal/requirements', { params }),
  getRequirementsByPhone: (phone) => request.get(`/portal/requirements/${phone}`),
  
  // 客户管理端
  getCustomerRequirements: (userId, params = {}) => request.get(`/portal/customer/requirements/${userId}`, { params }),
  createCustomerRequirement: (data) => request.post('/portal/customer/requirement', data),
  updateCustomerRequirement: (requirementId, data) =>
    request.put(`/portal/customer/requirement/${requirementId}`, data),
  getCustomerBookings: (userId, page = 1, pageSize = 20) => request.get(`/portal/customer/bookings/${userId}`, { params: { page, page_size: pageSize } }),
  getCustomerBookingDetail: (orderId, userId) => request.get(`/portal/customer/booking/${orderId}`, { params: { user_id: userId } }),
  approveCleaner: (requirementId, cleanerId) => request.post(`/portal/customer/approve-cleaner?requirement_id=${requirementId}&cleaner_id=${cleanerId}`),
  
  // 清洁工订单
  getCleanerBookings: (cleanerId, page = 1, pageSize = 20) => request.get(`/portal/cleaner/bookings/${cleanerId}`, { params: { page, page_size: pageSize } }),
  getCleanerBookingDetail: (orderId, cleanerId) => request.get(`/portal/cleaner/booking/${orderId}`, { params: { cleaner_id: cleanerId } }),
  
  // 清洁工申请相关
  applyForRequirement: (data) => request.post('/portal/apply', data),
  getApplications: (requirementId) => request.get(`/portal/applications/${requirementId}`),
  getCleanerApplications: (cleanerId) => request.get(`/portal/my-applications/${cleanerId}`)
}