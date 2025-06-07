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
    <div className="flex h-screen bg-gray-50">
      <ChatSidebar
        isCollapsed={isCollapsed}
        onToggleCollapse={handleToggleCollapse}
      />

      {/* 메인 콘텐츠 영역 */}
      <div className="flex-1 flex flex-col">{children}</div>
    </div>
  )
}
