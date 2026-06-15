<script setup lang="ts">
defineProps<{
  ads: any[]
}>()
</script>

<template>
  <section class="section-block">
    <div class="section-container">
      <div class="ads-section">
        <el-row :gutter="16">
          <el-col :span="12" v-for="ad in ads" :key="ad.id">
            <div class="ad-card" :style="{ backgroundColor: ad.color }">
              <div class="ad-content">
                <h3>{{ ad.title }}</h3>
                <p>{{ ad.subtitle }}</p>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </div>
  </section>
</template>

<style scoped>
.section-block {
  padding: 32px 20px;
  background: #fff;
}

.section-container {
  width: 100%;
}

.ads-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px 30px;
}

.ad-card {
  border-radius: 12px;
  padding: 32px;
  color: #fff;
  cursor: pointer;
  transition: transform 0.3s;
}

.ad-card:hover {
  transform: scale(1.02);
}

.ad-content h3 {
  font-size: 24px;
  margin-bottom: 8px;
}

.ad-content p {
  font-size: 16px;
  opacity: 0.9;
}
</style>
