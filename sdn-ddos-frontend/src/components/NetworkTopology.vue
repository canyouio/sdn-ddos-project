<template>
  <!-- 关键修改：组件根元素就是卡片，让父级控制其尺寸 -->
  <div class="card topology-panel-card">
    <h3>网络拓扑</h3>
    <div ref="cyContainer" id="cy"></div>
  </div>
</template>

<script setup>
// <script setup> 部分的代码保持不变，无需修改
import { ref, shallowRef, onMounted, onBeforeUnmount, nextTick } from 'vue';
import cytoscape from 'cytoscape';
import api from '@/services/ryu-api';

const cyContainer = ref(null);
const cy = shallowRef(null);
let intervalId = null;

const formatAndValidateElements = (topologyData) => {
  const elements = [];
  const nodeIds = new Set();
  const switches = topologyData.switches || [];
  const hosts = topologyData.hosts || [];
  const links = topologyData.links || [];

  switches.forEach(s => {
    if (s && s.dpid) {
      const id = `s${s.dpid}`;
      elements.push({ group: 'nodes', data: { id, label: `S${parseInt(s.dpid, 16)}`, type: 'switch' } });
      nodeIds.add(id);
    }
  });
  hosts.forEach(h => {
    if (h && h.mac) {
      const id = h.mac;
      elements.push({ group: 'nodes', data: { id, label: (h.ipv4 && h.ipv4[0]) || h.mac, type: 'host' } });
      nodeIds.add(id);
    }
  });

  links.forEach(l => {
    if (l && l.src && l.src.dpid && l.dst && l.dst.dpid) {
      const sourceId = `s${l.src.dpid}`;
      const targetId = `s${l.dst.dpid}`;
      if (nodeIds.has(sourceId) && nodeIds.has(targetId)) {
        elements.push({ group: 'edges', data: { id: `${sourceId}-${targetId}`, source: sourceId, target: targetId } });
      }
    }
  });
  hosts.forEach(h => {
    if (h && h.mac && h.port && h.port.dpid) {
      const sourceId = h.mac;
      const targetId = `s${h.port.dpid}`;
      if (nodeIds.has(sourceId) && nodeIds.has(targetId)) {
        elements.push({ group: 'edges', data: { id: `${sourceId}-${targetId}`, source: sourceId, target: targetId } });
      }
    }
  });
  return elements;
};

const updateTopology = async () => {
  if (!cy.value) return;
  try {
    const [sw, li, ho, al] = await Promise.all([
      api.getSwitches(), api.getLinks(), api.getHosts(), api.getAlerts()
    ]);
    const elements = formatAndValidateElements({ switches: sw.data, links: li.data, hosts: ho.data });
    
    cy.value.elements().remove();
    cy.value.add(elements);

    await nextTick();
    
    cy.value.layout({ name: 'cose', animate: 'end', animationDuration: 500, padding: 30, fit: true }).run();
    
    const blacklist = al.data.blacklist || [];
    cy.value.nodes().removeClass('attacker');
    blacklist.forEach(mac => {
      const node = cy.value.getElementById(mac);
      if (node.length > 0) {
        node.addClass('attacker');
      }
    });

  } catch (e) { console.error("Failed to update topology:", e); }
};

onMounted(() => {
  cy.value = cytoscape({
    container: cyContainer.value,
    style: [
      { selector: 'node', style: { 'label': 'data(label)', 'color': 'white', 'text-outline-color': '#2a2a4a', 'text-outline-width': 2, 'font-size': '12px' } },
      { selector: 'node[type="switch"]', style: { 'background-color': '#6e40c9', 'shape': 'round-rectangle', 'width': 60, 'height': 30 } },
      { selector: 'node[type="host"]', style: { 'background-color': '#2ea043' } },
      { selector: 'node.attacker', style: { 'background-color': 'red', 'border-color': 'white', 'border-width': 3 } },
      { selector: 'edge', style: { 'width': 2, 'line-color': '#4a4a6b', 'curve-style': 'bezier' } },
    ]
  });
  updateTopology();
  intervalId = setInterval(updateTopology, 5000);
});

onBeforeUnmount(() => {
  clearInterval(intervalId);
  if (cy.value) cy.value.destroy();
});
</script>

<style scoped>
/* 关键修改：让卡片和拓扑图容器都能正确地伸缩 */
.topology-panel-card {
  display: flex;
  flex-direction: column;
  flex-grow: 1; /* 允许它在flex容器中增长 */
  min-height: 0; /* 防止无限增高 */
}
#cy {
  flex-grow: 1; /* 让cytoscape容器占满卡片内所有剩余空间 */
  min-height: 400px; /* 给一个最小高度保证可见性 */
}
</style>
