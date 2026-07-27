import { useMutation } from '@tanstack/react-query'
import { useNavigate, useLocation } from 'react-router-dom'
import { login, type LoginRequest } from '../services/authService'
import { useAuthStore } from '@/stores/authStore'

export function useLogin() {
  const setToken = useAuthStore((s) => s.setToken)
  const navigate = useNavigate()
  const location = useLocation()
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname ?? '/'

  return useMutation({
    mutationFn: (req: LoginRequest) => login(req),
    onSuccess: (data) => {
      setToken(data.access_token)
      navigate(from, { replace: true })
    },
  })
}
