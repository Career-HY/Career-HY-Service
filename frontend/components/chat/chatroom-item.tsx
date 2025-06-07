import { Button } from '@/components/shadcn/button'
import { MessageSquareIcon, EditIcon, TrashIcon, Check, X } from 'lucide-react'
import type { ChatroomRead } from '@/lib/api/generated/model'

interface ChatroomItemProps {
  chatroom: ChatroomRead
  isCollapsed: boolean
  isEditing?: boolean
  editingTitle?: string
  onChatroomClick: (chatroomId: number) => void
  onChatroomEdit: (chatroomId: number) => void
  onChatroomSave: (chatroomId: number, newTitle: string) => void
  onChatroomCancel: () => void
  onChatroomDelete: (chatroomId: number) => void
  onTitleChange: (title: string) => void
}

export default function ChatroomItem({
  chatroom,
  isCollapsed,
  isEditing = false,
  editingTitle = '',
  onChatroomClick,
  onChatroomEdit,
  onChatroomSave,
  onChatroomCancel,
  onChatroomDelete,
  onTitleChange,
}: ChatroomItemProps) {
  const formatChatTitle = (chatroom: ChatroomRead) => {
    if (chatroom.title) {
      return chatroom.title
    }
    return `채팅방 #${chatroom.id}`
  }

  const handleClick = () => {
    if (!isEditing) {
      onChatroomClick(chatroom.id)
    }
  }

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation()
    onChatroomEdit(chatroom.id)
  }

  const handleSave = (e: React.MouseEvent) => {
    e.stopPropagation()
    onChatroomSave(chatroom.id, editingTitle)
  }

  const handleCancel = (e: React.MouseEvent) => {
    e.stopPropagation()
    onChatroomCancel()
  }

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation()
    onChatroomDelete(chatroom.id)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      onChatroomSave(chatroom.id, editingTitle)
    } else if (e.key === 'Escape') {
      onChatroomCancel()
    }
  }

  if (isEditing && !isCollapsed) {
    // 편집 모드: 전체 행을 편집 UI로 사용
    return (
      <div className="group p-3 mb-1 rounded-lg bg-gray-800">
        <div className="flex items-center space-x-2">
          <MessageSquareIcon className="w-4 h-4 text-gray-400 flex-shrink-0" />
          <input
            type="text"
            value={editingTitle}
            onChange={(e) => onTitleChange(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 text-sm bg-gray-700 text-gray-200 border border-gray-600 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-0"
            placeholder="채팅방 이름을 입력하세요"
            autoFocus
            onClick={(e) => e.stopPropagation()}
          />
          <div className="flex items-center space-x-1 flex-shrink-0">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleSave}
              className="w-6 h-6 p-0 text-green-400 hover:text-green-300 hover:bg-gray-700"
            >
              <Check className="w-3 h-3" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCancel}
              className="w-6 h-6 p-0 text-red-400 hover:text-red-300 hover:bg-gray-700"
            >
              <X className="w-3 h-3" />
            </Button>
          </div>
        </div>
      </div>
    )
  }

  // 일반 모드
  return (
    <div
      onClick={handleClick}
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
            onClick={handleEdit}
            className="w-6 h-6 p-0 text-gray-400 hover:text-white hover:bg-gray-700"
          >
            <EditIcon className="w-3 h-3" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleDelete}
            className="w-6 h-6 p-0 text-gray-400 hover:text-red-400 hover:bg-gray-700"
          >
            <TrashIcon className="w-3 h-3" />
          </Button>
        </div>
      )}
    </div>
  )
}
