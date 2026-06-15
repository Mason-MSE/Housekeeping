<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { portalApi, userApi } from '@/api'

import PortalHeader from '@/components/portal/PortalHeader.vue'
import PortalHero from '@/components/portal/PortalHero.vue'
import PromoBanner from '@/components/portal/PromoBanner.vue'
import ServiceCategories from '@/components/portal/ServiceCategories.vue'
import CleanerGrid from '@/components/portal/CleanerGrid.vue'
import RequirementsGrid from '@/components/portal/RequirementsGrid.vue'
import StatsSection from '@/components/portal/StatsSection.vue'
import PortalFooter from '@/components/portal/PortalFooter.vue'
import TestimonialsSection from '@/components/portal/TestimonialsSection.vue'
import HowItWorks from '@/components/portal/HowItWorks.vue'

import CleanerSelectionDialog from '@/components/portal/CleanerSelectionDialog.vue'
import ServiceDetailDialog from '@/components/portal/ServiceDetailDialog.vue'
import OrderDialog from '@/components/portal/OrderDialog.vue'
import RequirementDialog from '@/components/portal/RequirementDialog.vue'
import ApplicationsDialog from '@/components/portal/ApplicationsDialog.vue'
import ReviewDetailDialog from '@/components/portal/ReviewDetailDialog.vue'

const router = useRouter()
const userStore = useUserStore()

const isLoggedIn = computed(() => !!userStore.userInfo)
const userInfo = computed(() => userStore.userInfo)
const userRoles = computed(() => userStore.userInfo?.roles || [userStore.userInfo?.role || 'guest'])
const userRole = computed(() => userRoles.value[0])
const isCleaner = computed(() => userRoles.value.some(r => ['staff', 'cleaner', 'employee'].includes(r.toLowerCase())))
const isAdmin = computed(() => userRoles.value.some(r => ['admin', 'administrator'].includes(r.toLowerCase())))

console.log(userRoles);


const userResources = ref<string[]>([])

const searchKeyword = ref('')
const servicesSectionRef = ref<HTMLElement | null>(null)

const handleSearch = (keyword: string) => {
  nextTick(() => {
    const element = document.querySelector('.services-section')
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  })
}

const loading = ref(false)
const services = ref<any[]>([])
const rooms = ref<any[]>([])
const stats = ref({ total_users: 0, total_orders: 0, total_rooms: 0, rating: 4.9 })
const companyInfo = ref<any>({
  about_us: '',
  phone: '',
  email: '',
  address: '',
  facebook: '',
  twitter: '',
  instagram: ''
})

const testimonials = ref<any[]>([])
const hasMoreReviews = ref(false)
const reviewsOffset = ref(0)
const reviewsLimit = 6

const ads = ref([
  { id: 1, title: 'New User Special', subtitle: '30% off first order', color: '#ff6b6b' },
  { id: 2, title: 'Member Benefits', subtitle: 'Recharge $500 get $100', color: '#4ecdc4' },
])

const showCleanerDialog = ref(false)
const showServiceDetailDialog = ref(false)
const showOrderDialog = ref(false)
const showRequirementDialog = ref(false)
const showApplyDialog = ref(false)
const showReviewDetailDialog = ref(false)

const serviceDetail = ref<any>(null)
const selectedService = ref<any>(null)
const selectedCleaner = ref<any>(null)
const selectedRequirement = ref<any>(null)
const selectedReview = ref<any>(null)
const applications = ref<any[]>([])
const cleaners = ref<any[]>([])

const cleanerSearch = ref('')
const cleanerSort = ref('')

const requirementForm = ref({
  guest_name: '',
  guest_phone: '',
  guest_email: '',
  property_type: 'House',
  bedroom: 2,
  bathroom: 1,
  living_room: 1,
  kitchen: 1,
  lawn: 0,
  car_space: 0,
  square_footage: null,
  service_type_name: '',
  preferred_time: '',
  budget: null,
  description: ''
})

const orderForm = ref({
  service_type_id: 0,
  guest_name: '',
  guest_phone: '',
  guest_email: '',
  service_address: '',
  scheduled_time: '',
  scheduled_duration_hours: 2,
  priority: 0,
  remarks: '',
  cleaner_id: null as number | null
})

const applyForm = ref({
  requirement_id: 0,
  cleaner_id: 0,
  cleaner_name: '',
  offered_price: null,
  message: ''
})

const canViewCleaners = computed(() => {
  return userRoles.value.some(r => ['administrator', 'admin', 'manager', 'guest'].includes(r.toLowerCase()))
})

const canPostRequirement = computed(() => {
  return userRoles.value.some(r => ['administrator', 'admin', 'manager', 'guest'].includes(r.toLowerCase()))
})

const canApplyRequirement = computed(() => {
  return userRoles.value.some(r => ['administrator', 'admin', 'cleaner', 'manager', 'guest'].includes(r.toLowerCase()))
})

const canBookService = computed(() => {
  if (userRoles.value.some(r => ['cleaner', 'staff', 'employee'].includes(r.toLowerCase()))) return false
  return userRoles.value.some(r => ['administrator', 'admin', 'manager', 'guest'].includes(r.toLowerCase())) || !isLoggedIn.value
})

const loadRoleResources = async () => {
  if (!isLoggedIn.value) {
    userRole.value = 'guest'
    userRoles.value = ['guest']
    return
  }
  try {
    const res = await userApi.getRoleResources()
    userRoles.value = res.roles?.map((r: string) => r.toLowerCase()) || ['guest']
    userRole.value = userRoles.value[0] || 'guest'
  } catch (e) {
    console.error('Failed to load role resources:', e)
    userRole.value = userInfo.value?.roles?.[0]?.toLowerCase() || userInfo.value?.role?.toLowerCase() || 'guest'
    userRoles.value = [userRole.value]
  }
}

const loadData = async () => {
  try {
    loading.value = true
    
    const servicesRes = await portalApi.getServices()
    const statsRes = await portalApi.getStats()
    const companyInfoRes = await portalApi.getCompanyInfo()
    const cleanersRes = await portalApi.getCleaners()
    const requirementsRes = await portalApi.getRequirements({ limit: 50 })

    services.value = servicesRes || []
    rooms.value = []
    stats.value = statsRes || {}
    companyInfo.value = companyInfoRes || {}
    cleaners.value = cleanersRes || []
    requirements.value = requirementsRes || []

    const reviewsRes = await portalApi.getReviews(reviewsLimit)
    if (reviewsRes && reviewsRes.length > 0) {
      testimonials.value = reviewsRes.map((r: any) => ({
        id: r.id,
        name: r.guest_name,
        content: r.comment,
        rating: r.rating,
        service: r.service_type_name,
        date: r.create_time
      }))
      hasMoreReviews.value = reviewsRes.length >= reviewsLimit
    }
  } catch (e: any) {
    console.error('Failed to load data:', e)
    ElMessage.error('Failed to load data: ' + (e?.message || e?.response?.data?.detail || 'Unknown error'))
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadRoleResources()
  loadData()
})

const requirements = ref<any[]>([])

const handleCategoryClick = async (service: any) => {
  try {
    loading.value = true
    const detail = await portalApi.getServiceDetail(service.id)
    serviceDetail.value = detail
    showServiceDetailDialog.value = true
  } catch (e: any) {
    console.error('Failed to load service detail:', e)
    ElMessage.error('Failed to load service details')
  } finally {
    loading.value = false
  }
}

const openCleanerSelection = async (service?: any) => {
  if (service) {
    selectedService.value = service
  }
  await loadCleaners()
  showCleanerDialog.value = true
}

const loadCleaners = async () => {
  try {
    const params: any = {}
    if (cleanerSearch.value) {
      params.search = cleanerSearch.value
    }
    if (cleanerSort.value) {
      params.sort_by = cleanerSort.value
    }
    const res = await portalApi.getCleaners(params)
    cleaners.value = res
  } catch (e) {
    console.error('Failed to load cleaners:', e)
  }
}

const handleCleanerSearch = (params: { search?: string; sort_by?: string }) => {
  cleanerSearch.value = params.search || ''
  cleanerSort.value = params.sort_by || ''
  loadCleaners()
}

const selectCleaner = (cleaner: any) => {
  selectedCleaner.value = cleaner
  orderForm.value.cleaner_id = cleaner.id
  showCleanerDialog.value = false
  openOrderDialog(selectedService.value)
}

const handleBookNow = (service: any) => {
  showServiceDetailDialog.value = false
  openOrderDialog(service)
}

const openOrderDialog = (service: any) => {
  selectedService.value = service
  const u = userInfo.value as Record<string, unknown> | null | undefined
  // Portal services list uses `id`, but service detail API uses `type_id`.
  // Some callers pass a service detail object, so we coerce to the right field.
  const serviceTypeId = service?.id ?? service?.type_id ?? service?.service_type_id
  if (!serviceTypeId) {
    ElMessage.error('Service type id is missing. Please try again.')
    return
  }
  orderForm.value = {
    service_type_id: serviceTypeId,
    guest_name: (u?.full_name as string) || (u?.username as string) || '',
    guest_phone: (u?.phone as string) || '',
    guest_email: (u?.email as string) || '',
    service_address: (u?.address as string) || '',
    scheduled_time: '',
    scheduled_duration_hours: 2,
    priority: 0,
    remarks: '',
    cleaner_id: selectedCleaner.value?.id || null
  }
  showOrderDialog.value = true
}

const handleOrder = (service: any) => {
  openOrderDialog(service)
}

const submitOrder = async (formFromDialog?: typeof orderForm.value) => {
  const f = formFromDialog || orderForm.value
  if (!f.guest_name?.trim() || !f.guest_phone?.trim()) {
    ElMessage.warning('Please fill in name and phone')
    return
  }
  if (!f.service_address?.trim()) {
    ElMessage.warning('Please enter the service address')
    return
  }
  if (!f.scheduled_time) {
    ElMessage.warning('Please choose a preferred start time')
    return
  }

  const normalizeScheduledTime = (v: unknown) => {
    if (typeof v !== 'string') return v
    const s = v.trim()
    if (!s) return s
    // Vue date-picker uses "YYYY-MM-DD HH:mm:ss" by value-format; convert to ISO.
    if (s.includes(' ') && !s.includes('T')) return s.replace(' ', 'T')
    return s
  }

  try {
    loading.value = true
    const payloadForApi = {
      service_type_id: f.service_type_id,
      guest_name: f.guest_name.trim(),
      guest_phone: f.guest_phone.trim(),
      guest_email: f.guest_email?.trim() || undefined,
      service_address: f.service_address.trim(),
      scheduled_time: normalizeScheduledTime(f.scheduled_time),
      scheduled_duration_hours: f.scheduled_duration_hours ?? 2,
      remarks: f.remarks?.trim() || undefined,
      cleaner_id: f.cleaner_id || null,
      priority: f.priority ?? 0
    }
    // eslint-disable-next-line no-console
    console.log('portal/order payload:', payloadForApi)
    const res: { success?: boolean; order_no?: string; message?: string } = await portalApi.createOrder({
      ...payloadForApi
    })

    if (res.success) {
      ElMessage.success(`Booking successful! Order No: ${res.order_no}`)
      showOrderDialog.value = false
      loadData()
    } else {
      ElMessage.error(res.message || 'Booking failed')
    }
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    // eslint-disable-next-line no-console
    console.error('Booking failed detail:', e?.response?.data)
    if (detail) {
      ElMessage.error(typeof detail === 'string' ? detail : JSON.stringify(detail))
    } else {
      ElMessage.error(e?.response?.data?.message || 'Booking failed, please try again later')
    }
  } finally {
    loading.value = false
  }
}

const submitRequirement = async (form: any) => {
  if (!form.guest_name || !form.guest_phone) {
    ElMessage.warning('Please fill in name and phone')
    return
  }

  try {
    loading.value = true
    const res = await portalApi.createRequirement(form)
    if (res.success) {
      ElMessage.success('Requirement posted successfully!')
      showRequirementDialog.value = false
      loadData()
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Failed to post requirement')
  } finally {
    loading.value = false
  }
}

const viewApplications = async (requirement: any) => {
  selectedRequirement.value = requirement
  applyForm.value = {
    requirement_id: 0,
    cleaner_id: 0,
    cleaner_name: '',
    offered_price: null,
    message: ''
  }
  try {
    const res = await portalApi.getApplications(requirement.id)
    applications.value = res
    showApplyDialog.value = true
  } catch (e) {
    console.error('Failed to load applications:', e)
  }
}

const openApplyForm = (requirement: any) => {
  if (!isLoggedIn.value) {
    ElMessage.warning('Please login first')
    router.push({ path: '/login', query: { redirect: 'portal' } })
    return
  }

  if (!isCleaner.value) {
    ElMessage.warning('Only cleaners can apply for jobs')
    return
  }
  selectedRequirement.value = requirement
  applyForm.value = {
    requirement_id: requirement.id,
    cleaner_id: userInfo.value?.id || 0,
    cleaner_name: userInfo.value?.full_name || userInfo.value?.username || '',
    offered_price: requirement.budget || null,
    message: ''
  }
  showApplyDialog.value = true
}

const submitApplication = async () => {
  if (!applyForm.value.cleaner_name || !applyForm.value.offered_price) {
    ElMessage.warning('Please fill in your name and offer price')
    return
  }

  try {
    loading.value = true
    const res = await portalApi.applyForRequirement(applyForm.value)
    if (res.success) {
      ElMessage.success('Application submitted successfully!')
      showApplyDialog.value = false
      applyForm.value = {
        requirement_id: 0,
        cleaner_id: 0,
        cleaner_name: '',
        offered_price: null,
        message: ''
      }
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || 'Failed to apply')
  } finally {
    loading.value = false
  }
}

const loadMoreReviews = async () => {
  try {
    loading.value = true
    reviewsOffset.value += reviewsLimit
    const moreReviews = await portalApi.getReviews(reviewsLimit, reviewsOffset.value)

    if (moreReviews && moreReviews.length > 0) {
      const newReviews = moreReviews.map((r: any) => ({
        id: r.id,
        name: r.guest_name,
        content: r.comment,
        rating: r.rating,
        service: r.service_type_name,
        date: r.create_time
      }))
      testimonials.value = [...testimonials.value, ...newReviews]
      hasMoreReviews.value = moreReviews.length >= reviewsLimit
    } else {
      hasMoreReviews.value = false
    }
  } catch (e: any) {
    console.error('Failed to load more reviews:', e)
  } finally {
    loading.value = false
  }
}

const viewReviewDetail = (review: any) => {
  selectedReview.value = review
  showReviewDetailDialog.value = true
}

const handlePostRequirement = () => {
  if (!isLoggedIn.value) {
    ElMessage.warning('Please login first')
    router.push({ path: '/login', query: { redirect: 'portal' } })
    return
  }
  showRequirementDialog.value = true
}
</script>

<template>
  <div class="portal-page">
    <PortalHeader />

    <PortalHero v-model="searchKeyword" @search="handleSearch" />

    <div class="section-divider"></div>

    <HowItWorks />

    <div class="main-content">
      <ServiceCategories
        :services="services"
        :search-keyword="searchKeyword"
        @category-click="handleCategoryClick"
      />

      <CleanerGrid
        v-if="canViewCleaners"
        :cleaners="cleaners"
        @view-all="openCleanerSelection()"
        @select-cleaner="selectCleaner"
      />

      <RequirementsGrid
        v-if="canApplyRequirement || canPostRequirement"
        :requirements="requirements"
        :is-logged-in="isLoggedIn"
        :is-cleaner="isCleaner"
        :can-post="canPostRequirement"
        :can-apply="canApplyRequirement"
        @post-requirement="handlePostRequirement"
        @view-applications="viewApplications"
        @apply="openApplyForm"
      />
    </div>

    <StatsSection :stats="stats" />

    <TestimonialsSection
      :testimonials="testimonials"
      :has-more="hasMoreReviews"
      @load-more="loadMoreReviews"
      @view-detail="viewReviewDetail"
    />

    <PortalFooter :company-info="companyInfo" />

    <CleanerSelectionDialog
      v-model:visible="showCleanerDialog"
      :cleaners="cleaners"
      :loading="loading"
      @select="selectCleaner"
      @search="handleCleanerSearch"
    />

    <ServiceDetailDialog
      v-model:visible="showServiceDetailDialog"
      :service="serviceDetail"
      @book="handleBookNow(serviceDetail)"
      @select-cleaner="openCleanerSelection(selectedService)"
    />

    <OrderDialog
      v-model:visible="showOrderDialog"
      :form="orderForm"
      :selected-service="selectedService"
      :selected-cleaner="selectedCleaner"
      :loading="loading"
      @select-cleaner="openCleanerSelection(selectedService)"
      @submit="submitOrder($event)"
    />

    <RequirementDialog
      v-model:visible="showRequirementDialog"
      :form="requirementForm"
      :loading="loading"
      @submit="submitRequirement"
    />

    <ApplicationsDialog
      v-model:visible="showApplyDialog"
      :is-applying="!!applyForm.requirement_id"
      :is-logged-in="isLoggedIn"
      :is-cleaner="isCleaner"
      :selected-requirement="selectedRequirement"
      :applications="applications"
      :form="applyForm"
      :loading="loading"
      @submit="submitApplication"
    />

    <ReviewDetailDialog
      v-model:visible="showReviewDetailDialog"
      :review="selectedReview"
    />
  </div>
</template>

<style scoped>
.portal-page {
  min-height: 100vh;
  background: #fff;
}

.section-divider {
  height: 2px;
  background: linear-gradient(90deg, #00a885, #00d4aa);
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding-top: 16px;
}
</style>
