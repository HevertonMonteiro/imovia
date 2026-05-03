import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Cliente authenticated (com token)
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Cliente público (sem autenticação) - para Área do Cliente
export const publicApi = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para adicionar token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor para tratar erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API de autenticação
export const authAPI = {
  login: (email, password) => api.post('/auth/login', null, { params: { email, password } }),
  register: (name, email, password, tipo = 'cliente') => api.post('/auth/register', null, { params: { email, password, name, tipo } }),
  getMe: () => api.get('/auth/me')
}

// API de imóveis
export const propertiesAPI = {
  list: (params) => api.get('/properties', { params }),
  get: (id) => api.get(`/properties/${id}`),
  create: (data) => api.post('/properties', data),
  update: (id, data) => api.put(`/properties/${id}`, data),
  delete: (id) => api.delete(`/properties/${id}`),
  addImages: (id, images) => api.post(`/properties/${id}/images`, images)
}

// API de IA
export const aiAPI = {
  analyze: (propertyId) => api.post(`/ai/properties/${propertyId}/analyze`),
  generateAd: (propertyId) => api.post(`/ai/properties/${propertyId}/generate-ad`),
  improveImages: (propertyId) => api.post(`/ai/properties/${propertyId}/improve-images`),
  getSuggestions: (propertyId) => api.get(`/ai/suggestions/${propertyId}`)
}

// API de clientes
export const clientsAPI = {
  list: (params) => api.get('/clients', { params }),
  get: (id) => api.get(`/clients/${id}`),
  create: (data) => api.post('/clients', data),
  update: (id, data) => api.put(`/clients/${id}`, data),
  delete: (id) => api.delete(`/clients/${id}`)
}

// API de leads
export const leadsAPI = {
  list: (params) => api.get('/leads', { params }),
  get: (id) => api.get(`/leads/${id}`),
  create: (data) => api.post('/leads', data),
  delete: (id) => api.delete(`/leads/${id}`),
  listWithIntelligence: (params) => api.get('/leads/inteligente', { params }),
  getIntelligence: (id) => api.get(`/leads/${id}/inteligente`),
  contato: (id) => api.post(`/leads/${id}/contato`),
  transferir: (id, data) => api.post(`/leads/${id}/transferir`, data)
  
  // Para TransferModal
}

// API de dashboard
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getAdvancedStats: () => api.get('/dashboard/stats/advanced'),
  listCorretores: () => api.get('/dashboard/corretores'),
  getCorretorStats: (corretorId) => api.get(`/dashboard/corretores/${corretorId}/stats`)
}

// API de corretores
export const corretoresAPI = {
  list: (params) => api.get('/corretores', { params }),
  get: (id) => api.get(`/corretores/${id}`),
  create: (data) => api.post('/corretores', data),
  delete: (id) => api.delete(`/corretores/${id}`),
  activate: (id) => api.post(`/corretores/${id}/activate`),
  deactivate: (id) => api.post(`/corretores/${id}/deactivate`)
}

// API de imobiliárias
export const imobiliariasAPI = {
  list: () => api.get('/imobiliarias'),
  get: (id) => api.get(`/imobiliarias/${id}`),
  create: (data) => api.post('/imobiliarias', data),
  update: (id, data) => api.put(`/imobiliarias/${id}`, data),
  delete: (id) => api.delete(`/imobiliarias/${id}`),
  activate: (id) => api.post(`/imobiliarias/${id}/activate`),
  deactivate: (id) => api.post(`/imobiliarias/${id}/deactivate`),
  upgrade: (id, plano) => api.post(`/imobiliarias/${id}/upgrade?plano=${plano}`),
  getStats: (id) => api.get(`/imobiliarias/${id}/stats`)
}
