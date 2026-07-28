import api from '@/lib/api'
import type { AuthToken } from '@/types/api'

export interface LoginRequest {
  username: string
  password: string
}

export async function login(req: LoginRequest): Promise<AuthToken> {
  const { data } = await api.post<AuthToken>('/auth/login', req)
  return data
}
