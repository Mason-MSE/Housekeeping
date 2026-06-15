<script setup lang="ts">
import { Star, ArrowDown } from '@element-plus/icons-vue'

defineProps<{
  testimonials: any[]
  hasMore: boolean
  loading: boolean
}>()

const emit = defineEmits<{
  (e: 'view-detail', review: any): void
  (e: 'load-more'): void
}>()
</script>

<template>
  <section class="section-block">
    <div class="section-container">
      <div class="section-header">
        <h2>Customer Reviews</h2>
      </div>
      <div class="testimonials-grid">
        <div
          v-for="item in testimonials"
          :key="item.id"
          class="testimonial-card"
          @click="emit('view-detail', item)"
        >
          <div class="testimonial-stars">
            <el-icon v-for="n in item.rating" :key="n" color="#ff9900"><Star /></el-icon>
          </div>
          <p class="testimonial-content">{{ item.content }}</p>
          <div class="testimonial-author">
            <el-avatar :size="36">{{ item.name?.charAt(0) || 'G' }}</el-avatar>
            <span>{{ item.name }}</span>
            <span v-if="item.service" class="review-service">{{ item.service }}</span>
          </div>
        </div>
      </div>
      <div v-if="hasMore" class="view-more-reviews">
        <el-button type="primary" link @click="emit('load-more')" :loading="loading">
          View More Reviews <el-icon><ArrowDown /></el-icon>
        </el-button>
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

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.testimonial-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border: 1px solid #eee;
  cursor: pointer;
}

.testimonial-stars {
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
}

.testimonial-content {
  color: #666;
  line-height: 1.6;
  margin-bottom: 16px;
  font-size: 14px;
}

.testimonial-author {
  display: flex;
  align-items: center;
  gap: 10px;
}

.testimonial-author span {
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

.testimonial-author .review-service {
  color: #999;
  font-size: 12px;
  margin-left: auto;
}

.view-more-reviews {
  text-align: center;
  margin-top: 24px;
}

@media (max-width: 768px) {
  .testimonials-grid {
    grid-template-columns: 1fr;
  }
}
</style>
