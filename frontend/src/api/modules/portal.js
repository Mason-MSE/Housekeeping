import request from '../request'

// API endpoints for the public portal (service browsing, ordering, reviews, cleaner management)
export const portalApi = {
  // Get all available services
  getServices: () => request.get('/portal/services'),
  // Get details for a specific service type
  getServiceDetail: (typeId) => request.get(`/portal/services/${typeId}`),
  
  // Get all rooms
  getRooms: () => request.get('/portal/rooms'),
  
  // Create a new portal order
  createOrder: (data) => request.post('/portal/order', data),
  // Get orders by customer phone number
  getOrdersByPhone: (phone) => request.get(`/portal/orders/${phone}`),
  
  // Get portal statistics
  getStats: () => request.get('/portal/stats'),
  // Get company information
  getCompanyInfo: () => request.get('/portal/company-info'),
  
  // Get paginated customer reviews
  getReviews: (limit = 10, offset = 0) => request.get('/portal/reviews', { params: { limit, offset } }),
  // Get total review count
  getReviewCount: () => request.get('/portal/reviews/count'),
  // Get a single review by ID
  getReviewDetail: (reviewId) => request.get(`/portal/reviews/${reviewId}`),
  
  // Get a list of cleaners with optional filters
  getCleaners: (params) => request.get('/portal/cleaners', { params }),
  // Get details for a specific cleaner by ID
  getCleanerDetail: (cleanerId) => request.get(`/portal/cleaners/${cleanerId}`),
  
  // Get tasks assigned to a cleaner (optionally filtered by status)
  getCleanerTasks: (cleanerId, status = null) => request.get(`/portal/cleaner/tasks/${cleanerId}`, { params: { status } }),
  // Get applications submitted by a cleaner
  getCleanerApplications: (cleanerId) => request.get(`/portal/my-applications/${cleanerId}`),
  // Get requirements that match a cleaner's skills
  getCleanerRequirements: (cleanerId, params = {}) => request.get(`/portal/cleaner/my-requirements/${cleanerId}`, { params }),
  
  // Admin: get all customer requirements with optional filters
  getAdminRequirements: (params = {}) => request.get('/portal/admin/requirements', { params }),
  // Admin: get all cleaners
  getAdminCleaners: () => request.get('/portal/admin/cleaners'),
  // Admin: assign a requirement to a cleaner
  assignRequirementToCleaner: (requirementId, cleanerId) => request.post(`/portal/admin/assign-requirement?requirement_id=${requirementId}&cleaner_id=${cleanerId}`),
  // Admin: delete a requirement
  deleteRequirement: (requirementId) => request.delete(`/portal/admin/requirement/${requirementId}`),
  // Admin: hide a requirement from public view
  hideRequirement: (requirementId) => request.post(`/portal/admin/requirement/${requirementId}/hide`),
  
  // Admin: get tasks with optional filters
  getAdminTasks: (params = {}) => request.get('/portal/admin/tasks', { params }),
  
  // Customer: create a new cleaning requirement
  createRequirement: (data) => request.post('/portal/requirement', data),
  // Customer: get requirements with optional filters
  getRequirements: (params) => request.get('/portal/requirements', { params }),
  // Customer: get requirements by phone number
  getRequirementsByPhone: (phone) => request.get(`/portal/requirements/${phone}`),
  
  // Customer management: get requirements for a specific user
  getCustomerRequirements: (userId, params = {}) => request.get(`/portal/customer/requirements/${userId}`, { params }),
  // Customer management: create a requirement on behalf of a customer
  createCustomerRequirement: (data) => request.post('/portal/customer/requirement', data),
  // Customer management: update an existing requirement
  updateCustomerRequirement: (requirementId, data) =>
    request.put(`/portal/customer/requirement/${requirementId}`, data),
  // Customer management: get bookings for a user with pagination
  getCustomerBookings: (userId, page = 1, pageSize = 20) => request.get(`/portal/customer/bookings/${userId}`, { params: { page, page_size: pageSize } }),
  // Customer management: get booking detail for a specific order
  getCustomerBookingDetail: (orderId, userId) => request.get(`/portal/customer/booking/${orderId}`, { params: { user_id: userId } }),
  // Customer management: approve a cleaner for a requirement
  approveCleaner: (requirementId, cleanerId) => request.post(`/portal/customer/approve-cleaner?requirement_id=${requirementId}&cleaner_id=${cleanerId}`),
  
  // Cleaner: get bookings for a cleaner with pagination
  getCleanerBookings: (cleanerId, page = 1, pageSize = 20) => request.get(`/portal/cleaner/bookings/${cleanerId}`, { params: { page, page_size: pageSize } }),
  // Cleaner: get booking detail for a specific order
  getCleanerBookingDetail: (orderId, cleanerId) => request.get(`/portal/cleaner/booking/${orderId}`, { params: { cleaner_id: cleanerId } }),
  
  // Cleaner: apply for a requirement
  applyForRequirement: (data) => request.post('/portal/apply', data),
  // Get all applications for a requirement
  getApplications: (requirementId) => request.get(`/portal/applications/${requirementId}`),
  // Get a cleaner's own applications
  getCleanerApplications: (cleanerId) => request.get(`/portal/my-applications/${cleanerId}`)
}
