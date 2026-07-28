import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { LangSwitch } from '@/components/LangSwitch'
import { useLogin } from './hooks/useLogin'
import { useT } from '@/hooks/useT'

type FormValues = { username: string; password: string }

export default function LoginPage() {
  const t = useT()

  const schema = z.object({
    username: z.string().min(1, t.login.usernameRequired),
    password: z.string().min(1, t.login.passwordRequired),
  })

  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  })
  const login = useLogin()

  return (
    <div className="relative flex min-h-screen items-center justify-center bg-background">
      <div className="absolute top-4 right-4">
        <LangSwitch />
      </div>
      <div className="w-full max-w-sm space-y-6 p-8 border rounded-lg shadow-sm bg-card">
        <div>
          <h1 className="text-2xl font-bold">{t.appName}</h1>
          <p className="text-sm text-muted-foreground mt-1">{t.login.subtitle}</p>
        </div>
        <form onSubmit={handleSubmit((v) => login.mutate(v))} className="space-y-4">
          <div className="space-y-1">
            <Label htmlFor="username">{t.login.username}</Label>
            <Input id="username" autoComplete="username" {...register('username')} />
            {errors.username && <p className="text-xs text-destructive">{errors.username.message}</p>}
          </div>
          <div className="space-y-1">
            <Label htmlFor="password">{t.login.password}</Label>
            <Input id="password" type="password" autoComplete="current-password" {...register('password')} />
            {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
          </div>
          {login.error && (
            <p className="text-xs text-destructive">{t.login.error}</p>
          )}
          <Button type="submit" className="w-full" disabled={login.isPending}>
            {login.isPending ? t.login.submitting : t.login.submit}
          </Button>
        </form>
      </div>
    </div>
  )
}
