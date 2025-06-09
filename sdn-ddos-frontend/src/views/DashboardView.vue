<template>
  <div class="dashboard-view">
    <SystemStatus />
    <!-- 关键修改：用 Flexbox 替代 Grid -->
    <div class="panels-flex-container">
      <NetworkTopology class="card topology-panel"/>
      <div class="side-panels">
        <AlertList class="card"/>
        <TrafficChart /> <!-- TrafficChart内部已经有card了，这里不再嵌套 -->
      </div>
    </div>
  </div>
</template>

<script setup>
import SystemStatus from '@/components/SystemStatus.vue';
import NetworkTopology from '@/components/NetworkTopology.vue';
import AlertList from '@/components/AlertList.vue';
import TrafficChart from '@/components/TrafficChart.vue';
</script>

<style scoped>
.dashboard-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%; /* 占满父容器高度 */
}

.panels-flex-container {
  display: flex;
  gap: 20px;
  flex-grow: 1; /* 占满剩余空间 */
  min-height: 0; /* 防止无限增高 */
}

.topology-panel {
  flex: 3; /* 占据 3/4 空间 */
  display: flex; /* 让其内部也能用flex */
  flex-direction: column;
}

.side-panels {
  flex: 1; /* 占据 1/4 空间 */
  display: flex;
  flex-direction: column;
  gap: 20px;
}
</style>
