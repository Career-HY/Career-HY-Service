'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import LoginCard from './login-card'
import LoginInput from './login-input'
import { Button } from '@/components/shadcn/button'
import ErrorMessage from './error-message'
import { useCheckEmail, useSignup } from '@/hooks/useAuth'

export default function SignupForm() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [error, setError] = useState('')
  const [emailChecked, setEmailChecked] = useState(false)
  const [isCheckingEmail, setIsCheckingEmail] = useState(false)
  const router = useRouter()

  const { checkEmail } = useCheckEmail()
  const signupMutation = useSignup()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))

    // 이메일이 변경되면 중복체크 상태 초기화
    if (name === 'email') {
      setEmailChecked(false)
    }
  }

  const handleEmailCheck = async () => {
    if (!formData.email) {
      setError('이메일을 먼저 입력해주세요.')
      return
    }

    setError('')
    setIsCheckingEmail(true)

    try {
      const result = await checkEmail(formData.email)

      if (result.isDuplicate) {
        // 중복 이메일인 경우
        setError(result.message)
        setEmailChecked(false)
      } else {
        // 사용 가능한 이메일인 경우
        setEmailChecked(true)
      }
    } catch (err: unknown) {
      // 실제 네트워크 에러 등의 경우
      const error = err as { message?: string }
      setError(error.message || '이메일 중복체크 중 오류가 발생했습니다.')
      setEmailChecked(false)
    } finally {
      setIsCheckingEmail(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // 유효성 검사
    if (!formData.email || !formData.password || !formData.confirmPassword) {
      setError('모든 필드를 입력해주세요.')
      return
    }

    if (!emailChecked) {
      setError('이메일 중복체크를 먼저 해주세요.')
      return
    }

    if (formData.password !== formData.confirmPassword) {
      setError('비밀번호가 일치하지 않습니다.')
      return
    }

    if (formData.password.length < 6) {
      setError('비밀번호는 6자리 이상이어야 합니다.')
      return
    }

    try {
      await signupMutation.mutateAsync({
        data: {
          email: formData.email,
          pwd: formData.password,
        },
      })

      // 회원가입 성공 시 로그인 페이지로 이동
      alert('회원가입이 완료되었습니다! 로그인해주세요.')
      router.push('/')
    } catch (err: unknown) {
      const error = err as { message?: string }
      const errorMessage =
        error.message || '회원가입 중 오류가 발생했습니다. 다시 시도해주세요.'
      setError(errorMessage)
    }
  }

  const bottomLink = (
    <p className="text-gray-600 text-sm">
      이미 계정이 있으신가요?{' '}
      <Link
        href="/"
        className="text-blue-600 hover:text-blue-800 font-medium transition-colors"
      >
        로그인
      </Link>
    </p>
  )

  return (
    <LoginCard
      title="회원가입"
      subtitle1="Career-HY에 오신 것을 환영합니다!"
      description="취업 준비를 함께 시작해보세요"
      bottomLink={bottomLink}
    >
      <ErrorMessage message={error} />

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* 이메일 필드 + 중복체크 버튼 */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">
            이메일
          </label>
          <div className="flex gap-3 items-end">
            <div className="flex-[3]">
              <LoginInput
                id="email"
                name="email"
                type="email"
                label=""
                placeholder="student@hanyang.ac.kr"
                value={formData.email}
                onChange={handleChange}
                required
                disabled={isCheckingEmail}
                autoComplete="off"
              />
            </div>
            <Button
              type="button"
              disabled={!formData.email || emailChecked || isCheckingEmail}
              onClick={handleEmailCheck}
              variant="outline"
              className="flex-[1] min-w-[100px] h-9 disabled:opacity-70"
            >
              <div className="flex items-center justify-center">
                {isCheckingEmail ? (
                  <>
                    <div className="w-4 h-4 border-2 border-gray-600 border-t-transparent rounded-full animate-spin mr-1"></div>
                    확인중
                  </>
                ) : emailChecked ? (
                  <>✓ 완료</>
                ) : (
                  <>중복체크</>
                )}
              </div>
            </Button>
          </div>
          {emailChecked && (
            <p className="text-green-600 text-sm">✓ 사용 가능한 이메일입니다</p>
          )}
        </div>

        <LoginInput
          id="password"
          name="password"
          type="password"
          label="비밀번호"
          placeholder="비밀번호를 입력하세요 (6자리 이상)"
          value={formData.password}
          onChange={handleChange}
          required
          disabled={signupMutation.isPending}
          autoComplete="off"
        />

        <LoginInput
          id="confirmPassword"
          name="confirmPassword"
          type="password"
          label="비밀번호 확인"
          placeholder="비밀번호를 다시 입력하세요"
          value={formData.confirmPassword}
          onChange={handleChange}
          required
          disabled={signupMutation.isPending}
          autoComplete="off"
        />

        <Button
          type="submit"
          disabled={signupMutation.isPending}
          className="h-11 w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:from-blue-700 hover:to-blue-800 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-70"
        >
          {signupMutation.isPending ? (
            <div className="flex items-center">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
              가입 중...
            </div>
          ) : (
            '회원가입'
          )}
        </Button>
      </form>
    </LoginCard>
  )
}
