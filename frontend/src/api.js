import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

export const fetchPrice = async () => (await api.get('/price')).data
export const fetchSignal = async () => (await api.get('/signal')).data
export const fetchHistory = async () => (await api.get('/history')).data
export const openTrade = async (payload) => (await api.post('/trade', payload)).data
export const closeTrade = async (tradeId) => (await api.post('/close', { trade_id: tradeId })).data
export const trainModel = async () => (await api.post('/train')).data
export const getAutoTrade = async () => (await api.get('/autotrade')).data
export const setAutoTrade = async (enabled) => (await api.post('/autotrade', { enabled })).data

export default api
