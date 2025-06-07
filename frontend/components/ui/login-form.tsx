'use client'

import { useState } from 'react'

export default function LoginForm() {
  const [userId, setUserId] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [saveId, setSaveId] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    // TODO: API 연동 로직 추가
    console.log('로그인 시도:', { userId, password, saveId })

    // 임시 로딩 시뮬레이션
    setTimeout(() => {
      setIsLoading(false)
    }, 1000)
  }

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-blue-800 rounded-full mx-auto mb-4 flex items-center justify-center">
            <span className="text-white font-bold text-xl">한</span>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Career-HY</h2>
          <p className="text-gray-600 mb-1">한양대학교 취업지원 포털에</p>
          <p className="text-gray-600 font-medium">오신 것을 환영합니다.</p>
          <p className="text-sm text-gray-500 mt-2">
            Hanyang Career Support Portal
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label
              htmlFor="userId"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              아이디
            </label>
            <input
              id="userId"
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="학번 또는 아이디를 입력하세요"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 placeholder-gray-400"
              required
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              비밀번호
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="비밀번호를 입력하세요"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 placeholder-gray-400"
              required
            />
          </div>

          <div className="flex items-center justify-between">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={saveId}
                onChange={(e) => setSaveId(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-600">아이디 저장</span>
            </label>
            <div className="flex space-x-2 text-sm">
              <a
                href="#"
                className="text-blue-600 hover:text-blue-800 transition-colors"
              >
                아이디 찾기
              </a>
              <span className="text-gray-400">|</span>
              <a
                href="#"
                className="text-blue-600 hover:text-blue-800 transition-colors"
              >
                비밀번호 찾기
              </a>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 px-4 rounded-lg font-medium hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                로그인 중...
              </div>
            ) : (
              '로그인'
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600 text-sm">
            아직 계정이 없으신가요?{' '}
            <a
              href="#"
              className="text-blue-600 hover:text-blue-800 font-medium transition-colors"
            >
              회원가입
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
