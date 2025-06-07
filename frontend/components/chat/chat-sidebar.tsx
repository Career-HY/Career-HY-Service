import { useGetMyChatroomsChatroomsGet } from '@/lib/api/generated/chatrooms/chatrooms'
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
  // 채팅방 목록 조회 API 연동
  const {
    data: chatrooms = [],
    isLoading,
    error,
  } = useGetMyChatroomsChatroomsGet()

  const handleNewChat = () => {
    // TODO: 새 채팅방 생성 API 호출
    console.log('새 채팅 생성')
  }

  const handleChatroomClick = (chatroomId: number) => {
    // TODO: 채팅방으로 이동
    console.log('채팅방 클릭:', chatroomId)
  }

  const handleChatroomEdit = (chatroomId: number) => {
    // TODO: 채팅방 편집
    console.log('채팅방 편집:', chatroomId)
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
        onChatroomClick={handleChatroomClick}
        onChatroomEdit={handleChatroomEdit}
        onChatroomDelete={handleChatroomDelete}
      />

      <SidebarFooter isCollapsed={isCollapsed} />
    </div>
  )
}
