'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams } from 'next/navigation'
import { useChatroomDetail, useChatActions } from '@/hooks/api'
import { MessageList, ChatInput } from '@/components/chat'
import type { RecommendedJob } from '@/lib/api/generated/model'
import { pendingMessage, clearPendingMessage } from '@/store/chat'

interface ApiResponse {
  user_message: string
  llm_response: string
  recommended_jobs: RecommendedJob[]
  created_at: string
}

interface Message {
  id: number
  sender: 'user' | 'assistant'
  content: string
  apiResponse?: ApiResponse
  timestamp: string
}

// DB에서 가져온 메시지의 타입
interface DBMessage {
  id: number
  chat_room_id: number
  sender: string
  content: string | null
  recommended_jobs?: RecommendedJob[]
  created_at: string
}

export default function ChatroomPage() {
  const params = useParams()
  const chatroomId = Number(params.chatroomId)

  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<Message[]>(() => {
    // 컴포넌트 마운트 시 pendingMessage가 있으면 초기 메시지로 설정
    if (pendingMessage && pendingMessage.chatroomId === chatroomId) {
      const userMessage: Message = {
        id: Date.now(),
        sender: 'user',
        content: pendingMessage.message,
        timestamp: new Date().toLocaleString(),
      }
      return [userMessage]
    }
    return []
  })
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // API hooks
  const { data: chatroomData, isLoading: isLoadingChatroom } =
    useChatroomDetail(chatroomId, true)

  const { sendMessage: sendMessageAPI, isSending } = useChatActions(chatroomId)

  const handleSendMessage = useCallback(
    async (messageText: string) => {
      if (!messageText.trim() || isSending) return

      // 사용자 메시지 즉시 추가
      const userMessage: Message = {
        id: Date.now(),
        sender: 'user',
        content: messageText,
        timestamp: new Date().toLocaleString(),
      }
      setMessages((prev) => [...prev, userMessage])
      setMessage('')

      // 실제 API 호출
      try {
        const response = await sendMessageAPI(messageText)

        if (response) {
          const assistantMessage: Message = {
            id: Date.now() + 1,
            sender: 'assistant',
            content: '',
            apiResponse: {
              user_message: response.user_message || messageText,
              llm_response: response.llm_response || '',
              recommended_jobs: response.recommended_jobs || [],
              created_at: response.created_at || new Date().toISOString(),
            },
            timestamp: new Date().toLocaleString(),
          }
          setMessages((prev) => [...prev, assistantMessage])
        }
      } catch (error) {
        console.error('메시지 전송 실패:', error)
        // 에러 메시지 표시
        const errorMessage: Message = {
          id: Date.now() + 1,
          sender: 'assistant',
          content: '',
          apiResponse: {
            user_message: messageText,
            llm_response:
              '죄송합니다. 메시지 전송 중 오류가 발생했습니다. 다시 시도해주세요.',
            recommended_jobs: [],
            created_at: new Date().toISOString(),
          },
          timestamp: new Date().toLocaleString(),
        }
        setMessages((prev) => [...prev, errorMessage])
      }
    },
    [isSending, sendMessageAPI]
  )

  // pendingMessage 처리
  useEffect(() => {
    const processPendingMessage = async () => {
      if (pendingMessage && pendingMessage.chatroomId === chatroomId) {
        const messageText = pendingMessage.message
        clearPendingMessage()

        try {
          const response = await sendMessageAPI(messageText)

          if (response) {
            const assistantMessage: Message = {
              id: Date.now() + 1,
              sender: 'assistant',
              content: '',
              apiResponse: {
                user_message: response.user_message || messageText,
                llm_response: response.llm_response || '',
                recommended_jobs: response.recommended_jobs || [],
                created_at: response.created_at || new Date().toISOString(),
              },
              timestamp: new Date().toLocaleString(),
            }
            setMessages((prev) => [...prev, assistantMessage])
          }
        } catch (error) {
          console.error('메시지 전송 실패:', error)
          const errorMessage: Message = {
            id: Date.now() + 1,
            sender: 'assistant',
            content: '',
            apiResponse: {
              user_message: messageText,
              llm_response:
                '죄송합니다. 메시지 전송 중 오류가 발생했습니다. 다시 시도해주세요.',
              recommended_jobs: [],
              created_at: new Date().toISOString(),
            },
            timestamp: new Date().toLocaleString(),
          }
          setMessages((prev) => [...prev, errorMessage])
        }
      }
    }

    processPendingMessage()
  }, [chatroomId, sendMessageAPI])

  // 채팅 히스토리 로드
  useEffect(() => {
    if (chatroomData?.messages && messages.length === 0) {
      // 메시지를 시간순으로 정렬
      const sortedMessages = [...chatroomData.messages].sort(
        (a, b) =>
          new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      )

      const convertedMessages: Message[] = []

      // 메시지들을 순회하면서 user와 assistant 메시지 쌍으로 처리
      for (let i = 0; i < sortedMessages.length; i++) {
        const msg = sortedMessages[i] as DBMessage

        if (msg.sender === 'user') {
          // 사용자 메시지
          convertedMessages.push({
            id: msg.id,
            sender: 'user',
            content: msg.content || '',
            timestamp: new Date(msg.created_at).toLocaleString(),
          })

          // 다음 메시지가 있고 assistant의 응답인 경우
          const nextMsg = sortedMessages[i + 1] as DBMessage
          if (nextMsg && nextMsg.sender === 'llm') {
            convertedMessages.push({
              id: nextMsg.id,
              sender: 'assistant',
              content: '',
              apiResponse: {
                user_message: msg.content || '', // 이전 사용자 메시지
                llm_response: nextMsg.content || '',
                recommended_jobs: nextMsg.recommended_jobs || [],
                created_at: nextMsg.created_at,
              },
              timestamp: new Date(nextMsg.created_at).toLocaleString(),
            })
            i++ // 다음 메시지는 이미 처리했으므로 건너뛰기
          }
        }
      }

      setMessages(convertedMessages)
    }
  }, [chatroomData, messages.length])

  // 메시지 목록 하단으로 스크롤
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    handleSendMessage(message)
  }

  return (
    <div className="flex flex-col h-full">
      {/* 메시지 영역 */}
      {isLoadingChatroom ? (
        <div className="flex justify-center items-center h-full">
          <div className="text-gray-500">채팅방 로딩 중...</div>
        </div>
      ) : (
        <MessageList messages={messages} isLoading={isSending} />
      )}

      {/* 입력 영역 */}
      <div className="border-t border-gray-200 p-6">
        <ChatInput
          message={message}
          setMessage={setMessage}
          onSubmit={handleSubmit}
          isLoading={isSending}
        />
      </div>
    </div>
  )
}
