'use client'

import { useState, FormEvent } from 'react'
import { useRouter } from 'next/navigation'
import { useCreateNewChatroomChatroomsPost } from '@/lib/api/generated/chatrooms/chatrooms'
import { useChatWithLlmChatroomsChatroomIdChatPost } from '@/lib/api/generated/chat/chat'
import {
  ChatHeader,
  ExampleQuestions,
  ChatInput,
  ChatFooter,
} from '@/components/chat'

export default function ChatPage() {
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const router = useRouter()

  const createChatroomMutation = useCreateNewChatroomChatroomsPost()
  const sendMessageMutation = useChatWithLlmChatroomsChatroomIdChatPost()

  const handleExampleClick = (question: string) => {
    setMessage(question)
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!message.trim() || isLoading) return

    setIsLoading(true)

    try {
      // 1. 새 채팅방 생성
      const chatroomResponse = await createChatroomMutation.mutateAsync({
        data: { title: message.substring(0, 50) + '...' },
      })

      const chatroomId = chatroomResponse.id

      // 2. 첫 메시지 전송
      await sendMessageMutation.mutateAsync({
        chatroomId,
        data: { message: message },
      })

      // 3. 채팅방으로 이동
      router.push(`/chat/${chatroomId}`)
    } catch (error) {
      console.error('Error creating chat:', error)
      alert('채팅을 시작하는 중 오류가 발생했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-6 py-8">
      <div className="w-full max-w-4xl">
        <ChatHeader />

        <ExampleQuestions
          onQuestionClick={handleExampleClick}
          isLoading={isLoading}
        />

        <ChatInput
          message={message}
          setMessage={setMessage}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />

        <ChatFooter />
      </div>
    </div>
  )
}
