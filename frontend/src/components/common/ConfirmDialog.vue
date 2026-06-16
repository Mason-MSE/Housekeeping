<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="30%"
    :before-close="handleClose"
  >
    <div class="confirm-content">
      <slot>
        <p>{{ message }}</p>
      </slot>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="cancel">{{ cancelText }}</el-button>
        <el-button 
          type="primary" 
          @click="confirm"
          :loading="confirmLoading"
        >
          {{ confirmText }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: 'Confirmation'
  },
  message: {
    type: String,
    default: 'Are you sure you want to proceed?'
  },
  confirmText: {
    type: String,
    default: 'Confirm'
  },
  cancelText: {
    type: String,
    default: 'Cancel'
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

// Controls the dialog visibility
const visible = ref(false)
// Loading state for the confirm button
const confirmLoading = ref(false)

// Syncs the dialog visibility with the modelValue prop
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
})

// Syncs the confirm loading state with the loading prop
watch(() => props.loading, (newVal) => {
  confirmLoading.value = newVal
})

// Closes the dialog and emits both cancel and modelValue events
function handleClose() {
  visible.value = false
  emit('update:modelValue', false)
  emit('cancel')
}

// Emits the confirm event and sets the loading state
function confirm() {
  confirmLoading.value = true
  emit('confirm')
}

// Cancels the dialog and triggers handleClose
function cancel() {
  handleClose()
}
</script>

<style scoped>
.confirm-content {
  padding: 20px 0;
  text-align: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>