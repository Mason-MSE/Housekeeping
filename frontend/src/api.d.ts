// Type declarations for the @/api module
declare module '@/api' {
  export const portalApi: any
  export const serviceOrderApi: any
  export const orderPhotoApi: any
  export const roomApi: any
  export const userApi: any
  export const serviceTypeApi: any
  export const walletApi: any
}

// Type declarations for individual API modules under @/api/*
declare module '@/api/*' {
  const api: any
  export default api
}
