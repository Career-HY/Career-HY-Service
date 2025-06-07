import { Button } from '@/components/shadcn/button'
import { MessageSquareIcon, EditIcon, TrashIcon } from 'lucide-react'
import type { ChatroomRead } from '@/lib/api/generated/model'

interface ChatroomItemProps {
  chatroom: ChatroomRead
  isCollapsed: boolean
  onEdit?: (chatroomId: number) => void
  onDelete?: (chatroomId: number) => void
  onClick?: (chatroomId: number) => void
}

export default function ChatroomItem({
  chatroom,
  isCollapsed,
  onEdit,
  onDelete,
  onClick,
}: ChatroomItemProps) {
  const formatChatTitle = (chatroom: ChatroomRead) => {
    if (chatroom.title) {
      return chatroom.title
    }
    // title이 없으면 날짜와 시간으로 표시
    const date = new Date(chatroom.created_at)
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`
  }

  const handleClick = () => {
    onClick?.(chatroom.id)
  }

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation()
    onEdit?.(chatroom.id)
  }

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation()
    onDelete?.(chatroom.id)
  }

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
