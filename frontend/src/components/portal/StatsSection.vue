<script setup lang="ts">
defineProps<{
  stats: {
    total_users: number
    total_orders: number
    total_tasks: number
    rating: number
  }
}>()
</script>

<template>
  <section class="stats-section">
    <div class="container">
      <div class="section-header">
        <div class="header-text">
          <span class="section-label">Our Achievements</span>
          <h2>Why Choose Us</h2>
          <p>Trusted by thousands of satisfied customers</p>
        </div>
      </div>
      <div class="stats-grid">
        <div class="stat-item">
          <div class="stat-icon stat-icon-green">
            <span>👥</span>
          </div>
          <div class="stat-content">
            <span class="stat-number">{{ stats.total_users > 10000 ? '10K+' : stats.total_users }}</span>
            <span class="stat-label">Happy Customers</span>
          </div>
        </div>
        
        <div class="stat-item">
          <div class="stat-icon stat-icon-blue">
            <span>🏢</span>
          </div>
          <div class="stat-content">
            <span class="stat-number">500+</span>
            <span class="stat-label">Partner Properties</span>
          </div>
        </div>
        
        <div class="stat-item">
          <div class="stat-icon stat-icon-teal">
            <span>✅</span>
          </div>
          <div class="stat-content">
            <span class="stat-number">{{ stats.total_orders > 50000 ? '50K+' : stats.total_orders }}</span>
            <span class="stat-label">Services Completed</span>
          </div>
        </div>
        
        <div class="stat-item">
          <div class="stat-icon stat-icon-yellow">
            <span>⭐</span>
          </div>
          <div class="stat-content">
            <span class="stat-number">{{ stats.rating }}+</span>
            <span class="stat-label">Customer Rating</span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.stats-section {
  padding: 48px 0;
  background: linear-gradient(135deg, #f0fdf4 0%, #ecfeff 50%, #f0f9ff 100%);
  position: relative;
  overflow: hidden;
}

.stats-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #00a885, #00d4aa, #4ecdc4);
}

.stats-background {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  position: relative;
  z-index: 1;
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 32px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon span {
  font-size: 26px;
}

.stat-icon-green {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
}

.stat-icon-blue {
  background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
}

.stat-icon-teal {
  background: linear-gradient(135deg, #14b8a6 0%, #2dd4bf 100%);
}

.stat-icon-yellow {
  background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a2e;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-top: 4px;
}

@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-item {
    padding: 20px;
  }
  
  .stat-number {
    font-size: 24px;
  }
}
</style>
