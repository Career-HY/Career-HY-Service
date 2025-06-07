'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { useCreateChatroom } from '@/hooks/api'
import ChatHeader from '@/components/chat/chat-header'
import ExampleQuestions from '@/components/chat/example-questions'
import ChatInput from '@/components/chat/chat-input'
import ChatFooter from '@/components/chat/chat-footer'

export default function ChatPage() {
  const router = useRouter()
  const [message, setMessage] = useState('')

  // 새 채팅방 생성 API 연동
  const createChatroomMutation = useCreateChatroom()

  const handleSendMessage = async (messageText: string) => {
    try {
      // 1. 새 채팅방 생성
      const newChatroom = await createChatroomMutation.mutateAsync({
        data: { title: messageText.slice(0, 30) + '...' },
      })

      // 2. 새 채팅방으로 이동하면서 메시지 전달
      router.push(
        `/chat/${newChatroom.id}?initialMessage=${encodeURIComponent(messageText)}`
      )
    } catch (error) {
      console.error('채팅방 생성 실패:', error)
    }
  }

  const handleExampleClick = (question: string) => {
    setMessage(question)
  }

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!message.trim() || createChatroomMutation.isPending) return

    handleSendMessage(message)
  }

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-6 py-8">
      <div className="w-full max-w-4xl">
        <ChatHeader />

        <ExampleQuestions
          onQuestionClick={handleExampleClick}
          isLoading={createChatroomMutation.isPending}
        />

        <ChatInput
          message={message}
          setMessage={setMessage}
          onSubmit={handleSubmit}
          isLoading={createChatroomMutation.isPending}
        />

        <ChatFooter />
      </div>
    </div>
  )
}
