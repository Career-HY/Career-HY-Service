'use client'

import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { LogOut, User, Bookmark } from 'lucide-react'
import { Button } from '@/components/shadcn/button'
import { useLogoutUsersLogoutPost } from '@/lib/api/generated/users/users'
import { useQueryClient } from '@tanstack/react-query'

export default function RightSidebar() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { mutate: logout } = useLogoutUsersLogoutPost({
    mutation: {
      onSuccess: () => {
        // 캐시 초기화
        queryClient.clear()
        // 로그인 페이지로 이동
        router.push('/')
      },
      onError: (error) => {
        console.error('로그아웃 중 오류가 발생했습니다:', error)
      },
    },
  })

  return (
    <div className="fixed right-0 top-0 h-full w-16 bg-white/80 backdrop-blur-sm border-l border-gray-200">
      <div className="flex flex-col items-center py-4 space-y-2">
        <Button
          variant="ghost"
          size="sm"
          className="hover:bg-gray-200/70 w-full justify-center"
          asChild
        >
          <Link
            href="/profile"
            className="flex flex-col items-center space-y-1"
          >
            <User className="h-4 w-4" />
            <span className="text-xs">프로필</span>
          </Link>
        </Button>

        <Button
          variant="ghost"
          size="sm"
          className="hover:bg-gray-200/70 w-full justify-center"
          disabled
        >
          <div className="flex flex-col items-center space-y-1">
            <Bookmark className="h-4 w-4" />
            <span className="text-xs">스크랩</span>
          </div>
        </Button>

        <Button
          variant="ghost"
          size="sm"
          className="hover:bg-gray-200/70 w-full justify-center"
          onClick={() => logout()}
        >
          <div className="flex flex-col items-center space-y-1">
            <LogOut className="h-4 w-4" />
            <span className="text-xs">로그아웃</span>
          </div>
        </Button>
      </div>
    </div>
  )
}
