<template>
  <section class="section-block">
    <div class="container">
      <div class="section-header">
        <div class="header-text">
          <span class="section-label">Customer Requests</span>
          <h2>Cleaning Requirements</h2>
          <p>Browse latest cleaning requests from customers</p>
        </div>
       
      </div>
      <div class="requirements-grid">
        <div v-for="req in paginatedRequirements" :key="req.id" class="requirement-card">
          <div class="req-header">
            <el-tag type="success">{{ req.property_type }}</el-tag>
            <span class="req-time">{{ req.create_time?.split('T')[0] }}</span>
          </div>
          <div class="req-details">
            <div class="detail-row"><span class="label">Bedroom:</span><span class="value">{{ req.bedroom }}</span></div>
            <div class="detail-row"><span class="label">Bathroom:</span><span class="value">{{ req.bathroom }}</span></div>
            <div class="detail-row"><span class="label">Living Room:</span><span class="value">{{ req.living_room }}</span></div>
            <div class="detail-row"><span class="label">Kitchen:</span><span class="value">{{ req.kitchen }}</span></div>
            <div class="detail-row" v-if="req.lawn"><span class="label">Lawn:</span><span class="value">{{ req.lawn }}</span></div>
            <div class="detail-row" v-if="req.car_space"><span class="label">Car Space:</span><span class="value">{{ req.car_space }}</span></div>
          </div>
          <div class="req-service">{{ req.service_type_name }}</div>
          <div class="req-footer">
            <div class="budget">
              <span class="price">${{ req.budget }}</span>
              <span class="time">{{ req.preferred_time }}</span>
            </div>
            <div class="req-actions">
              <el-button type="primary" size="small" @click="emit('view-applications', req)">View Applications ({{ req.applications_count || 0 }})</el-button>
              <el-button v-if="isLoggedIn && canApply" type="success" size="small" @click="emit('apply', req)">Apply Now</el-button>
            </div>
          </div>
        </div>
      </div>
      <div class="pagination-wrapper" v-if="totalItems > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[8, 12, 16, 24]"
          :total="totalItems"
          layout="total, sizes, prev, pager, next"
          background
        />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ArrowRight } from '@element-plus/icons-vue'

const props = defineProps<{
  requirements: any[]
  isLoggedIn: boolean
  isCleaner: boolean
  canPost: boolean
  canApply: boolean
}>()

const emit = defineEmits<{
  (e: 'post-requirement'): void
  (e: 'view-applications', requirement: any): void
  (e: 'apply', requirement: any): void
}>()

const currentPage = ref(1)
const pageSize = ref(8)

const totalItems = computed(() => props.requirements.length)

const paginatedRequirements = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return props.requirements.slice(start, end)
})
</script>

<style scoped>
.section-block {
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

.post-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #00a885 0%, #00d4aa 100%);
  border: none;
  transition: all 0.3s ease;
}

.post-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 168, 133, 0.35);
}

.header-text p {
  font-size: 16px;
  color: #64748b;
}

.requirements-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.requirement-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #eee;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  min-height: 200px;
}

.requirement-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
}

.req-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.req-time {
  font-size: 12px;
  color: #999;
}

.req-details {
  margin-bottom: 16px;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px 16px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 4px 0;
}

.detail-row .label {
  color: #64748b;
}

.detail-row .value {
  color: #1a1a2e;
  font-weight: 600;
}

.req-service {
  margin-bottom: 12px;
  padding: 6px 12px;
  background: rgba(64, 158, 255, 0.1);
  border-radius: 6px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14px;
  font-weight: 500;
  color: #409eff;
  text-align: center;
}

.req-footer {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 12px;
  border-top: 1px solid #eee;
  margin-top: auto;
}

.req-actions {
  display: flex;
  gap: 8px;
}

.budget .price {
  font-size: 24px;
  font-weight: 700;
  color: #ff6b6b;
}

.budget .time {
  font-size: 14px;
  color: #999;
  margin-left: 6px;
}

@media (max-width: 1024px) {
  .requirements-grid {
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
  
  .requirements-grid {
    grid-template-columns: 1fr;
  }
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}
</style>
