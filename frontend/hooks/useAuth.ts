'use client'

import { useQueryClient, useQuery } from '@tanstack/react-query'
import {
  useLoginUsersLoginPost,
  useSignupUsersSignupPost,
  useCheckEmailDuplicateUsersCheckEmailGet,
} from '@/lib/api/generated/users/users'

// 타입 정의
interface User {
  id: string
  email: string
  signup_date?: string
}

// 로그인 API 호출
export const useLogin = () => {
  const queryClient = useQueryClient()

  return useLoginUsersLoginPost({
    mutation: {
      onSuccess: (user) => {
        console.log('🎉 로그인 성공:', user)
        // 사용자 정보를 캐시에 저장
        queryClient.setQueryData(['currentUser'], user)
      },
      onError: (error) => {
        console.error('❌ 로그인 실패:', error)
      },
    },
  })
}

// 회원가입 API 호출
export const useSignup = () => {
  return useSignupUsersSignupPost({
    mutation: {
      onError: (error) => {
        console.error('회원가입 실패:', error)
      },
    },
  })
}

// 현재 사용자 정보 조회 (세션 확인)
export const useCurrentUser = () => {
  return useQuery({
    queryKey: ['currentUser'],
    queryFn: async (): Promise<User | null> => {
      try {
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

  return {
    mutate: () => {
      // 사용자 캐시 제거
      queryClient.removeQueries({ queryKey: ['currentUser'] })
      queryClient.clear()
    },
  }
}

// 이메일 중복체크 API 호출
export const useCheckEmail = () => {
  return useCheckEmailDuplicateUsersCheckEmailGet
}
