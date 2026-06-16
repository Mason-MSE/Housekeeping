<script setup lang="ts">
import { computed } from 'vue'
import { Star, ArrowRight } from '@element-plus/icons-vue'

const props = defineProps<{
  cleaners: any[]
}>()

const emit = defineEmits<{
  (e: 'view-all'): void
  (e: 'select-cleaner', cleaner: any): void
}>()

// Limits the displayed cleaners to the first 4
const displayedCleaners = computed(() => {
  return props.cleaners.slice(0, 4)
})

// Extracts initials from a full name
const getInitials = (name: string) => {
  return name?.split(' ').map(n => n[0]).join('').toUpperCase() || 'C'
}
</script>

<template>
  <section class="cleaners-section">
    <div class="container">
      <div class="section-header">
        <div class="header-text">
          <span class="section-label">Expert Team</span>
          <h2>Our Professional Cleaners</h2>
          <p>Meet our dedicated team of cleaning experts</p>
        </div>
        <el-button type="primary" class="view-all-btn" @click="emit('view-all')">
          View All <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>

      <div class="cleaners-grid">
        <div
          v-for="cleaner in displayedCleaners"
          :key="cleaner.id"
          class="cleaner-card"
          @click="emit('select-cleaner', cleaner)"
        >
          <div class="card-header">
            <div class="avatar-wrapper">
              <div class="avatar">
                {{ getInitials(cleaner.full_name) }}
              </div>
              <div class="online-dot"></div>
            </div>
            <div class="rating-badge">
              <el-icon><Star /></el-icon>
              <span>{{ cleaner.total_rating }}</span>
            </div>
          </div>
          
          <div class="card-body">
            <h3>{{ cleaner.full_name }}</h3>
            <p class="specialty">Professional Cleaner</p>
            
            <div class="stats-row">
              <div class="stat-item">
                <span>{{ cleaner.total_orders || 0 }}+ Jobs</span>
              </div>
              <div class="stat-item">
                <el-icon><Star /></el-icon>
                <span>{{ cleaner.total_rating }}</span>
              </div>
            </div>
          </div>
          
          <div class="card-footer">
            <el-button type="primary" class="book-btn">Book Now</el-button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.cleaners-section {
  padding: 48px 0;
  background: #fff;
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
}

.cleaners-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.cleaner-card {
  background: #fff;
  border-radius: 20px;
  padding: 28px;
  text-align: center;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid #e2e8f0;
  position: relative;
  overflow: hidden;
}

.cleaner-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #00a885, #00d4aa);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s ease;
}

.cleaner-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 168, 133, 0.15);
  border-color: transparent;
}

.cleaner-card:hover::before {
  transform: scaleX(1);
}

.card-header {
  position: relative;
  margin-bottom: 20px;
}

.avatar-wrapper {
  position: relative;
  display: inline-block;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #00a885 0%, #00d4aa 100%);
  color: #fff;
  font-size: 24px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
}

.online-dot {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 16px;
  height: 16px;
  background: #22c55e;
  border: 3px solid #fff;
  border-radius: 50%;
}

.rating-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: #fffbeb;
  color: #f59e0b;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card-body h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 4px;
}

.specialty {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 16px;
}

.stats-row {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #64748b;
}

.stat-item .el-icon {
  color: #00a885;
}

.card-footer {
  margin-top: 20px;
}

.book-btn {
  width: 100%;
  background: linear-gradient(135deg, #00a885 0%, #00d4aa 100%);
  border: none;
  font-weight: 500;
}

.book-btn:hover {
  opacity: 0.9;
}

@media (max-width: 1024px) {
  .cleaners-grid {
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
  
  .cleaners-grid {
    grid-template-columns: 1fr;
  }
}
</style>
