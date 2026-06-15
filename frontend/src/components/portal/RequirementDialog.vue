<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  visible: boolean
  form: {
    guest_name: string
    guest_phone: string
    guest_email: string
    property_type: string
    bedroom: number
    bathroom: number
    living_room: number
    kitchen: number
    lawn: number
    car_space: number
    square_footage: number | null
    service_type_name: string
    preferred_time: string
    budget: number | null
    description: string
  }
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'submit'): void
}>()

const formData = ref({ ...props.form })

watch(() => props.visible, (val) => {
  if (val) {
    formData.value = { ...props.form }
  }
})

watch(() => props.form, (val) => {
  formData.value = { ...val }
}, { deep: true })

const handleSubmit = () => {
  emit('submit', formData.value)
}

const closeDialog = () => {
  emit('update:visible', false)
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="emit('update:visible', $event)"
    title="Post Your Cleaning Requirement"
    width="600px"
  >
    <el-form :model="formData" label-width="120px">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Your Name" required>
            <el-input v-model="formData.guest_name" placeholder="Enter your name" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Phone" required>
            <el-input v-model="formData.guest_phone" placeholder="Enter your phone" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Email">
            <el-input v-model="formData.guest_email" placeholder="Enter your email" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Property Type">
            <el-select v-model="formData.property_type" style="width: 100%">
              <el-option label="House" value="House" />
              <el-option label="Apartment" value="Apartment" />
              <el-option label="Villa" value="Villa" />
              <el-option label="Townhouse" value="Townhouse" />
              <el-option label="Studio" value="Studio" />
              <el-option label="Condo" value="Condo" />
              <el-option label="Penthouse" value="Penthouse" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Bedroom">
            <el-input-number v-model="formData.bedroom" :min="0" :max="10" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Bathroom">
            <el-input-number v-model="formData.bathroom" :min="0" :max="10" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Living Room">
            <el-input-number v-model="formData.living_room" :min="0" :max="10" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Kitchen">
            <el-input-number v-model="formData.kitchen" :min="0" :max="5" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Lawn">
            <el-input-number v-model="formData.lawn" :min="0" :max="5" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Car Space">
            <el-input-number v-model="formData.car_space" :min="0" :max="5" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row> 
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Square Footage">
            <el-input-number v-model="formData.square_footage" :min="0" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Budget ($)">
            <el-input-number v-model="formData.budget" :min="0" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="Service Type">
            <el-select v-model="formData.service_type_name" style="width: 100%">
              <el-option label="Regular Cleaning" value="Regular Cleaning" />
              <el-option label="Deep Cleaning" value="Deep Cleaning" />
              <el-option label="Move-in Cleaning" value="Move-in Cleaning" />
              <el-option label="Move-out Cleaning" value="Move-out Cleaning" />
              <el-option label="Office Cleaning" value="Office Cleaning" />
              <el-option label="Post-Construction" value="Post-Construction" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Preferred Time">
            <el-select v-model="formData.preferred_time" style="width: 100%">
              <el-option label="Weekday Morning" value="Weekday Morning" />
              <el-option label="Weekday Afternoon" value="Weekday Afternoon" />
              <el-option label="Weekday Evening" value="Weekday Evening" />
              <el-option label="Weekend Morning" value="Weekend Morning" />
              <el-option label="Weekend Afternoon" value="Weekend Afternoon" />
              <el-option label="Weekend Evening" value="Weekend Evening" />
              <el-option label="Flexible" value="Flexible" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="Description">
        <el-input v-model="formData.description" type="textarea" rows="3" placeholder="Any special requirements..." />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="closeDialog">Cancel</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">Submit</el-button>
    </template>
  </el-dialog>
</template>
