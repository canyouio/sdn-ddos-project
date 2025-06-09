<template>
  <div class="list-management-view">
    <div class="list-panel card">
      <h3>白名单管理 (Whitelist)</h3>
      <div class="input-group">
        <input v-model="whitelistInput" placeholder="输入MAC地址, e.g., 00:00:00:00:00:01">
        <button @click="addToList('whitelist')">添加</button>
      </div>
      <ul>
        <li v-for="mac in lists.whitelist" :key="mac">
          <span>{{ mac }}</span>
          <button @click="removeFromList('whitelist', mac)">删除</button>
        </li>
      </ul>
    </div>
    <div class="list-panel card">
      <h3>黑名单管理 (Blacklist)</h3>
      <div class="input-group">
        <input v-model="blacklistInput" placeholder="输入MAC地址, e.g., 00:00:00:00:00:02">
        <button @click="addToList('blacklist')">添加</button>
      </div>
      <ul>
        <li v-for="mac in lists.blacklist" :key="mac">
          <span>{{ mac }}</span>
          <button @click="removeFromList('blacklist', mac)">删除</button>
        </li>
      </ul>
    </div>
  </div>
</template>
<script>
import api from '@/services/ryu-api';
export default {
  data: () => ({
    lists: { whitelist: [], blacklist: [] },
    whitelistInput: '',
    blacklistInput: '',
  }),
  methods: {
    async fetchLists() {
      try { this.lists = (await api.getLists()).data; }
      catch (e) { console.error("Failed to fetch lists:", e); }
    },
    async addToList(type) {
      const mac = type === 'whitelist' ? this.whitelistInput : this.blacklistInput;
      if (!mac) return;
      try {
        await api.addToList(type, mac);
        if (type === 'whitelist') this.whitelistInput = ''; else this.blacklistInput = '';
        this.fetchLists();
      } catch (e) { console.error(`Failed to add to ${type}:`, e); }
    },
    async removeFromList(type, mac) {
      try { await api.removeFromList(type, mac); this.fetchLists(); }
      catch (e) { console.error(`Failed to remove from ${type}:`, e); }
    }
  },
  mounted() { this.fetchLists(); }
}
</script>
<style scoped>
.list-management-view { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.input-group { display: flex; gap: 10px; margin-bottom: 15px; }
ul { list-style: none; padding: 0; }
li { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--border-color); }
</style>
