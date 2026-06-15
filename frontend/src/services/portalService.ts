import request from '@/api/request'

export const portalService = {
  // Service Types
  getServices: () => request.get('/portal/services'),
  getServiceDetail: (typeId: number) => request.get(`/portal/services/${typeId}`),
  
  // Rooms
  getRooms: () => request.get('/portal/rooms'),
  
  // Orders
  createOrder: (data: any) => request.post('/portal/order', data),
  getOrdersByPhone: (phone: string) => request.get(`/portal/orders/${phone}`),
  
  // Stats
  getStats: () => request.get('/portal/stats'),
  getCompanyInfo: () => request.get('/portal/company-info'),
  
  // Reviews
  getReviews: (limit: number = 10, offset: number = 0) => 
    request.get('/portal/reviews', { params: { limit, offset } }),
  getReviewCount: () => request.get('/portal/reviews/count'),
  getReviewDetail: (reviewId: number) => request.get(`/portal/reviews/${reviewId}`),
  
  // Cleaners
  getCleaners: (params?: any) => request.get('/portal/cleaners', { params }),
  getCleanerDetail: (cleanerId: number) => request.get(`/portal/cleaners/${cleanerId}`),
  
  // Cleaner Tasks
  getCleanerTasks: (cleanerId: number, status?: number, page: number = 1, pageSize: number = 20) => 
    request.get(`/portal/cleaner-tasks/${cleanerId}/paginated`, { params: { status, page, page_size: pageSize } }),
  getCleanerApplications: (cleanerId: number, status?: number, page: number = 1, pageSize: number = 20) => 
    request.get(`/portal/my-applications/${cleanerId}/paginated`, { params: { status, page, page_size: pageSize } }),
  
  // Customer Requirements
  createRequirement: (data: any) => request.post('/portal/requirement', data),
  getRequirements: (params?: any) => request.get('/portal/requirements', { params }),
  getRequirementsByPhone: (phone: string) => request.get(`/portal/requirements/${phone}`),
  
  // Customer Management
  getCustomerRequirements: (
    userId: number,
    page: number = 1,
    pageSize: number = 20,
    filters?: { requirement_id?: number | null }
  ) =>
    request.get(`/portal/customer/requirements/${userId}`, {
      params: { page, page_size: pageSize, ...(filters || {}) }
    }),
  getCustomerBookings: (userId: number, page: number = 1, pageSize: number = 20) => 
    request.get(`/portal/customer/bookings/${userId}`, { params: { page, page_size: pageSize } }),
  
  // Applications
  applyForRequirement: (data: any) => request.post('/portal/apply', data),
  getApplications: (requirementId: number) => request.get(`/portal/applications/${requirementId}`),
  
  // Admin APIs
  getAdminRequirements: (status?: number, page: number = 1, pageSize: number = 20, filters?: {
    guest_name?: string,
    guest_phone?: string,
    property_type?: string,
    service_type?: string,
    start_date?: string,
    end_date?: string
  }) => request.get('/portal/admin/requirements', { params: { status, page, page_size: pageSize, ...filters } }),
  getAdminCleaners: () => request.get('/portal/admin/cleaners'),
  assignRequirementToCleaner: (requirementId: number, cleanerId: number) => 
    request.post(`/portal/admin/assign-requirement?requirement_id=${requirementId}&cleaner_id=${cleanerId}`),
  deleteRequirement: (requirementId: number) => request.delete(`/portal/admin/requirement/${requirementId}`),
  hideRequirement: (requirementId: number) => request.post(`/portal/admin/requirement/${requirementId}/hide`),
  
  // Admin Tasks
  getAdminTasks: (page: number = 1, pageSize: number = 20, filters?: {
    order_no?: string,
    cleaner_name?: string,
    start_date?: string,
    end_date?: string,
    status?: number
  }) => request.get('/portal/admin/tasks', { params: { page, page_size: pageSize, ...filters } })
}
