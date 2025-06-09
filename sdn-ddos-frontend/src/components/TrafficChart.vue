<template>
  <div class="card">
    <h3>实时流量 (PPS)</h3>
    <div class="chart-container">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
// <script setup> 部分的代码保持不变，无需修改
import { ref, shallowRef, onMounted, onBeforeUnmount } from 'vue';
import Chart from 'chart.js/auto';
import api from '@/services/ryu-api';

const chartCanvas = ref(null);
const chartInstance = shallowRef(null);
let intervalId = null;

const updateChart = async () => {
  if (!chartInstance.value) return;
  try {
    const { data } = await api.getTrafficStats();
    if (!Array.isArray(data)) {
        chartInstance.value.data.labels = [];
        chartInstance.value.data.datasets[0].data = [];
        chartInstance.value.update('none');
        return;
    }
    const labels = data.map(d => d.time);
    const ppsData = data.map(d => d.pps);
    chartInstance.value.data.labels = labels;
    chartInstance.value.data.datasets[0].data = ppsData;
    chartInstance.value.update('none');
  } catch (e) { console.error("Failed to fetch traffic data:", e); }
};

onMounted(() => {
  if (!chartCanvas.value) return;
  const ctx = chartCanvas.value.getContext('2d');
  chartInstance.value = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{ label: 'PPS', data: [], borderColor: '#00e676', tension: 0.4, fill: true, backgroundColor: 'rgba(0, 230, 118, 0.2)' }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { ticks: { color: 'white' } },
        y: { beginAtZero: true, ticks: { color: 'white' } }
      },
      plugins: {
        legend: { labels: { color: 'white' } }
      }
    }
  });
  updateChart();
  intervalId = setInterval(updateChart, 5000);
});

onBeforeUnmount(() => {
  clearInterval(intervalId);
  if (chartInstance.value) {
    chartInstance.value.destroy();
  }
});
</script>

<style scoped>
/* 关键修改：给图表一个明确的父容器尺寸 */
.chart-container {
  position: relative;
  height: 250px; /* 固定高度 */
  width: 100%;
}
</style>
