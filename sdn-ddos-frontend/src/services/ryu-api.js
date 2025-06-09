import axios from 'axios';
const apiClient = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL,
  headers: { 'Content-Type': 'application/json' }
});
export default {
  getAlerts: () => apiClient.get('/alerts'),
  getTrafficStats: () => apiClient.get('/traffic-stats'),
  getSwitches: () => apiClient.get('/topology/switches'),
  getLinks: () => apiClient.get('/topology/links'),
  getHosts: () => apiClient.get('/topology/hosts'),
  getLists: () => apiClient.get('/lists'),
  addToList: (type, mac) => apiClient.post('/lists/add', { type, mac }),
  removeFromList: (type, mac) => apiClient.post('/lists/remove', { type, mac }),
};
