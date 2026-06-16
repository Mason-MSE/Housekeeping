<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  visible: boolean
  isApplying: boolean
  isLoggedIn: boolean
  isCleaner: boolean
  selectedRequirement: any
  applications: any[]
  form: {
    requirement_id: number
    cleaner_id: number
    cleaner_name: string
    offered_price: number | null
    message: string
  }
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit'): void
}>()

// Reactive copy of the form data
const formData = ref({ ...props.form })

// Resets the form data when the dialog becomes visible
watch(() => props.visible, (val) => {
  if (val) {
    formData.value = { ...props.form }
  }
})

// Watches for external form prop changes and syncs the local form data
watch(() => props.form, (val) => {
  formData.value = { ...val }
}, { deep: true })

// Emits the form data when the user submits their application
const handleSubmit = () => {
  emit('submit', formData.value)
}

// Closes the dialog by emitting the update:visible event
const closeDialog = () => {
  emit('update:visible', false)
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="emit('update:visible', $event)"
    title="Cleaner Applications"
    width="700px"
  >
    <div v-if="isApplying && isLoggedIn && isCleaner" class="apply-form">
      <h3>Submit Your Application</h3>
      <el-form :model="formData" label-width="120px">
        <el-form-item label="Requirement ID">
          <el-input v-model="formData.requirement_id" disabled />
        </el-form-item>
        <el-form-item label="Your Name">
          <el-input v-model="formData.cleaner_name" disabled />
        </el-form-item>
        <el-form-item label="Offer Price ($)" required>
          <el-input-number v-model="formData.offered_price" :min="1" :precision="2" />
        </el-form-item>
        <el-form-item label="Message">
          <el-input v-model="formData.message" type="textarea" rows="3" placeholder="Introduce yourself and your experience..." />
        </el-form-item>
      </el-form>
    </div>
    <div v-else>
      <div v-if="applications.length === 0" class="no-applications">
        No applications yet. Be the first to apply!
      </div>
      <div class="applications-list">
        <div v-for="app in applications" :key="app.id" class="application-card">
          <div class="app-cleaner">
            <el-avatar :size="50">{{ app.cleaner_name?.charAt(0) || 'C' }}</el-avatar>
            <div class="app-cleaner-info">
              <div class="name">{{ app.cleaner_name }}</div>
              <div class="stats">
                <el-rate :model-value="app.star_level || 1" disabled :max="5" size="small" />
                <span>{{ app.total_orders || 0 }} orders</span>
                <span>{{ app.total_rating || 5.0 }} rating</span>
              </div>
            </div>
          </div>
          <div class="app-offer">
            <div class="price">${{ app.offered_price }}</div>
            <div class="message">{{ app.message }}</div>
          </div>
        </div>
      </div>
    </div>
    <template #footer>
      <el-button @click="closeDialog">Close</el-button>
      <el-button v-if="isApplying && isLoggedIn && isCleaner" type="primary" :loading="loading" @click="handleSubmit">Submit Application</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.apply-form {
  padding: 10px;
}

.apply-form h3 {
  margin: 0 0 16px 0;
  color: #303133;
}

.no-applications {
  text-align: center;
  padding: 40px;
  color: #909399;
}

.applications-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.application-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

.app-cleaner {
  display: flex;
  align-items: center;
  gap: 12px;
}

.app-cleaner-info .name {
  font-weight: 500;
  margin-bottom: 4px;
}

.app-cleaner-info .stats {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #909399;
}

.app-offer {
  text-align: right;
}

.app-offer .price {
  font-size: 20px;
  font-weight: bold;
  color: #67c23a;
}

.app-offer .message {
  font-size: 12px;
  color: #909399;
}
</style>
