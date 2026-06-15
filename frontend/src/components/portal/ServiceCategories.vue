<script setup lang="ts">
import { computed } from 'vue'
import { ArrowRight } from '@element-plus/icons-vue'

const props = defineProps<{
  services: any[]
  searchKeyword?: string
}>()

const emit = defineEmits<{
  (e: 'category-click', service: any): void
}>()

const serviceImages: Record<number, string> = {
  1: 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=600&q=80',
  2: 'https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?w=600&q=80',
  3: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=600&q=80',
  4: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=600&q=80',
}

const serviceColors: Record<number, string> = {
  1: '#00a885',
  2: '#e74c3c',
  3: '#3498db',
  4: '#9b59b6',
}

const filteredServices = computed(() => {
  if (!props.searchKeyword) return props.services
  const keyword = props.searchKeyword.toLowerCase()
  return props.services.filter(s =>
    s.type_name.toLowerCase().includes(keyword) ||
    (s.description && s.description.toLowerCase().includes(keyword))
  )
})

const handleCategoryClick = (service: any) => {
  emit('category-click', service)
}

const showPromo = (service: any) => {
  const m = Number(service?.market_price)
  const p = Number(service?.price)
  return Number.isFinite(m) && Number.isFinite(p) && m > p
}

const fmt = (v: unknown) => {
  const n = Number(v)
  return Number.isFinite(n) ? n.toFixed(2) : '0.00'
}
</script>

<template>
  <section class="services-section">
    <div class="container">
      <div class="section-header">
        <div class="header-text">
          <span class="section-label">What We Offer</span>
          <h2>Our Cleaning Services</h2>
          <p>Professional cleaning solutions tailored to your needs</p>
        </div>
        <!-- <el-button type="primary" text class="view-all-btn">
          View All Services <el-icon><ArrowRight /></el-icon>
        </el-button> -->
      </div>

      <div class="services-grid">
        <div
          v-for="(service, index) in filteredServices"
          :key="service.id"
          class="service-card"
          :style="{ '--accent-color': serviceColors[index + 1] || '#00a885' }"
          @click="handleCategoryClick(service)"
        >
          <div class="card-image">
            <img :src="serviceImages[service.id] || serviceImages[1]" :alt="service.type_name" />
            <div class="card-overlay"></div>
            <div class="price-badge" v-if="service.price != null || service.market_price != null">
              <template v-if="showPromo(service)">
                <span class="price-was">${{ fmt(service.market_price) }}</span>
                <span class="price-now">${{ fmt(service.price) }}</span>
                <span class="price-tag">Promo</span>
              </template>
              <template v-else>${{ fmt(service.price) }}</template>
            </div>
          </div>
          <div class="card-content">
            <h3>{{ service.type_name }}</h3>
            <p>{{ service.description }}</p>
            <div class="card-footer">
              <span class="learn-more">Learn More <el-icon><ArrowRight /></el-icon></span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.services-section {
  padding: 48px 0;
  background: linear-gradient(180deg, #f8fafc 0%, #fff 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 32px;
}

.section-label {
  display: inline-block;
  font-size: 13px;
  font-weight: 600;
  color: #00a885;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 12px;
}

.header-text h2 {
  font-size: 36px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.header-text p {
  font-size: 16px;
  color: #64748b;
}

.view-all-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.service-card {
  background: #fff;
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
}

.service-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
}

.card-image {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s ease;
}

.service-card:hover .card-image img {
  transform: scale(1.1);
}

.card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 0%, rgba(0, 0, 0, 0.3) 100%);
}

.price-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  background: var(--accent-color);
  color: #fff;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  line-height: 1.2;
}

.price-badge .price-was {
  font-size: 12px;
  font-weight: 500;
  text-decoration: line-through;
  opacity: 0.85;
}

.price-badge .price-now {
  font-size: 15px;
  font-weight: 700;
}

.price-badge .price-tag {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: rgba(255, 255, 255, 0.25);
  padding: 2px 8px;
  border-radius: 8px;
}

.card-content {
  padding: 24px;
}

.card-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.card-content p {
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  align-items: center;
}

.learn-more {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--accent-color);
  font-size: 14px;
  font-weight: 500;
  transition: gap 0.3s ease;
}

.service-card:hover .learn-more {
  gap: 10px;
}

@media (max-width: 1024px) {
  .services-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }
  
  .header-text h2 {
    font-size: 28px;
  }
  
  .services-grid {
    grid-template-columns: 1fr;
  }
}
</style>
