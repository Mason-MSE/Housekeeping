<script setup lang="ts">
import { House, Phone, Message, Location, Clock } from '@element-plus/icons-vue'

defineProps<{
  companyInfo: {
    about_us: string
    phone: string
    email: string
    address: string
  }
}>()

// The current year for the footer copyright notice
const currentYear = new Date().getFullYear()
</script>

<template>
  <footer class="portal-footer">
    <div class="footer-main">
      <div class="container">
        <div class="footer-grid">
          <div class="footer-brand">
            <div class="brand-logo">
              <el-icon class="logo-icon"><House /></el-icon>
              <span class="logo-text">CleanPro</span>
            </div>
            <p class="brand-desc">{{ companyInfo.about_us || 'Your trusted partner for professional cleaning services. We deliver excellence in every clean.' }}</p>
            <div class="social-links">
              <a href="#" class="social-icon">𝕏</a>
              <a href="#" class="social-icon">in</a>
              <a href="#" class="social-icon">f</a>
            </div>
          </div>
          
          <div class="footer-links">
            <h4>Quick Links</h4>
            <ul>
              <li><a href="#">Home</a></li>
              <li><a href="#">Services</a></li>
              <li><a href="#">About Us</a></li>
              <li><a href="#">Contact</a></li>
            </ul>
          </div>
          
          <div class="footer-links">
            <h4>Services</h4>
            <ul>
              <li><a href="#">Regular Cleaning</a></li>
              <li><a href="#">Deep Cleaning</a></li>
              <li><a href="#">Move-in/out</a></li>
              <li><a href="#">Commercial</a></li>
            </ul>
          </div>
          
          <div class="footer-contact">
            <h4>Contact Us</h4>
            <div class="contact-item">
              <el-icon><Phone /></el-icon>
              <span>{{ companyInfo.phone || '400-888-8888' }}</span>
            </div>
            <div class="contact-item">
              <el-icon><Message /></el-icon>
              <span>{{ companyInfo.email || 'service@cleanpro.com' }}</span>
            </div>
            <div class="contact-item">
              <el-icon><Location /></el-icon>
              <span>{{ companyInfo.address || 'Shanghai, China' }}</span>
            </div>
            <div class="contact-item">
              <el-icon><Clock /></el-icon>
              <span>Mon - Sun: 24/7 Available</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="footer-bottom">
      <div class="container">
        <p>&copy; {{ currentYear }} CleanPro. All rights reserved. | Privacy Policy | Terms of Service</p>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.portal-footer {
  background: linear-gradient(180deg, #ffffff 0%, #f0fdf4 100%);
  color: #1a1a2e;
  border-top: 3px solid #00a885;
}

.footer-main {
  padding: 56px 0 24px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.footer-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr 1.2fr;
  gap: 48px;
}

.footer-brand {
  padding-right: 20px;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.logo-icon {
  font-size: 28px;
  color: #00a885;
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  color: #1a1a2e;
}

.brand-desc {
  color: #64748b;
  font-size: 14px;
  line-height: 1.7;
  margin-bottom: 20px;
}

.social-links {
  display: flex;
  gap: 12px;
}

.social-icon {
  width: 36px;
  height: 36px;
  background: #fff;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-size: 14px;
  text-decoration: none;
  transition: all 0.3s ease;
  border: 1px solid #e5e7eb;
}

.social-icon:hover {
  background: #00a885;
  color: #fff;
  transform: translateY(-3px);
}

.footer-links h4,
.footer-contact h4 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #1a1a2e;
}

.footer-links ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 12px;
}

.footer-links a {
  color: #64748b;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s ease;
}

.footer-links a:hover {
  color: #00a885;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
  color: #64748b;
  font-size: 14px;
}

.contact-item .el-icon {
  color: #00a885;
  font-size: 18px;
}

.footer-bottom {
  padding: 20px 0;
  border-top: 1px solid #e5e7eb;
  background: #fff;
}

.footer-bottom p {
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
}

@media (max-width: 1024px) {
  .footer-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 32px;
  }
}

@media (max-width: 640px) {
  .footer-grid {
    grid-template-columns: 1fr;
  }
  
  .footer-brand {
    padding-right: 0;
  }
}
</style>
