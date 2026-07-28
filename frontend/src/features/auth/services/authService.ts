import api from '@/lib/api'
import type { AuthToken } from '@/types/api'

export interface LoginRequest {
  username: string
  password: string
}

export async function login(req: LoginRequest): Promise<AuthToken> {
  const form = new URLSearchParams()
  form.append('username', req.username)
  form.append('password', req.password)
  const { data } = await api.post<AuthToken>('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}
