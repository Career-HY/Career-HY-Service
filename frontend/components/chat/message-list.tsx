import { useRef, useEffect } from 'react'
import ChatMessage from './chat-message'
import UserMessage from './user-message'
import LoadingDots from './loading-dots'

interface JobRecommendation {
  rec_idx: string
  title: string
  url: string
  deadline: string
  start_date: string
  crawling_time: string
  recommendation_reason: string
}

interface ApiResponse {
  user_message: string
  llm_response: string
  recommended_jobs: JobRecommendation[]
  created_at: string
}

interface Message {
  id: number
  sender: 'user' | 'assistant'
  content: string
  apiResponse?: ApiResponse
  timestamp: string
}

interface MessageListProps {
  messages: Message[]
  isLoading: boolean
}

export default function MessageList({ messages, isLoading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {messages.map((message) => (
          <div key={message.id}>
            {message.sender === 'user' ? (
              <UserMessage
                content={message.content}
                timestamp={message.timestamp}
              />
            ) : (
              <ChatMessage
                content={message.content}
                apiResponse={message.apiResponse}
                timestamp={message.timestamp}
              />
            )}
          </div>
        ))}

        {/* 로딩 상태 */}
        {isLoading && <LoadingDots />}

        {/* 스크롤 앵커 */}
        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}
