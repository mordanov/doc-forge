import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useLogin } from './hooks/useLogin'

const schema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
})

type FormValues = z.infer<typeof schema>

export default function LoginPage() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  })
  const login = useLogin()

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="w-full max-w-sm space-y-6 p-8 border rounded-lg shadow-sm bg-card">
        <div>
          <h1 className="text-2xl font-bold">DocForge</h1>
          <p className="text-sm text-muted-foreground mt-1">Sign in to your account</p>
        </div>
        <form onSubmit={handleSubmit((v) => login.mutate(v))} className="space-y-4">
          <div className="space-y-1">
            <Label htmlFor="username">Username</Label>
            <Input id="username" autoComplete="username" {...register('username')} />
            {errors.username && <p className="text-xs text-destructive">{errors.username.message}</p>}
          </div>
          <div className="space-y-1">
            <Label htmlFor="password">Password</Label>
            <Input id="password" type="password" autoComplete="current-password" {...register('password')} />
            {errors.password && <p className="text-xs text-destructive">{errors.password.message}</p>}
          </div>
          {login.error && (
            <p className="text-xs text-destructive">
              Login failed. Check your credentials.
            </p>
          )}
          <Button type="submit" className="w-full" disabled={login.isPending}>
            {login.isPending ? 'Signing in…' : 'Sign in'}
          </Button>
        </form>
      </div>
    </div>
  )
}
