<script setup lang="ts">
import { computed } from 'vue'

const docsUrl = computed(() => {
  return '/docs'
})
</script>

<template>
  <div class="docs-container">
    <iframe 
      :src="docsUrl" 
      frameborder="0" 
      class="docs-iframe"
      title="API Documentation"
    />
  </div>
</template>

<style scoped>
.docs-container {
  height: calc(100vh - 120px);
  width: 100%;
  background: #fff;
}

.docs-iframe {
  width: 100%;
  height: 100%;
  min-height: calc(100vh - 120px);
  border: none;
}
</style>
