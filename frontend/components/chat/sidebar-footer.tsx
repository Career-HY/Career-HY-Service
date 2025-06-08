'use client'

import { useRouter } from 'next/navigation'
import { User, ChevronRight } from 'lucide-react'
import { Button } from '@/components/shadcn/button'

interface SidebarFooterProps {
  isCollapsed: boolean
}

export default function SidebarFooter({ isCollapsed }: SidebarFooterProps) {
  const router = useRouter()

  const handleProfileClick = () => {
    router.push('/profile')
  }

  return (
    <div className="p-2 border-t border-gray-700">
      <Button
        variant="ghost"
        className={`w-full relative ${
          isCollapsed ? 'px-2' : 'px-4'
        } hover:bg-gray-800 text-gray-400 hover:text-gray-300`}
        onClick={handleProfileClick}
      >
        <User size={20} className="absolute left-4" />
        {!isCollapsed && (
          <>
            <span className="flex-1 text-center">프로필 관리</span>
            <ChevronRight size={16} className="absolute right-4" />
          </>
        )}
      </Button>
    </div>
  )
}
