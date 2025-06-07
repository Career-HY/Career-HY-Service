import { Button } from '@/components/shadcn/button'
import { PlusIcon } from 'lucide-react'

interface NewChatButtonProps {
  isCollapsed: boolean
  onNewChat: () => void
}

export default function NewChatButton({
  isCollapsed,
  onNewChat,
}: NewChatButtonProps) {
  return (
    <div className="p-4">
      <Button
        onClick={onNewChat}
        className={`w-full bg-gray-800 hover:bg-gray-700 text-white border border-gray-600 ${
          isCollapsed ? 'px-2' : 'px-4'
        }`}
      >
        <PlusIcon className="w-4 h-4" />
        {!isCollapsed && <span className="ml-2">새 채팅</span>}
      </Button>
    </div>
  )
}
