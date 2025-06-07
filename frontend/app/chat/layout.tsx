'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/shadcn/button'
import {
  PlusIcon,
  MessageSquareIcon,
  TrashIcon,
  EditIcon,
  HomeIcon,
} from 'lucide-react'
import { useGetMyChatroomsChatroomsGet } from '@/lib/api/generated/chatrooms/chatrooms'
import type { ChatroomRead } from '@/lib/api/generated/model'

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const router = useRouter()

  // 채팅방 목록 조회 API 연동
  const {
    data: chatrooms = [],
    isLoading,
    error,
  } = useGetMyChatroomsChatroomsGet()

  const formatChatTitle = (chatroom: ChatroomRead) => {
    if (chatroom.title) {
      return chatroom.title
    }
    // title이 없으면 날짜와 시간으로 표시
    const date = new Date(chatroom.created_at)
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`
  }

  const handleNewChat = () => {
    // TODO: 새 채팅방 생성 API 호출
    console.log('새 채팅 생성')
  }

  const handleGoHome = () => {
    router.push('/')
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* 사이드바 */}
      <div
        className={`bg-gray-900 text-white transition-all duration-300 ${
          isCollapsed ? 'w-16' : 'w-64'
        } flex flex-col`}
      >
        {/* 헤더 */}
        <div className="p-4 border-b border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {!isCollapsed && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleGoHome}
                  className="text-gray-300 hover:text-white hover:bg-gray-800 p-2"
                  title="홈으로 이동"
                >
                  <HomeIcon className="w-4 h-4" />
                </Button>
              )}
              {!isCollapsed && (
                <h1 className="text-lg font-semibold">Career-HY</h1>
              )}
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="text-gray-300 hover:text-white hover:bg-gray-800"
            >
              {isCollapsed ? '→' : '←'}
            </Button>
          </div>
        </div>

        {/* 새 채팅 버튼 */}
        <div className="p-4">
          <Button
            onClick={handleNewChat}
            className={`w-full bg-gray-800 hover:bg-gray-700 text-white border border-gray-600 ${
              isCollapsed ? 'px-2' : 'px-4'
            }`}
          >
            <PlusIcon className="w-4 h-4" />
            {!isCollapsed && <span className="ml-2">새 채팅</span>}
          </Button>
        </div>

        {/* 채팅방 목록 */}
        <div className="flex-1 overflow-y-auto">
          <div className="px-2">
            {isLoading && !isCollapsed && (
              <div className="p-3 text-center text-gray-400 text-sm">
                채팅방 목록을 불러오는 중...
              </div>
            )}

            {!!error && !isCollapsed && (
              <div className="p-3 text-center text-red-400 text-sm">
                채팅방 목록을 불러오지 못했습니다.
              </div>
            )}

            {chatrooms.length === 0 && !isLoading && !error && !isCollapsed && (
              <div className="p-3 text-center text-gray-500 text-sm">
                아직 채팅방이 없습니다.
              </div>
            )}

            {chatrooms.map((chatroom) => (
              <div
                key={chatroom.id}
                className="group flex items-center justify-between p-3 mb-1 rounded-lg hover:bg-gray-800 cursor-pointer transition-colors"
              >
                <div className="flex items-center flex-1 min-w-0">
                  <MessageSquareIcon className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  {!isCollapsed && (
                    <span className="ml-3 text-sm truncate text-gray-200">
                      {formatChatTitle(chatroom)}
                    </span>
                  )}
                </div>

                {!isCollapsed && (
                  <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="w-6 h-6 p-0 text-gray-400 hover:text-white hover:bg-gray-700"
                    >
                      <EditIcon className="w-3 h-3" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="w-6 h-6 p-0 text-gray-400 hover:text-red-400 hover:bg-gray-700"
                    >
                      <TrashIcon className="w-3 h-3" />
                    </Button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* 사용자 정보 영역 (나중에 추가) */}
        <div className="p-4 border-t border-gray-700">
          {!isCollapsed && (
            <div className="text-sm text-gray-400">사용자 정보 영역</div>
          )}
        </div>
      </div>

      {/* 메인 콘텐츠 영역 */}
      <div className="flex-1 flex flex-col">{children}</div>
    </div>
  )
}
