<script setup lang="ts">
import { ref, watch } from 'vue'

export type PortalBookForm = {
  service_type_id: number
  guest_name: string
  guest_phone: string
  guest_email: string
  service_address: string
  scheduled_time: string
  scheduled_duration_hours: number
  priority: number
  remarks: string
  cleaner_id: number | null
}

const props = defineProps<{
  visible: boolean
  form: PortalBookForm
  selectedService: any
  selectedCleaner: any
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'select-cleaner'): void
  (e: 'submit', value: PortalBookForm): void
}>()

const formData = ref<PortalBookForm>({ ...props.form })

watch(
  () => props.visible,
  (val) => {
    if (val) {
      formData.value = { ...props.form }
    }
  }
)

watch(
  () => props.form,
  (val) => {
    formData.value = { ...val }
  },
  { deep: true }
)

const priorityOptions = [
  { value: 0, label: 'Normal' },
  { value: 1, label: 'Urgent' },
  { value: 2, label: 'Emergency' }
]

const handleSubmit = () => {
  emit('submit', { ...formData.value })
}

const closeDialog = () => {
  emit('update:visible', false)
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="emit('update:visible', $event)"
    title="Book service"
    width="560px"
    destroy-on-close
  >
    <p class="lead">
      Your booking becomes a <strong>service order</strong>: we save the service address, schedule, priority, and
      optional cleaner on the order for staff to fulfil.
    </p>
    <el-form :model="formData" label-position="top" class="book-form">
      <el-form-item label="Service">
        <el-input :value="selectedService?.type_name" disabled />
      </el-form-item>
      <el-form-item label="Price (reference)">
        <el-input :value="'$' + (selectedService?.price ?? '—')" disabled />
      </el-form-item>
      <el-form-item label="Preferred cleaner (optional)">
        <div v-if="selectedCleaner" class="selected-cleaner">
          <el-avatar :size="40">{{ selectedCleaner.full_name?.charAt(0) || 'C' }}</el-avatar>
          <div class="cleaner-detail">
            <span class="name">{{ selectedCleaner.full_name }}</span>
            <el-rate :model-value="selectedCleaner.star_level" disabled :max="5" size="small" />
          </div>
          <el-button link type="primary" @click="emit('select-cleaner')">Change</el-button>
        </div>
        <el-button v-else type="primary" link @click="emit('select-cleaner')">Select a cleaner</el-button>
        <div class="hint">Leave unassigned to let the platform assign later (order stays pending).</div>
      </el-form-item>

      <el-divider content-position="left">Where &amp; when</el-divider>

      <el-form-item label="Service address" required>
        <el-input
          v-model="formData.service_address"
          type="textarea"
          :rows="2"
          maxlength="500"
          show-word-limit
          placeholder="Street, unit, city, access instructions — where cleaning takes place"
        />
      </el-form-item>

      <el-row :gutter="16">
        <el-col :span="14">
          <el-form-item label="Preferred start time" required>
            <el-date-picker
              v-model="formData.scheduled_time"
              type="datetime"
              placeholder="Pick date and time"
              style="width: 100%"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DD HH:mm:ss"
            />
          </el-form-item>
        </el-col>
        <el-col :span="10">
          <el-form-item label="Est. duration (hours)">
            <el-input-number
              v-model="formData.scheduled_duration_hours"
              :min="0.5"
              :max="24"
              :step="0.5"
              :precision="1"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="Priority">
        <el-select v-model="formData.priority" placeholder="Select" style="width: 100%">
          <el-option v-for="p in priorityOptions" :key="p.value" :label="p.label" :value="p.value" />
        </el-select>
      </el-form-item>

      <el-divider content-position="left">Contact</el-divider>

      <el-form-item label="Contact name" required>
        <el-input v-model="formData.guest_name" maxlength="100" placeholder="Full name" />
      </el-form-item>
      <el-form-item label="Phone" required>
        <el-input v-model="formData.guest_phone" maxlength="30" placeholder="Mobile (must match your account)" />
      </el-form-item>
      <el-form-item label="Email (optional)">
        <el-input v-model="formData.guest_email" maxlength="100" placeholder="For confirmations" />
      </el-form-item>
      <el-form-item label="Notes for staff">
        <el-input
          v-model="formData.remarks"
          type="textarea"
          :rows="3"
          maxlength="500"
          show-word-limit
          placeholder="Pets, parking, supplies, special requests"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="closeDialog">Cancel</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">Confirm booking</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.lead {
  margin: 0 0 16px 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}
.hint {
  margin-top: 6px;
  font-size: 12px;
  color: #909399;
}
.selected-cleaner {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cleaner-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.cleaner-detail .name {
  font-weight: 500;
}
.book-form :deep(.el-divider) {
  margin: 8px 0 16px 0;
}
</style>
