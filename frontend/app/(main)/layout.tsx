'use client'

import { useState } from 'react'
import { ChatSidebar } from '@/components/chat'
import Header from '@/components/layout/Header'

export default function MainLayout({
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

      {/* 헤더와 메인 콘텐츠를 포함하는 오른쪽 영역 */}
      <div
        className={`flex-1 flex flex-col ${isCollapsed ? 'ml-16' : 'ml-64'}`}
      >
        <Header />
        <main className="flex-1">{children}</main>
      </div>
    </div>
  )
}
