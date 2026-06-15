declare module '@/services' {
  export const portalService: any
}

declare module '@/services/*' {
  const service: any
  export default service
}
