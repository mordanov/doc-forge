import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const raw = localStorage.getItem('auth')
  if (raw) {
    try {
      const parsed = JSON.parse(raw) as { state?: { token?: string }; token?: string }
      const token = parsed.state?.token ?? parsed.token
      if (token) config.headers.Authorization = `Bearer ${token}`
    } catch {
      // ignore malformed storage
    }
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (axios.isAxiosError(err) && err.response?.status === 401) {
      localStorage.removeItem('auth')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
