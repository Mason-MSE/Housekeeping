<script setup lang="ts">
import { ArrowRight } from '@element-plus/icons-vue'
</script>

<template>
  <section class="promo-section">
    <div class="promo-container">
      <div class="promo-badge">
        <span>🎁</span>
        <span>Limited Time Offer</span>
      </div>
      
      <div class="promo-content">
        <h2>New User Exclusive!</h2>
        <p>Sign up today and get <span class="discount">30% OFF</span> your first cleaning service</p>
        
        <div class="promo-code">
          <span class="code-label">Use Code:</span>
          <span class="code-value">CLEAN30</span>
        </div>
        
        <el-button type="primary" class="promo-btn">
          Claim Now <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      
      <div class="promo-decoration">
        <div class="circle circle-1"></div>
        <div class="circle circle-2"></div>
        <div class="circle circle-3"></div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.promo-section {
  padding: 40px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.promo-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 24px;
  position: relative;
  z-index: 1;
  text-align: center;
}

.promo-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  padding: 8px 20px;
  border-radius: 50px;
  color: #fff;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.promo-badge .el-icon {
  font-size: 18px;
  color: #ffd700;
}

.promo-content h2 {
  font-size: 42px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 12px;
  line-height: 1.2;
}

.promo-content p {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 28px;
}

.discount {
  background: #ffd700;
  color: #333;
  padding: 4px 16px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 20px;
}

.promo-code {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.15);
  padding: 12px 24px;
  border-radius: 12px;
  margin-bottom: 28px;
  border: 1px dashed rgba(255, 255, 255, 0.5);
}

.code-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.code-value {
  background: #fff;
  color: #667eea;
  padding: 6px 16px;
  border-radius: 6px;
  font-weight: 700;
  font-size: 18px;
  letter-spacing: 2px;
}

.promo-btn {
  background: #ffd700;
  color: #333;
  border: none;
  padding: 14px 36px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.promo-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.promo-decoration {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  right: -50px;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: -80px;
  left: -50px;
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 50%;
  left: 10%;
}

@media (max-width: 768px) {
  .promo-content h2 {
    font-size: 32px;
  }
  
  .promo-content p {
    font-size: 16px;
  }
  
  .discount {
    font-size: 18px;
  }
}
</style>
