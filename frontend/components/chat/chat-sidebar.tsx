import { useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import {
  useChatroomList,
  useUpdateChatroom,
  useDeleteChatroom,
} from '@/hooks/api'
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
  const params = useParams()

  // 현재 접속중인 채팅방 ID
  const currentChatroomId = params?.chatroomId
    ? Number(params.chatroomId)
    : null

  // 편집 상태 관리
  const [editingChatroomId, setEditingChatroomId] = useState<number | null>(
    null
  )
  const [editingTitle, setEditingTitle] = useState('')

  // 채팅방 목록 조회 API 연동
  const { data: chatrooms = [], isLoading, error } = useChatroomList()

  // 채팅방 수정 API 연동
  const updateChatroomMutation = useUpdateChatroom()

  // 채팅방 삭제 API 연동
  const deleteChatroomMutation = useDeleteChatroom()

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
    // 삭제 확인
    if (!window.confirm('정말로 이 채팅방을 삭제하시겠습니까?')) {
      return
    }

    deleteChatroomMutation.mutate(
      { chatroomId },
      {
        onSuccess: () => {
          // 삭제된 채팅방이 현재 보고 있는 채팅방이면 메인 페이지로 이동
          if (currentChatroomId === chatroomId) {
            router.push('/chat')
          }
          console.log('채팅방 삭제 완료:', chatroomId)
        },
        onError: (error) => {
          console.error('채팅방 삭제 실패:', error)
          alert('채팅방 삭제에 실패했습니다. 다시 시도해주세요.')
        },
      }
    )
  }

  return (
    <div
      className={`bg-gray-900 text-white transition-all duration-300 ${
        isCollapsed ? 'w-16' : 'w-64'
      } flex flex-col h-full`}
    >
      <SidebarHeader
        isCollapsed={isCollapsed}
        onToggleCollapse={onToggleCollapse}
      />

      <NewChatButton isCollapsed={isCollapsed} />

      <ChatroomList
        chatrooms={chatrooms}
        isCollapsed={isCollapsed}
        isLoading={isLoading}
        error={error}
        currentChatroomId={currentChatroomId}
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
