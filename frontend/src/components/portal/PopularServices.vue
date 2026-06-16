<script setup lang="ts">
import { computed } from 'vue'
import { Star } from '@element-plus/icons-vue'

const props = defineProps<{
  services: any[]
  searchKeyword?: string
}>()

const emit = defineEmits<{
  (e: 'order', service: any): void
}>()

// Mapping of service type IDs to their image URLs
const serviceImages: Record<number, string> = {
  1: 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=400',
  2: 'https://images.unsplash.com/photo-1527515637462-cff94eecc1ac?w=400',
  3: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400',
  4: 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=400',
  5: 'https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=400',
  6: 'https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=400',
}

// Filters services by the search keyword (by name or description)
const filteredServices = computed(() => {
  if (!props.searchKeyword) return props.services
  const keyword = props.searchKeyword.toLowerCase()
  return props.services.filter(s =>
    s.type_name.toLowerCase().includes(keyword) ||
    (s.description && s.description.toLowerCase().includes(keyword))
  )
})

// Emits the order event with the selected service
const handleOrder = (service: any) => {
  emit('order', service)
}
</script>

<template>
  <section class="section-block alt-bg">
    <div class="section-container">
      <div class="section-header">
        <h2>Popular Services</h2>
        <el-button link type="primary">View More</el-button>
      </div>
      <div class="services-grid">
        <div v-for="service in filteredServices" :key="service.type_id" class="service-card">
          <div class="service-image">
            <img :src="serviceImages[service.type_id] || serviceImages[1]" :alt="service.type_name" />
            <div class="service-badge">Hot</div>
          </div>
          <div class="service-info">
            <h3>{{ service.type_name }}</h3>
            <div class="service-meta">
              <span class="rating"><el-icon><Star /></el-icon>4.9</span>
              <span class="sales">{{ Math.floor(Math.random() * 1000) + 500 }}+ sold</span>
            </div>
            <div class="service-price">
              <span class="price">${{ service.price }}</span>
              <span class="unit">/visit</span>
            </div>
            <el-button type="primary" size="small" class="order-btn" @click="handleOrder(service)">Book Now</el-button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.section-block {
  padding: 32px 20px;
  background: #fff;
}

.section-block.alt-bg {
  background: #fafbfc;
}

.section-container {
  width: 100%;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.service-card {
  background: #fff;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #eee;
}

.service-card:hover {
  border-color: #409eff;
}

.service-image {
  position: relative;
  height: 120px;
}

.service-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.service-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  background: #ff6b6b;
  color: #fff;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
}

.service-info {
  padding: 12px;
}

.service-info h3 {
  font-size: 13px;
  color: #333;
}

.service-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
  color: #999;
}

.rating {
  display: flex;
  align-items: center;
  gap: 2px;
  color: #ff9900;
}

.service-price {
  margin-bottom: 8px;
}

.price {
  font-size: 16px;
  color: #ff6b6b;
  font-weight: 600;
}

.unit {
  font-size: 11px;
  color: #999;
}

.order-btn {
  width: 100%;
}

@media (max-width: 768px) {
  .services-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
