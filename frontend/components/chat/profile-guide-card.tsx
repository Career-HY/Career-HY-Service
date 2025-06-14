'use client'

import { useRouter } from 'next/navigation'
import { Button } from '@/components/shadcn/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/shadcn/card'
import { ArrowRight } from 'lucide-react'

export default function ProfileGuideCard() {
  const router = useRouter()

  return (
    <Card className="bg-blue-50 border-blue-200 mt-8 mb-10">
      <CardHeader>
        <CardTitle className="text-blue-800">
          프로필 정보를 입력해주세요
        </CardTitle>
        <CardDescription className="text-blue-600">
          더 정확한 채용 공고 추천을 위해 프로필 정보를 입력해주세요.
        </CardDescription>
      </CardHeader>
      <CardContent className="flex items-center justify-between">
        <p className="text-sm text-blue-600">
          학과, 수강 이력, 자격증 등의 정보를 입력하면 더 정확한 추천을 받을 수
          있습니다.
        </p>
        <Button
          variant="link"
          className="text-blue-700 font-semibold"
          onClick={() => router.push('/profile')}
        >
          프로필 작성하기
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      </CardContent>
    </Card>
  )
}
