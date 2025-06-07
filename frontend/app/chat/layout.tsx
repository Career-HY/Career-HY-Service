'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/shadcn/button'
import { PlusIcon, MessageSquareIcon, TrashIcon, EditIcon } from 'lucide-react'
import { useGetMyChatroomsChatroomsGet } from '@/lib/api/generated/chatrooms/chatrooms'
import type { ChatroomRead } from '@/lib/api/generated/model'

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [isCollapsed, setIsCollapsed] = useState(false)

  // 채팅방 목록 조회 API 연동
  const {
    data: chatrooms = [],
    isLoading,
    error,
  } = useGetMyChatroomsChatroomsGet()

  // 디버깅용 로그
  useEffect(() => {
    console.log('🐛 채팅방 API 상태:', {
      chatrooms,
      isLoading,
      error,
      API_URL: process.env.NEXT_PUBLIC_API_URL,
    })

    // 쿠키 정보 확인
    console.log('🍪 현재 쿠키:', document.cookie)

    // 현재 URL과 API URL 확인
    console.log('🌐 현재 도메인:', window.location.origin)
    console.log('🎯 API 도메인:', process.env.NEXT_PUBLIC_API_URL)
  }, [chatrooms, isLoading, error])

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

  // 임시 테스트: 기존 api 인스턴스로 직접 호출
  const testDirectAPI = async () => {
    try {
      console.log('🧪 직접 API 호출 테스트 시작')
      const { api } = await import('@/lib/api/mutator')
      const response = await api.get('chatrooms')
      const data = await response.json()
      console.log('🧪 직접 API 성공:', data)
    } catch (error) {
      console.error('🧪 직접 API 에러:', error)
    }
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
            {!isCollapsed && (
              <h1 className="text-lg font-semibold">Career-HY</h1>
            )}
            <div className="flex items-center space-x-2">
              {/* 임시 테스트 버튼 */}
              {!isCollapsed && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={testDirectAPI}
                  className="text-yellow-400 hover:text-yellow-300 text-xs"
                >
                  Test
                </Button>
              )}
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
