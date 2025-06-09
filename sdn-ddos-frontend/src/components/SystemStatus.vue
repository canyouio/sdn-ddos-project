<template>
  <div class="system-status-bar">
    <div class="status-item card">总交换机: <strong>{{ stats.switches }}</strong></div>
    <div class="status-item card">总主机: <strong>{{ stats.hosts }}</strong></div>
    <div class="status-item card">总链路: <strong>{{ stats.links }}</strong></div>
  </div>
</template>
<script>
import api from '@/services/ryu-api';
export default {
  data: () => ({ stats: { switches: 0, hosts: 0, links: 0 }, intervalId: null }),
  methods: {
    async fetchStats() {
      try {
        const [sw, ho, li] = await Promise.all([api.getSwitches(), api.getHosts(), api.getLinks()]);
        this.stats = { switches: sw.data.length, hosts: ho.data.length, links: li.data.length };
      } catch (e) { console.error("Failed to fetch system status:", e); }
    }
  },
  mounted() { this.fetchStats(); this.intervalId = setInterval(this.fetchStats, 10000); },
  beforeUnmount() { clearInterval(this.intervalId); }
}
</script>
<style scoped>
.system-status-bar { display: flex; gap: 20px; }
.status-item { flex-grow: 1; text-align: center; }
strong { color: var(--secondary-color); font-size: 1.5em; margin-left: 10px; }
</style>
