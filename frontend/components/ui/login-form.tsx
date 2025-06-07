'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useLogin } from '@/hooks/useAuth'
import LoginCard from './login-card'
import LoginInput from './login-input'
import { Button } from '@/components/shadcn/button'
import ErrorMessage from './error-message'

export default function LoginForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()

  const loginMutation = useLogin()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!email || !password) {
      setError('이메일과 비밀번호를 모두 입력해주세요.')
      return
    }

    try {
      await loginMutation.mutateAsync({
        data: {
          email,
          pwd: password,
        },
      })

      // 로그인 성공 시 채팅 페이지로 리다이렉트
      router.push('/chat')
    } catch (err: unknown) {
      // 에러 처리
      const error = err as { response?: { status: number } }
      if (error.response?.status === 401) {
        setError('이메일 또는 비밀번호가 올바르지 않습니다.')
      } else {
        setError('로그인 중 오류가 발생했습니다. 다시 시도해주세요.')
      }
    }
  }

  const bottomLink = (
    <p className="text-gray-600 text-sm">
      아직 계정이 없으신가요?{' '}
      <Link
        href="/signup"
        className="text-blue-600 hover:text-blue-800 font-medium transition-colors"
      >
        회원가입
      </Link>
    </p>
  )

  return (
    <LoginCard
      title="Career-HY"
      subtitle1="한양대학교 취업지원 포털에"
      subtitle2="오신 것을 환영합니다."
      description="Hanyang Career Support Portal"
      bottomLink={bottomLink}
    >
      <ErrorMessage message={error} />

      <form onSubmit={handleSubmit} className="space-y-5">
        <LoginInput
          id="email"
          name="email"
          type="text"
          label="이메일"
          placeholder="student@hanyang.ac.kr"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          disabled={loginMutation.isPending}
          autoComplete="username"
        />

        <LoginInput
          id="password"
          name="password"
          type="password"
          label="비밀번호"
          placeholder="비밀번호를 입력하세요"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          disabled={loginMutation.isPending}
          autoComplete="current-password"
        />

        <Button
          type="submit"
          disabled={loginMutation.isPending}
          className="h-11 w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-70"
        >
          {loginMutation.isPending ? (
            <div className="flex items-center">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              로그인 중...
            </div>
          ) : (
            '로그인'
          )}
        </Button>
      </form>
    </LoginCard>
  )
}
