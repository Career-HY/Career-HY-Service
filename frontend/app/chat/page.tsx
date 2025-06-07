'use client'

import Image from 'next/image'

export default function ChatPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 mx-auto mb-4 flex items-center justify-center">
          <Image
            src="/images/logos/careerhy.png"
            alt="Career-HY"
            width={64}
            height={64}
            className="object-contain"
          />
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">로그인 성공!</h1>
        <p className="text-gray-600">Career-HY 채팅 페이지입니다.</p>
        <p className="text-sm text-gray-500 mt-4">
          UI는 다음 이슈에서 작업 예정
        </p>
      </div>
    </div>
  )
}
