'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { useChatroomActions } from '@/hooks/api'
import ChatHeader from '@/components/chat/chat-header'
import ExampleQuestions from '@/components/chat/example-questions'
import ChatInput from '@/components/chat/chat-input'
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
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    const day = String(now.getDate()).padStart(2, '0')
    const hours = String(now.getHours()).padStart(2, '0')
    const minutes = String(now.getMinutes()).padStart(2, '0')

    return `${year}-${month}-${day} ${hours}:${minutes}`
  }

  const handleSendMessage = async (messageText: string) => {
    if (isProcessing) return

    setIsProcessing(true)

    try {
      // 1. 새 채팅방 생성 (날짜+시간 이름으로)
      const title = generateChatroomTitle()
      const newChatroom = await createMutation.mutateAsync({
        data: { title },
      })

      // 2. 채팅방으로 이동하면서 초기 메시지를 전달
      // 개별 채팅방 페이지에서 initialMessage를 받아서 자동 전송함
      router.push(
        `/chat/${newChatroom.id}?initialMessage=${encodeURIComponent(messageText)}`
      )
    } catch (error) {
      console.error('채팅방 생성 실패:', error)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleExampleClick = (question: string) => {
    setMessage(question)
  }

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!message.trim() || isProcessing) return

    handleSendMessage(message)
  }

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-6 py-8">
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
  )
}
