import { describe, it, expect, beforeEach } from 'vitest'
import { useThemeStore } from '@/stores/themeStore'

beforeEach(() => {
  localStorage.clear()
  document.documentElement.classList.remove('dark')
  useThemeStore.setState({ theme: 'light' })
})

describe('themeStore', () => {
  it('defaults to light', () => {
    expect(useThemeStore.getState().theme).toBe('light')
  })

  it('setTheme dark adds class', () => {
    useThemeStore.getState().setTheme('dark')
    expect(useThemeStore.getState().theme).toBe('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('setTheme light removes class', () => {
    useThemeStore.getState().setTheme('dark')
    useThemeStore.getState().setTheme('light')
    expect(useThemeStore.getState().theme).toBe('light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })
})
