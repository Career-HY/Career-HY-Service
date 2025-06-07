'use client'

import { useState } from 'react'
import { Button } from '@/components/shadcn/button'
import { PlusIcon, MessageSquareIcon, TrashIcon, EditIcon } from 'lucide-react'

interface ChatroomItem {
  id: number
  title: string | null
  created_at: string
}

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [chatrooms, setChatrooms] = useState<ChatroomItem[]>([])
  const [isCollapsed, setIsCollapsed] = useState(false)

  // 임시 더미 데이터 (나중에 API 연동)
  const dummyChatrooms: ChatroomItem[] = [
    {
      id: 1,
      title: '프론트엔드 개발자 취업 상담',
      created_at: '2024-01-15T10:30:00Z',
    },
    { id: 2, title: null, created_at: '2024-01-14T15:45:00Z' },
    {
      id: 3,
      title: '백엔드 개발 커리어 질문',
      created_at: '2024-01-13T09:20:00Z',
    },
  ]

  const formatChatTitle = (chatroom: ChatroomItem) => {
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
            {dummyChatrooms.map((chatroom) => (
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
