import ChatroomItem from './chatroom-item'
import type { ChatroomRead } from '@/lib/api/generated/model'

interface ChatroomListProps {
  chatrooms: ChatroomRead[]
  isCollapsed: boolean
  isLoading?: boolean
  error?: any
  onChatroomClick?: (chatroomId: number) => void
  onChatroomEdit?: (chatroomId: number) => void
  onChatroomDelete?: (chatroomId: number) => void
}

export default function ChatroomList({
  chatrooms,
  isCollapsed,
  isLoading,
  error,
  onChatroomClick,
  onChatroomEdit,
  onChatroomDelete,
}: ChatroomListProps) {
  return (
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
          <ChatroomItem
            key={chatroom.id}
            chatroom={chatroom}
            isCollapsed={isCollapsed}
            onClick={onChatroomClick}
            onEdit={onChatroomEdit}
            onDelete={onChatroomDelete}
          />
        ))}
      </div>
    </div>
  )
}
