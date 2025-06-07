import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useChatroomList, useUpdateChatroom } from '@/hooks/api'
import SidebarHeader from './sidebar-header'
import NewChatButton from './new-chat-button'
import ChatroomList from './chatroom-list'
import SidebarFooter from './sidebar-footer'

interface ChatSidebarProps {
  isCollapsed: boolean
  onToggleCollapse: () => void
}

export default function ChatSidebar({
  isCollapsed,
  onToggleCollapse,
}: ChatSidebarProps) {
  const router = useRouter()

  // 편집 상태 관리
  const [editingChatroomId, setEditingChatroomId] = useState<number | null>(
    null
  )
  const [editingTitle, setEditingTitle] = useState('')

  // 채팅방 목록 조회 API 연동
  const { data: chatrooms = [], isLoading, error } = useChatroomList()

  // 채팅방 수정 API 연동
  const updateChatroomMutation = useUpdateChatroom()

  const handleNewChat = () => {
    // TODO: 새 채팅방 생성 API 호출
    console.log('새 채팅 생성')
  }

  const handleChatroomClick = (chatroomId: number) => {
    // 편집 중이 아닐 때만 이동
    if (editingChatroomId === null) {
      console.log('채팅방 클릭:', chatroomId)
      router.push(`/chat/${chatroomId}`)
    }
  }

  const handleChatroomEdit = (chatroomId: number) => {
    // 현재 채팅방 이름 가져오기
    const chatroom = chatrooms.find((c) => c.id === chatroomId)
    const currentTitle = chatroom?.title || `채팅방 #${chatroomId}`

    setEditingChatroomId(chatroomId)
    setEditingTitle(currentTitle)
  }

  const handleChatroomSave = (chatroomId: number, newTitle: string) => {
    if (!newTitle.trim()) return

    updateChatroomMutation.mutate(
      {
        chatroomId,
        data: { title: newTitle.trim() },
      },
      {
        onSuccess: () => {
          setEditingChatroomId(null)
          setEditingTitle('')
        },
        onError: () => {
          setEditingChatroomId(null)
          setEditingTitle('')
        },
      }
    )
  }

  const handleChatroomCancel = () => {
    setEditingChatroomId(null)
    setEditingTitle('')
  }

  const handleChatroomDelete = (chatroomId: number) => {
    // TODO: 채팅방 삭제
    console.log('채팅방 삭제:', chatroomId)
  }

  return (
    <div
      className={`bg-gray-900 text-white transition-all duration-300 ${
        isCollapsed ? 'w-16' : 'w-64'
      } flex flex-col`}
    >
      <SidebarHeader
        isCollapsed={isCollapsed}
        onToggleCollapse={onToggleCollapse}
      />

      <NewChatButton isCollapsed={isCollapsed} onNewChat={handleNewChat} />

      <ChatroomList
        chatrooms={chatrooms}
        isCollapsed={isCollapsed}
        isLoading={isLoading}
        error={error}
        editingChatroomId={editingChatroomId}
        editingTitle={editingTitle}
        onChatroomClick={handleChatroomClick}
        onChatroomEdit={handleChatroomEdit}
        onChatroomSave={handleChatroomSave}
        onChatroomCancel={handleChatroomCancel}
        onChatroomDelete={handleChatroomDelete}
        onTitleChange={setEditingTitle}
      />

      <SidebarFooter isCollapsed={isCollapsed} />
    </div>
  )
}
