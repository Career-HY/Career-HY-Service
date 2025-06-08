'use client'

import Link from 'next/link'
import { LogOut, User, Bookmark } from 'lucide-react'
import { Button } from '@/components/shadcn/button'

export default function Header() {
  return (
    <header className="sticky top-0 z-50 w-full">
      <div className="container h-14 max-w-screen-2xl mx-auto flex items-center justify-end pr-4">
        <nav className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            className="hover:bg-gray-200/70"
            asChild
          >
            <Link href="/profile" className="flex items-center space-x-1">
              <User className="h-4 w-4" />
              <span>프로필</span>
            </Link>
          </Button>

          <Button
            variant="ghost"
            size="sm"
            className="hover:bg-gray-200/70"
            disabled
          >
            <Bookmark className="h-4 w-4 mr-1" />
            <span>스크랩</span>
          </Button>

          <Button variant="ghost" size="sm" className="hover:bg-gray-200/70">
            <LogOut className="h-4 w-4 mr-1" />
            <span>로그아웃</span>
          </Button>
        </nav>
      </div>
    </header>
  )
}
