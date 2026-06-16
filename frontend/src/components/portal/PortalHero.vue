<script setup lang="ts">
import { Search, Phone, Clock } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue?: string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'search', value: string): void
}>()

// Two-way bound model for the search keyword input
const searchKeyword = defineModel<string>('searchKeyword', { default: '' })

// Emits the search keyword when the user triggers a search
const handleSearch = () => {
  emit('update:modelValue', searchKeyword.value)
  emit('search', searchKeyword.value)
}
</script>

<template>
  <section class="hero-section">
    <div class="hero-background"></div>
    <div class="hero-content">
      <h1>Professional Cleaning Services</h1>

      <div class="search-box">
        <el-input
          v-model="searchKeyword"
          placeholder="What service do you need?"
          size="large"
          class="search-input"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" size="large" class="search-btn" @click="handleSearch">
          Search
        </el-button>
      </div>

      <div class="trust-badges">
        <div class="badge-item">
          <el-icon><Clock /></el-icon>
          <span>24/7 Available</span>
        </div>
        <div class="badge-item">
          <el-icon><Phone /></el-icon>
          <span>Free Consultation</span>
        </div>
        <div class="badge-item badge-highlight">
          <span>100% Satisfaction</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-section {
  position: relative;
  height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  margin-bottom: 0;
}

.hero-background {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  background-image: url('https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=1920&q=80');
  background-size: cover;
  background-position: center;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(26, 26, 46, 0.5) 0%, rgba(15, 52, 96, 0.4) 100%);
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px 24px;
  text-align: center;
}

.hero-content h1 {
  color: #ffffff;
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 16px;
  text-shadow: 0 2px 10px rgba(0,0,0,0.3);
}

.search-box {
  display: flex;
  gap: 10px;
  max-width: 500px;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.15);
  padding: 6px;
  border-radius: 12px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.search-input {
  flex: 1;
}

.search-input :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.95);
  border: none;
  border-radius: 12px;
  box-shadow: none;
}

.search-input :deep(.el-input__inner) {
  font-size: 15px;
}

.search-btn {
  background: linear-gradient(135deg, #00d4aa 0%, #00a885 100%);
  border: none;
  border-radius: 10px;
  padding: 0 24px;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s ease;
}

.search-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 212, 170, 0.35);
}

.trust-badges {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
  margin-top: 16px;
}

.badge-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 13px;
  font-weight: 500;
}

.badge-item .el-icon {
  font-size: 16px;
  color: #64ffda;
}

.badge-highlight {
  background: rgba(100, 255, 218, 0.15);
  padding: 4px 12px;
  border-radius: 20px;
  color: #64ffda;
  font-weight: 500;
}

@media (max-width: 768px) {
  .hero-section {
    height: 220px;
  }
  
  .hero-content h1 {
    font-size: 20px;
  }

  .trust-badges {
    gap: 12px;
    font-size: 12px;
  }
  
  .search-box {
    flex-direction: column;
    padding: 12px;
  }
  
  .search-btn {
    width: 100%;
  }
}
</style>
