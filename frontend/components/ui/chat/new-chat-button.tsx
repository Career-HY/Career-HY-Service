import { Button } from '@/components/shadcn/button'
import { PlusIcon } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface NewChatButtonProps {
  isCollapsed: boolean
  onNewChat?: () => void
}

export default function NewChatButton({
  isCollapsed,
  onNewChat,
}: NewChatButtonProps) {
  const router = useRouter()

  const handleNewChat = () => {
    // 메인 채팅 페이지로 이동
    router.push('/chat')

    // 추가 콜백이 있다면 실행
    if (onNewChat) {
      onNewChat()
    }
  }

  return (
    <div className="p-4">
      <Button
        onClick={handleNewChat}
        className={`w-full bg-gray-800 hover:bg-gray-700 text-white border border-gray-600 flex justify-center items-center ${
          isCollapsed ? 'px-2' : 'px-4'
        }`}
      >
        <PlusIcon className="w-4 h-4" />
        {!isCollapsed && <span className="mr-2">새 채팅</span>}
      </Button>
    </div>
  )
}
