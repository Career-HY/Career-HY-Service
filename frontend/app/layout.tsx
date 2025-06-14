import type { Metadata } from 'next'
import './globals.css'
import { QueryProvider } from '@/components/providers/query-provider'

export const metadata: Metadata = {
  title: 'Career-HY | 맞춤 채용공고 추천 RAG 시스템',
  description:
    '한양대학교 학생들의 수강 이력과 개인 프로필을 기반으로 맞춤형 채용공고를 추천하는 AI 시스템',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="ko">
      <body className="antialiased">
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  )
}
