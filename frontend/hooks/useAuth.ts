'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api/mutator'

// 타입 정의
interface LoginRequest {
  email: string
  pwd: string
}

interface SignupRequest {
  email: string
  pwd: string
}

interface User {
  id: string
  email: string
  signup_date?: string
}

// 로그인 API 호출
export const useLogin = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (credentials: LoginRequest): Promise<User> => {
      try {
        console.log('🚀 로그인 요청:', credentials)

        const response = await api.post('users/login', {
          json: credentials,
        })

        console.log('✅ 응답 받음 - 상태:', response.status)
        console.log('📋 응답 헤더:', response.headers)

        // 응답 텍스트를 먼저 확인
        const responseText = await response.text()
        console.log('📄 응답 텍스트:', responseText)

        // JSON 파싱
        const data = JSON.parse(responseText) as User
        console.log('📦 파싱된 데이터:', data)

        return data
      } catch (error) {
        console.error('💥 로그인 과정에서 에러:', error)
        throw error
      }
    },
    onSuccess: (user) => {
      console.log('🎉 로그인 성공:', user)
      // 사용자 정보를 캐시에 저장
      queryClient.setQueryData(['currentUser'], user)
    },
    onError: (error) => {
      console.error('❌ 로그인 실패:', error)
    },
  })
}

// 회원가입 API 호출
export const useSignup = () => {
  return useMutation({
    mutationFn: async (userData: SignupRequest): Promise<User> => {
      const response = await api
        .post('users/signup', {
          json: userData,
        })
        .json<User>()
      return response
    },
    onError: (error) => {
      console.error('회원가입 실패:', error)
    },
  })
}

// 현재 사용자 정보 조회 (세션 확인)
export const useCurrentUser = () => {
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: async (): Promise<User | null> => {
      try {
        // 세션이 유지되고 있는지 확인하는 엔드포인트가 필요할 수 있습니다
        // 현재는 로그인 시에만 사용자 정보를 설정합니다
        return null
      } catch (error) {
        return null
      }
    },
    staleTime: 1000 * 60 * 5, // 5분
    retry: false,
  })
}

// 로그아웃
export const useLogout = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (): Promise<void> => {
      // 백엔드에 로그아웃 엔드포인트가 있다면 호출
      // await api.post('users/logout')
      // 현재는 클라이언트에서만 세션 정리
    },
    onSuccess: () => {
      // 사용자 캐시 제거
      queryClient.removeQueries({ queryKey: ['currentUser'] })
      queryClient.clear()
    },
  })
}

// 이메일 중복체크 API 호출
export const useCheckEmail = () => {
  return useMutation({
    mutationFn: async (
      email: string
    ): Promise<{
      message: string
      available: boolean
      isDuplicate?: boolean
    }> => {
      try {
        console.log('🔍 이메일 중복체크 요청:', email)

        const response = await api.get(
          `users/check-email?email=${encodeURIComponent(email)}`
        )
        const data = await response.json<{
          message: string
          available: boolean
        }>()

        return data
      } catch (error: any) {
        // 409 상태 코드 (중복)인 경우 - 에러가 아닌 정상 응답으로 처리
        if (error.response?.status === 409) {
          return {
            message: '이미 사용 중인 이메일입니다',
            available: false,
            isDuplicate: true,
          }
        }

        // 실제 에러인 경우만 throw
        console.error('❌ 실제 이메일 중복체크 에러:', error)
        throw new Error('이메일 확인 중 오류가 발생했습니다')
      }
    },
    onSuccess: (data) => {
      console.log('🎉 이메일 중복체크 완료:', data)
    },
    onError: (error) => {
      console.error('💥 이메일 중복체크 에러:', error)
    },
  })
}
