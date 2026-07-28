import { describe, it, expect, beforeEach } from 'vitest'
import { useAuthStore } from '@/stores/authStore'

beforeEach(() => {
  localStorage.clear()
  useAuthStore.setState({ token: null, isAuthenticated: false })
})

describe('authStore', () => {
  it('starts unauthenticated', () => {
    expect(useAuthStore.getState().isAuthenticated).toBe(false)
    expect(useAuthStore.getState().token).toBeNull()
  })

  it('setToken marks as authenticated', () => {
    useAuthStore.getState().setToken('tok123')
    expect(useAuthStore.getState().isAuthenticated).toBe(true)
    expect(useAuthStore.getState().token).toBe('tok123')
  })

  it('logout clears token', () => {
    useAuthStore.getState().setToken('tok123')
    useAuthStore.getState().logout()
    expect(useAuthStore.getState().isAuthenticated).toBe(false)
    expect(useAuthStore.getState().token).toBeNull()
  })
})
