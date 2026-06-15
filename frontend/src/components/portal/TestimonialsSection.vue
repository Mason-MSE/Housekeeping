<script setup lang="ts">
import { Star } from '@element-plus/icons-vue'

defineProps<{
  testimonials: any[]
  hasMore?: boolean
}>()

const emit = defineEmits<{
  (e: 'load-more'): void
  (e: 'view-detail', review: any): void
}>()
</script>

<template>
  <section class="testimonials-section">
    <div class="container">
      <div class="section-header">
        <div class="header-text">
          <span class="section-label">Testimonials</span>
          <h2>What Our Customers Say</h2>
          <p>Real feedback from our valued customers</p>
        </div>
      </div>

      <div class="testimonials-grid" v-if="testimonials.length > 0">
        <div
          v-for="(testimonial, index) in testimonials"
          :key="testimonial.id || index"
          class="testimonial-card"
          @click="emit('view-detail', testimonial)"
        >
          <div class="card-header">
            <div class="avatar">
              {{ testimonial.name?.charAt(0) || 'C' }}
            </div>
            <div class="customer-info">
              <h4>{{ testimonial.name }}</h4>
              <div class="rating">
                <el-icon v-for="i in 5" :key="i" class="star" :class="{ filled: i <= (testimonial.rating || 5) }">
                  <Star />
                </el-icon>
              </div>
            </div>
          </div>
          <p class="review-text">"{{ testimonial.content }}"</p>
          <div class="card-footer">
            <span class="service-type" v-if="testimonial.service">{{ testimonial.service }}</span>
            <span class="date" v-if="testimonial.date">{{ new Date(testimonial.date).toLocaleDateString() }}</span>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <p>No reviews yet. Be the first to share your experience!</p>
      </div>

      <div class="load-more" v-if="hasMore">
        <el-button type="primary" plain @click="emit('load-more')">
          Load More Reviews
        </el-button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.testimonials-section {
  padding: 48px 0;
  background: #f8fafc;
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

.header-text {
  text-align: left;
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

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.testimonial-card {
  background: #fff;
  border-radius: 20px;
  padding: 28px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  border: 1px solid #f0f0f0;
}

.testimonial-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
}

.avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00a885 0%, #00d4aa 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
}

.customer-info h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 4px;
}

.rating {
  display: flex;
  gap: 2px;
}

.star {
  color: #ddd;
  font-size: 14px;
}

.star.filled {
  color: #ffc107;
}

.review-text {
  font-size: 15px;
  color: #475569;
  line-height: 1.7;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.service-type {
  font-size: 13px;
  color: #00a885;
  font-weight: 500;
  background: rgba(0, 168, 133, 0.1);
  padding: 4px 12px;
  border-radius: 12px;
}

.date {
  font-size: 13px;
  color: #94a3b8;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  background: #f8fafc;
  border-radius: 20px;
}

.empty-state p {
  font-size: 16px;
  color: #64748b;
}

.load-more {
  text-align: center;
  margin-top: 40px;
}

@media (max-width: 1024px) {
  .testimonials-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .header-text h2 {
    font-size: 28px;
  }
  
  .testimonials-grid {
    grid-template-columns: 1fr;
  }
}
</style>
