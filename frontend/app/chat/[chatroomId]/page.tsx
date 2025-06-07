'use client'

import { useState, useEffect, useRef } from 'react'
import { useParams, useSearchParams } from 'next/navigation'
import { useChatroomDetail, useChatActions } from '@/hooks/api'
import { MessageList, ChatInput } from '@/components/chat'

// 더미 데이터
const dummyMessages = [
  {
    id: 1,
    sender: 'user' as const,
    content:
      '머신러닝 엔지니어링에 관심이 많은데 지금 지원할 수 있는 기업의 채용공고를 보여줄래?',
    timestamp: '2024-12-19 19:00',
  },
  {
    id: 2,
    sender: 'assistant' as const,
    content: '',
    apiResponse: {
      user_message:
        '머신러닝 엔지니어링에 관심이 많은데 지금 지원할 수 있는 기업의 채용공고를 보여줄래?',
      llm_response: `안녕하세요! 머신러닝 엔지니어링 분야의 채용공고를 찾아드릴게요. 현재 지원 가능한 기업들을 추천해드립니다.

## 추천 채용공고

머신러닝 엔지니어링 분야에서 현재 채용 중인 기업들입니다:`,
      recommended_jobs: [
        {
          rec_idx: '501',
          title: '머신러닝 엔지니어',
          url: 'https://example.com/job/501',
          deadline: '2024-12-30',
          start_date: '2024-12-01 00:00',
          crawling_time: '2024-12-19 10:00:00',
          recommendation_reason:
            'AI 플랫폼 개발 및 머신러닝 모델 설계/구현 역량을 기를 수 있는 좋은 기회입니다.',
        },
        {
          rec_idx: '502',
          title: 'AI/ML 엔지니어',
          url: 'https://example.com/job/502',
          deadline: '2024-12-25',
          start_date: '2024-12-01 00:00',
          crawling_time: '2024-12-19 10:00:00',
          recommendation_reason:
            '추천 시스템 및 검색 엔진 ML 모델 개발 경험을 쌓을 수 있습니다.',
        },
        {
          rec_idx: '503',
          title: '머신러닝 플랫폼 개발자',
          url: 'https://example.com/job/503',
          deadline: '2025-01-15',
          start_date: '2024-12-01 00:00',
          crawling_time: '2024-12-19 10:00:00',
          recommendation_reason:
            'ML 플랫폼 구축 및 데이터 파이프라인 개발 역량을 기를 수 있습니다.',
        },
      ],
      created_at: '2024-12-19T10:01:30Z',
    },
    timestamp: '2024-12-19 19:01',
  },
]

export default function ChatroomPage() {
  const params = useParams()
  const searchParams = useSearchParams()
  const chatroomId = Number(params.chatroomId)
  const initialMessage = searchParams.get('initialMessage')

  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<any[]>([])
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // 123번은 더미데이터, 나머지는 실제 API 호출
  const isDemoRoom = chatroomId === 123

  // API hooks
  const { data: chatroomData, isLoading: isLoadingChatroom } =
    useChatroomDetail(chatroomId, !isDemoRoom)

  const { sendMessage: sendMessageAPI, isSending } = useChatActions(chatroomId)

  // 초기 메시지 설정
  useEffect(() => {
    if (isDemoRoom) {
      // 데모 채팅방: 더미 데이터 사용
      setMessages(dummyMessages)
    } else if (chatroomData?.messages) {
      // 실제 API 데이터 변환
      const convertedMessages = chatroomData.messages.map((msg: any) => {
        if (msg.sender === 'user') {
          return {
            id: msg.id,
            sender: 'user',
            content: msg.content || '',
            timestamp: new Date(msg.created_at).toLocaleString(),
          }
        } else {
          // AI 메시지는 apiResponse 구조로 변환
          return {
            id: msg.id,
            sender: 'assistant',
            content: '',
            apiResponse: {
              user_message: '', // 이전 사용자 메시지 (필요시 찾아서 연결)
              llm_response: msg.content || '',
              recommended_jobs: [], // 기존 메시지에는 추천 공고가 없을 수 있음
              created_at: msg.created_at,
            },
            timestamp: new Date(msg.created_at).toLocaleString(),
          }
        }
      })
      setMessages(convertedMessages)
    }
  }, [isDemoRoom, chatroomData])

  // URL 파라미터로 전달된 초기 메시지가 있다면 자동 전송
  useEffect(() => {
    if (initialMessage && !isDemoRoom) {
      handleSendMessage(initialMessage)
    }
  }, [initialMessage, isDemoRoom])

  // 메시지 목록 하단으로 스크롤
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (messageText: string) => {
    if (!messageText.trim() || isSending) return

    // 사용자 메시지 즉시 추가
    const userMessage = {
      id: Date.now(),
      sender: 'user' as const,
      content: messageText,
      timestamp: new Date().toLocaleString(),
    }
    setMessages((prev) => [...prev, userMessage])
    setMessage('')

    if (isDemoRoom) {
      // 데모 채팅방: 더미 응답
      setTimeout(() => {
        const assistantMessage = {
          id: Date.now() + 1,
          sender: 'assistant' as const,
          content: '',
          apiResponse: {
            user_message: messageText,
            llm_response:
              '이것은 데모 채팅방입니다. 실제 AI 응답을 보시려면 다른 채팅방을 이용해주세요.',
            recommended_jobs: [],
            created_at: new Date().toISOString(),
          },
          timestamp: new Date().toLocaleString(),
        }
        setMessages((prev) => [...prev, assistantMessage])
      }, 1000)
    } else {
      // 실제 API 호출
      try {
        const response = await sendMessageAPI(messageText)

        if (response) {
          const assistantMessage = {
            id: Date.now() + 1,
            sender: 'assistant' as const,
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
        const errorMessage = {
          id: Date.now() + 1,
          sender: 'assistant' as const,
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

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    handleSendMessage(message)
  }

  const chatroomTitle = isDemoRoom
    ? '📚 데모 채팅방'
    : chatroomData?.title || `💬 채팅방 #${chatroomId}`

  return (
    <div className="flex flex-col h-full bg-white">
      {/* 헤더 (채팅방 정보 표시) */}
      <div className="border-b border-gray-200 p-4 bg-gray-50">
        <div className="text-sm text-gray-600">
          {isDemoRoom ? (
            <span className="inline-flex items-center">
              📚 데모 채팅방 (더미데이터)
            </span>
          ) : (
            <span className="inline-flex items-center">💬 {chatroomTitle}</span>
          )}
        </div>
      </div>

      {/* 메시지 영역 */}
      {isLoadingChatroom && !isDemoRoom ? (
        <div className="flex justify-center items-center h-full">
          <div className="text-gray-500">채팅방 로딩 중...</div>
        </div>
      ) : (
        <MessageList messages={messages} isLoading={isSending} />
      )}

      {/* 입력 영역 */}
      <div className="border-t border-gray-200 p-6 bg-white">
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
