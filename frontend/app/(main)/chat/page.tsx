'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { useChatroomActions } from '@/hooks/api'
import { ProfileGuideCard } from '@/components/chat'
import { setPendingMessage } from '@/store/chat'
import ChatInput from '@/components/chat/chat-input'
import ChatHeader from '@/components/chat/chat-header'
import ExampleQuestions from '@/components/chat/example-questions'
import ChatFooter from '@/components/chat/chat-footer'

export default function ChatPage() {
  const router = useRouter()
  const [message, setMessage] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)

  // 채팅방 생성 API 연동
  const { createMutation } = useChatroomActions()

  // 현재 날짜+시간으로 채팅방 이름 생성
  const generateChatroomTitle = () => {
    const now = new Date()
    return `채팅 ${now.toLocaleString()}`
  }

  const handleExampleClick = (question: string) => {
    setMessage(question)
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!message.trim() || isProcessing) return

    try {
      setIsProcessing(true)
      // 1. 채팅방 생성
      const chatroom = await createMutation.mutateAsync({
        data: { title: generateChatroomTitle() },
      })

      // 2. 전역 상태에 메시지 저장
      setPendingMessage(chatroom.id, message.trim())

      // 3. 생성된 채팅방으로 이동
      router.push(`/chat/${chatroom.id}`)
    } catch (error) {
      console.error('채팅방 생성 실패:', error)
      alert('채팅방 생성에 실패했습니다. 다시 시도해주세요.')
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="container mx-auto p-6">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* <h1 className="text-3xl font-bold">새 채팅</h1> */}
        <ProfileGuideCard />

        <div className="flex-1 flex flex-col items-center justify-center">
          <div className="w-full max-w-4xl">
            <ChatHeader />

            <ExampleQuestions
              onQuestionClick={handleExampleClick}
              isLoading={isProcessing}
            />

            <ChatInput
              message={message}
              setMessage={setMessage}
              onSubmit={handleSubmit}
              isLoading={isProcessing}
            />

            <ChatFooter />
          </div>
        </div>
      </div>
    </div>
  )
}
