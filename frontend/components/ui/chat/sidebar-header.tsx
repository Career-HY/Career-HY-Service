import { Button } from '@/components/shadcn/button'
import { HomeIcon } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface SidebarHeaderProps {
  isCollapsed: boolean
  onToggleCollapse: () => void
}

export default function SidebarHeader({
  isCollapsed,
  onToggleCollapse,
}: SidebarHeaderProps) {
  const router = useRouter()

  const handleGoHome = () => {
    router.push('/')
  }

  return (
    <div className="p-4 border-b border-gray-700">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          {!isCollapsed && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleGoHome}
              className="text-gray-300 hover:text-white hover:bg-gray-800 p-2"
              title="홈으로 이동"
            >
              <HomeIcon className="w-4 h-4" />
            </Button>
          )}
          {!isCollapsed && <h1 className="text-lg font-semibold">Career-HY</h1>}
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggleCollapse}
          className="text-gray-300 hover:text-white hover:bg-gray-800"
        >
          {isCollapsed ? '→' : '←'}
        </Button>
      </div>
    </div>
  )
}
