// Type declarations for the @/services module
declare module '@/services' {
  export const portalService: any
}

// Type declarations for individual service modules under @/services/*
declare module '@/services/*' {
  const service: any
  export default service
}
