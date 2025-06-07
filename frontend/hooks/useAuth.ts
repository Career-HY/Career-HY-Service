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
      const response = await api
        .post('users/login', {
          json: credentials,
        })
        .json<User>()
      return response
    },
    onSuccess: (user) => {
      // 사용자 정보를 캐시에 저장
      queryClient.setQueryData(['currentUser'], user)
    },
    onError: (error) => {
      console.error('로그인 실패:', error)
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
