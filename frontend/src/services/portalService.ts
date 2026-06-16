import request from '@/api/request'

// Service layer for portal-related API calls
export const portalService = {
  // Service Types
  // Get all available services
  getServices: () => request.get('/portal/services'),
  // Get details for a specific service type by ID
  getServiceDetail: (typeId: number) => request.get(`/portal/services/${typeId}`),
  
  // Rooms
  // Get all rooms
  getRooms: () => request.get('/portal/rooms'),
  
  // Orders
  // Create a new portal order
  createOrder: (data: any) => request.post('/portal/order', data),
  // Get orders by customer phone number
  getOrdersByPhone: (phone: string) => request.get(`/portal/orders/${phone}`),
  
  // Stats
  // Get portal statistics
  getStats: () => request.get('/portal/stats'),
  // Get company information
  getCompanyInfo: () => request.get('/portal/company-info'),
  
  // Reviews
  // Get paginated customer reviews
  getReviews: (limit: number = 10, offset: number = 0) => 
    request.get('/portal/reviews', { params: { limit, offset } }),
  // Get total review count
  getReviewCount: () => request.get('/portal/reviews/count'),
  // Get a single review by ID
  getReviewDetail: (reviewId: number) => request.get(`/portal/reviews/${reviewId}`),
  
  // Cleaners
  // Get a list of cleaners with optional filters
  getCleaners: (params?: any) => request.get('/portal/cleaners', { params }),
  // Get details for a specific cleaner by ID
  getCleanerDetail: (cleanerId: number) => request.get(`/portal/cleaners/${cleanerId}`),
  
  // Cleaner Tasks
  // Get paginated tasks assigned to a cleaner (optionally filtered by status)
  getCleanerTasks: (cleanerId: number, status?: number, page: number = 1, pageSize: number = 20) => 
    request.get(`/portal/cleaner-tasks/${cleanerId}/paginated`, { params: { status, page, page_size: pageSize } }),
  // Get paginated applications submitted by a cleaner (optionally filtered by status)
  getCleanerApplications: (cleanerId: number, status?: number, page: number = 1, pageSize: number = 20) => 
    request.get(`/portal/my-applications/${cleanerId}/paginated`, { params: { status, page, page_size: pageSize } }),
  
  // Customer Requirements
  // Create a new cleaning requirement
  createRequirement: (data: any) => request.post('/portal/requirement', data),
  // Get requirements with optional filters
  getRequirements: (params?: any) => request.get('/portal/requirements', { params }),
  // Get requirements by customer phone number
  getRequirementsByPhone: (phone: string) => request.get(`/portal/requirements/${phone}`),
  
  // Customer Management
  // Get paginated requirements for a specific customer
  getCustomerRequirements: (
    userId: number,
    page: number = 1,
    pageSize: number = 20,
    filters?: { requirement_id?: number | null }
  ) =>
    request.get(`/portal/customer/requirements/${userId}`, {
      params: { page, page_size: pageSize, ...(filters || {}) }
    }),
  // Get paginated bookings for a customer
  getCustomerBookings: (userId: number, page: number = 1, pageSize: number = 20) => 
    request.get(`/portal/customer/bookings/${userId}`, { params: { page, page_size: pageSize } }),
  
  // Applications
  // Apply for a requirement as a cleaner
  applyForRequirement: (data: any) => request.post('/portal/apply', data),
  // Get all applications for a specific requirement
  getApplications: (requirementId: number) => request.get(`/portal/applications/${requirementId}`),
  
  // Admin APIs
  // Admin: get paginated requirements with optional filters
  getAdminRequirements: (status?: number, page: number = 1, pageSize: number = 20, filters?: {
    guest_name?: string,
    guest_phone?: string,
    property_type?: string,
    service_type?: string,
    start_date?: string,
    end_date?: string
  }) => request.get('/portal/admin/requirements', { params: { status, page, page_size: pageSize, ...filters } }),
  // Admin: get all cleaners
  getAdminCleaners: () => request.get('/portal/admin/cleaners'),
  // Admin: assign a requirement to a cleaner
  assignRequirementToCleaner: (requirementId: number, cleanerId: number) => 
    request.post(`/portal/admin/assign-requirement?requirement_id=${requirementId}&cleaner_id=${cleanerId}`),
  // Admin: delete a requirement
  deleteRequirement: (requirementId: number) => request.delete(`/portal/admin/requirement/${requirementId}`),
  // Admin: hide a requirement from public view
  hideRequirement: (requirementId: number) => request.post(`/portal/admin/requirement/${requirementId}/hide`),
  
  // Admin Tasks
  // Admin: get paginated tasks with optional filters
  getAdminTasks: (page: number = 1, pageSize: number = 20, filters?: {
    order_no?: string,
    cleaner_name?: string,
    start_date?: string,
    end_date?: string,
    status?: number
  }) => request.get('/portal/admin/tasks', { params: { page, page_size: pageSize, ...filters } })
}
