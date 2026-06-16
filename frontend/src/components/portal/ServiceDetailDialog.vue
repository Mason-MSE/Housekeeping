<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Clock, Check, Warning, Star, Calendar, User } from '@element-plus/icons-vue'

const props = defineProps<{
  visible: boolean
  service: any
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'book'): void
  (e: 'select-cleaner'): void
}>()

// Currently active tab ('overview', 'process', or 'precautions')
const activeTab = ref('overview')
// The cleaner selected for this service booking
const selectedCleaner = ref<any>(null)

// Mapping of service type IDs to their hero images
const serviceImages: Record<number, string> = {
   1: 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=800&q=80',
  2: 'https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?w=800&q=80',
  3: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80',
  4: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&q=80',
}

// Computes the cover image URL from the service's process steps or a default image
const coverImage = computed(() => {
  if (props.service?.process_steps?.length > 0 && props.service.process_steps[0].image_url) {
    return props.service.process_steps[0].image_url
  }
  return serviceImages[props.service?.type_id] || serviceImages[1]
})

// Emits a book event when the user clicks the book now button
const handleBookNow = () => {
  emit('book')
}

// Closes the dialog by emitting the update:visible event
const closeDialog = () => {
  emit('update:visible', false)
}

// Resets the active tab to 'overview' whenever the dialog becomes visible
watch(() => props.visible, (val) => {
  if (val) {
    activeTab.value = 'overview'
  }
})
</script>

<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="emit('update:visible', $event)"
    :title="service?.type_name || 'Service Details'"
    width="800px"
    class="service-detail-dialog"
    :show-close="true"
  >
    <div v-if="service" class="service-detail">
      <div class="service-hero" :style="{ backgroundImage: `url(${coverImage})` }">
        <div class="hero-overlay">
          <div class="hero-content">
            <h2>{{ service.type_name }}</h2>
            <p class="hero-desc">{{ service.description || 'Professional cleaning service tailored to your needs.' }}</p>
            <div class="hero-meta">
              <div class="meta-item">
                <el-icon><Clock /></el-icon>
                <span>{{ service.standard_time || 60 }} mins</span>
              </div>
              <div class="meta-item">
                <el-icon><Star /></el-icon>
                <span>4.9 Rating</span>
              </div>
              <div class="meta-item">
                <el-icon><User /></el-icon>
                <span>1000+ Booked</span>
              </div>
            </div>
          </div>
          <div class="hero-price">
            <template
              v-if="
                Number(service.market_price) > Number(service.price) &&
                Number.isFinite(Number(service.market_price))
              "
            >
              <span class="price-market">${{ Number(service.market_price).toFixed(2) }}</span>
            </template>
            <span class="price">${{ Number(service.price || 0).toFixed(2) }}</span>
            <span class="unit">{{
              Number(service.market_price) > Number(service.price) ? 'promo from' : 'starting from'
            }}</span>
          </div>
        </div>
      </div>

      <div class="service-tabs">
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'overview' }"
          @click="activeTab = 'overview'"
        >
          Overview
        </div>
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'process' }"
          @click="activeTab = 'process'"
        >
          Process
        </div>
        <div 
          class="tab-item" 
          :class="{ active: activeTab === 'precautions' }"
          @click="activeTab = 'precautions'"
        >
          Precautions
        </div>
      </div>

      <div class="tab-content">
        <div v-if="activeTab === 'overview'" class="overview-tab">
          <div class="features-grid">
            <div v-for="(feature, index) in service.features" :key="index" class="feature-card">
              <div class="feature-icon">
                <el-icon><Check /></el-icon>
              </div>
              <span>{{ feature }}</span>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'process'" class="process-tab">
          <div class="process-timeline">
            <div 
              v-for="(step, index) in service.process_steps" 
              :key="index" 
              class="process-step"
            >
              <div class="step-number">{{ step.step_number || index + 1 }}</div>
              <div class="step-content">
                <h4>{{ step.title }}</h4>
                <p>{{ step.description || 'Complete this step' }}</p>
                <span v-if="step.duration_minutes" class="step-duration">
                  {{ step.duration_minutes }} mins
                </span>
              </div>
              <div v-if="index < service.process_steps.length - 1" class="step-connector"></div>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'precautions'" class="precautions-tab">
          <div class="precautions-list">
            <div v-for="(precaution, index) in service.precautions" :key="index" class="precaution-item">
              <div class="precaution-icon">
                <el-icon><Warning /></el-icon>
              </div>
              <span>{{ precaution }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="booking-section">
        <div class="cleaner-select" @click="emit('select-cleaner')">
          <div class="cleaner-info" v-if="selectedCleaner">
            <el-avatar :size="36">{{ selectedCleaner.full_name?.charAt(0) }}</el-avatar>
            <div class="cleaner-detail">
              <span class="name">{{ selectedCleaner.full_name }}</span>
              <el-rate :model-value="selectedCleaner.star_level" disabled size="small" />
            </div>
          </div>
          <div class="cleaner-placeholder" v-else>
            <el-icon><User /></el-icon>
            <span>Select a cleaner (optional)</span>
          </div>
          <el-icon class="arrow"><Calendar /></el-icon>
        </div>
        
        <div class="booking-action">
          <div class="price-display">
            <span class="final-price">${{ Number(service.price || 0).toFixed(2) }}</span>
            <span
              class="original-price"
              v-if="
                service.market_price != null &&
                Number(service.market_price) > Number(service.price || 0)
              "
              >${{ Number(service.market_price).toFixed(2) }}</span
            >
          </div>
          <el-button type="primary" size="large" @click="handleBookNow">
            Book Now
          </el-button>
        </div>
      </div>
    </div>
    <template #footer>
      <div class="dialog-footer">
        <span class="footer-note">
          <el-icon><Check /></el-icon>
          Free cancellation up to 24h before
        </span>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.service-detail {
  margin: -16px;
}

.service-hero {
  height: 220px;
  background-size: cover;
  background-position: center;
  position: relative;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.8) 0%, rgba(0, 0, 0, 0.4) 100%);
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding: 24px;
}

.hero-content h2 {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 8px;
}

.hero-desc {
  color: rgba(255, 255, 255, 0.85);
  font-size: 14px;
  margin-bottom: 12px;
  max-width: 500px;
}

.hero-meta {
  display: flex;
  gap: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #fff;
  font-size: 13px;
}

.meta-item .el-icon {
  color: #00d4aa;
}

.hero-price {
  text-align: right;
}

.hero-price .price-market {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.75);
  text-decoration: line-through;
  margin-bottom: 4px;
}

.hero-price .price {
  display: block;
  font-size: 36px;
  font-weight: 700;
  color: #fff;
}

.hero-price .unit {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.service-tabs {
  display: flex;
  border-bottom: 1px solid #eee;
  padding: 0 24px;
}

.tab-item {
  padding: 16px 24px;
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.tab-item:hover {
  color: #00a885;
}

.tab-item.active {
  color: #00a885;
  border-bottom-color: #00a885;
}

.tab-content {
  padding: 24px;
  min-height: 200px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.feature-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: #f8fafc;
  border-radius: 12px;
  font-size: 14px;
  color: #374151;
}

.feature-icon {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #00a885 0%, #00d4aa 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.process-timeline {
  position: relative;
}

.process-step {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  position: relative;
}

.step-number {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #00a885 0%, #00d4aa 100%);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
  z-index: 1;
}

.step-content {
  flex: 1;
  padding-top: 6px;
}

.step-content h4 {
  font-size: 15px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 4px;
}

.step-content p {
  font-size: 13px;
  color: #64748b;
  line-height: 1.5;
}

.step-duration {
  display: inline-block;
  font-size: 12px;
  color: #00a885;
  background: rgba(0, 168, 133, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  margin-top: 6px;
}

.step-connector {
  position: absolute;
  left: 17px;
  top: 36px;
  width: 2px;
  height: calc(100% + 4px);
  background: linear-gradient(180deg, #00a885 0%, #e0e0e0 100%);
}

.precautions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.precaution-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: #fffbeb;
  border-radius: 12px;
  border: 1px solid #fde68a;
}

.precaution-icon {
  width: 32px;
  height: 32px;
  background: #f59e0b;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.precaution-item span {
  font-size: 14px;
  color: #92400e;
}

.booking-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  background: #f8fafc;
  border-top: 1px solid #eee;
}

.cleaner-select {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 240px;
  padding: 10px 14px;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cleaner-select:hover {
  border-color: #00a885;
}

.cleaner-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.cleaner-detail .name {
  font-size: 13px;
  font-weight: 500;
  color: #1a1a2e;
  display: block;
}

.cleaner-placeholder {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #9ca3af;
  font-size: 13px;
}

.arrow {
  color: #9ca3af;
}

.booking-action {
  display: flex;
  align-items: center;
  gap: 16px;
}

.price-display {
  text-align: right;
}

.final-price {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #ff6b6b;
}

.original-price {
  font-size: 14px;
  color: #9ca3af;
  text-decoration: line-through;
}

.dialog-footer {
  text-align: center;
}

.footer-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
  color: #00a885;
}

:deep(.el-dialog__footer) {
  padding: 0 20px 20px;
}
</style>
