'use client'

import { useState } from 'react'
import { ChatSidebar } from '@/components/chat'

export default function ChatLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [isCollapsed, setIsCollapsed] = useState(false)

  const handleToggleCollapse = () => {
    setIsCollapsed(!isCollapsed)
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* 고정된 사이드바 */}
      <div className="fixed inset-y-0 left-0 z-30">
        <ChatSidebar
          isCollapsed={isCollapsed}
          onToggleCollapse={handleToggleCollapse}
        />
      </div>

      {/* 메인 콘텐츠 영역 - 사이드바 너비만큼 마진 추가 */}
      <div
        className={`flex-1 flex flex-col ${isCollapsed ? 'ml-16' : 'ml-64'}`}
      >
        {children}
      </div>
    </div>
  )
}
