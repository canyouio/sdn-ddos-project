<template>
  <div>
    <h3>告警与封禁列表</h3>
    <ul v-if="alerts.blacklist && alerts.blacklist.length > 0">
      <li v-for="mac in alerts.blacklist" :key="mac">
        <span>{{ mac }} (PPS: {{ alerts.alerts[mac] ? alerts.alerts[mac].pps : 'N/A' }})</span>
        <button @click="unblock(mac)">解封</button>
      </li>
    </ul>
    <p v-else>暂无告警</p>
  </div>
</template>
<script>
import api from '@/services/ryu-api';
export default {
  data: () => ({ alerts: {}, intervalId: null }),
  methods: {
    async fetchAlerts() {
      try { this.alerts = (await api.getAlerts()).data; }
      catch (e) { console.error("Failed to fetch alerts:", e); }
    },
    async unblock(mac) {
      try { await api.removeFromList('blacklist', mac); this.fetchAlerts(); }
      catch (e) { console.error("Failed to unblock:", e); }
    }
  },
  mounted() { this.fetchAlerts(); this.intervalId = setInterval(this.fetchAlerts, 2000); },
  beforeUnmount() { clearInterval(this.intervalId); }
}
</script>
<style scoped>
ul { list-style: none; padding: 0; max-height: 150px; overflow-y: auto; }
li { display: flex; justify-content: space-between; align-items: center; padding: 5px 0; }
li span { color: var(--danger-color); }
</style>
