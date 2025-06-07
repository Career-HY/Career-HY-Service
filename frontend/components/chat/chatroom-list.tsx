import ChatroomItem from './chatroom-item'
import type { ChatroomRead } from '@/lib/api/generated/model'

interface ChatroomListProps {
  chatrooms: ChatroomRead[]
  isCollapsed: boolean
  isLoading: boolean
  error: unknown
  editingChatroomId: number | null
  editingTitle: string
  onChatroomClick: (chatroomId: number) => void
  onChatroomEdit: (chatroomId: number) => void
  onChatroomSave: (chatroomId: number, newTitle: string) => void
  onChatroomCancel: () => void
  onChatroomDelete: (chatroomId: number) => void
  onTitleChange: (title: string) => void
}

export default function ChatroomList({
  chatrooms,
  isCollapsed,
  isLoading,
  error,
  editingChatroomId,
  editingTitle = '',
  onChatroomClick,
  onChatroomEdit,
  onChatroomSave,
  onChatroomCancel,
  onChatroomDelete,
  onTitleChange,
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
            isEditing={editingChatroomId === chatroom.id}
            editingTitle={editingTitle}
            onChatroomClick={onChatroomClick}
            onChatroomEdit={onChatroomEdit}
            onChatroomSave={onChatroomSave}
            onChatroomCancel={onChatroomCancel}
            onChatroomDelete={onChatroomDelete}
            onTitleChange={onTitleChange}
          />
        ))}
      </div>
    </div>
  )
}
