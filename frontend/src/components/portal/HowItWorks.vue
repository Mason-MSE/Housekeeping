<script setup lang="ts">
import { Calendar, User, Check, Sunny } from '@element-plus/icons-vue'

// The four-step process for how the service works
const steps = [
  {
    icon: Calendar,
    title: 'Book Your Service',
    description: 'Choose from our range of cleaning services and select a time that works for you.',
    color: '#00a885'
  },
  {
    icon: User,
    title: 'Get Matched with a Pro',
    description: 'We pair you with a verified, experienced cleaner tailored to your specific needs.',
    color: '#4ecdc4'
  },
  {
    icon: Sunny,
    title: 'Enjoy the Clean',
    description: 'Relax while our professional cleaner transforms your space into a pristine haven.',
    color: '#ff6b6b'
  },
  {
    icon: Check,
    title: 'Rate & Review',
    description: 'Share your experience to help us improve and reward our hardworking cleaners.',
    color: '#9b59b6'
  }
]
</script>

<template>
  <section class="how-it-works">
    <div class="container">
      <div class="section-header">
        <span class="section-label">Simple Process</span>
        <h2>How It Works</h2>
        <p>Get your space cleaned in just four easy steps</p>
      </div>

      <div class="steps-container">
        <div class="connector-line"></div>
        <div class="steps-grid">
          <div
            v-for="(step, index) in steps"
            :key="index"
            class="step-card"
          >
            <div class="step-number">{{ index + 1 }}</div>
            <div class="step-icon" :style="{ background: step.color }">
              <el-icon :size="20"><component :is="step.icon" /></el-icon>
            </div>
            <h3>{{ step.title }}</h3>
            <p>{{ step.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.how-it-works {
  padding: 16px 0;
  background: transparent;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  position: relative;
  z-index: 1;
}

.section-header {
  text-align: center;
  margin-bottom: 24px;
}

.section-label {
  display: inline-block;
  font-size: 12px;
  font-weight: 600;
  color: #00a885;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 8px;
}

.section-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 6px;
}

.section-header p {
  font-size: 14px;
  color: #64748b;
}

.steps-container {
  position: relative;
}

.connector-line {
  position: absolute;
  top: 50px;
  left: 12%;
  right: 12%;
  height: 2px;
  background: linear-gradient(90deg, #00a885, #4ecdc4, #ff6b6b, #9b59b6);
  border-radius: 2px;
  z-index: 0;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  position: relative;
  z-index: 1;
}

.step-card {
  text-align: center;
  padding: 12px;
}

.step-number {
  width: 28px;
  height: 28px;
  background: #1a1a2e;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  margin: 0 auto 12px;
  position: relative;
  z-index: 2;
}

.step-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
  color: #fff;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.step-card:hover .step-icon {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.step-card h3 {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 6px;
}

.step-card p {
  font-size: 12px;
  color: #64748b;
  line-height: 1.5;
}

@media (max-width: 1024px) {
  .connector-line {
    display: none;
  }
  
  .steps-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .section-header h2 {
    font-size: 28px;
  }
  
  .steps-grid {
    grid-template-columns: 1fr;
    gap: 32px;
  }
}
</style>
