interface SidebarFooterProps {
  isCollapsed: boolean
}

export default function SidebarFooter({ isCollapsed }: SidebarFooterProps) {
  return (
    <div className="p-4 border-t border-gray-700">
      {!isCollapsed && (
        <div className="text-sm text-gray-400">사용자 정보 영역</div>
      )}
    </div>
  )
}
