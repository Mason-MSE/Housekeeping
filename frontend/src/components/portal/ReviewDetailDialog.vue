<script setup lang="ts">
defineProps<{
  visible: boolean
  review: any
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
}>()

const closeDialog = () => {
  emit('update:visible', false)
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="emit('update:visible', $event)"
    title="Review Details"
    width="500px"
  >
    <div v-if="review" class="review-detail">
      <div class="review-detail-header">
        <el-avatar :size="60">{{ review.name?.charAt(0) || 'G' }}</el-avatar>
        <div class="review-detail-info">
          <h3>{{ review.name }}</h3>
          <div class="review-detail-stars">
            <el-rate v-model="review.rating" disabled :max="5" />
            <span class="rating-value">{{ review.rating }}.0</span>
          </div>
        </div>
      </div>
      <div class="review-detail-service">
        <el-tag v-if="review.service" type="info">{{ review.service }}</el-tag>
        <el-tag v-if="review.date" type="success">{{ review.date }}</el-tag>
      </div>
      <div class="review-detail-comment">
        <h4>Comment</h4>
        <p>{{ review.content }}</p>
      </div>
    </div>
    <template #footer>
      <el-button @click="closeDialog">Close</el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.review-detail {
  padding: 10px;
}

.review-detail-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.review-detail-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #303133;
}

.review-detail-stars {
  display: flex;
  align-items: center;
  gap: 8px;
}

.review-detail-stars .rating-value {
  color: #ff9900;
  font-weight: bold;
}

.review-detail-service {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.review-detail-comment h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #606266;
}

.review-detail-comment p {
  margin: 0;
  color: #303133;
  line-height: 1.6;
}
</style>
