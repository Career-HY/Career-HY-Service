'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { ChatInput, MessageList } from '@/components/chat'
import { useGetChatroomDetailChatroomsChatroomIdGet } from '@/lib/api/generated/chatrooms/chatrooms'
import { useChatWithLlmChatroomsChatroomIdChatPost } from '@/lib/api/generated/chat/chat'
import type { RecommendedJob } from '@/lib/api/generated/model'

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

// 123번 채팅방 전용 더미 메시지 데이터
const dummyMessages: Message[] = [
  {
    id: 1,
    sender: 'user' as const,
    content: '백엔드 개발자가 되기 위해 필요한 역량은 무엇인가요?',
    timestamp: '2024-01-15 14:30',
  },
  {
    id: 2,
    sender: 'assistant' as const,
    content: '',
    apiResponse: {
      user_message: '백엔드 개발자가 되기 위해 필요한 역량은 무엇인가요?',
      llm_response: `백엔드 개발자가 되기 위해 필요한 주요 역량들을 말씀드리겠습니다:

**기술적 역량:**
1. **프로그래밍 언어**: Java, Python, Node.js, Go 등
2. **데이터베이스**: MySQL, PostgreSQL, MongoDB 등
3. **프레임워크**: Spring, Django, Express.js 등
4. **클라우드**: AWS, GCP, Azure 등

**소프트 스킬:**
- 문제 해결 능력
- 논리적 사고
- 커뮤니케이션 능력

이러한 역량들을 차근차근 쌓아가시면 좋은 백엔드 개발자가 되실 수 있을 것입니다.`,
      recommended_jobs: [], // 일반 상담이므로 빈 배열
      created_at: '2024-01-15T14:31:00.000Z',
    },
    timestamp: '2024-01-15 14:31',
  },
  {
    id: 3,
    sender: 'user' as const,
    content: '내가 지원할만한 채용공고를 보여줄래?',
    timestamp: '2024-01-15 14:35',
  },
  {
    id: 4,
    sender: 'assistant' as const,
    content: '',
    apiResponse: {
      user_message: '내가 지원할만한 채용공고를 보여줄래?',
      llm_response:
        '개발 분야에서의 성장과 전문성을 더욱 키우기 위해 관련 경험과 프로젝트를 쌓는 것이 중요합니다.\n\n실무 팁:\n이력서 및 포트폴리오를 잘 준비하여 지원할 때 실력을 어필하세요. 개발 관련 프로젝트를 진행해보는 것도 좋습니다.\n\n아래 추천 채용공고들을 확인해보세요!',
      recommended_jobs: [
        {
          rec_idx: '50055856',
          title: '[에듀윌] 자격증 수험서 기획/편집 신입(경력)직 모집',
          url: 'https://www.saramin.co.kr/zf_user/jobs/relay/view?view_type=public-recruit&rec_idx=50055856',
          deadline: '',
          start_date: '2025.04.07 00:00',
          crawling_time: '2025-04-17 15:14:41',
          recommendation_reason:
            '개발 관련 채용공고가 포함되어 있으며, 다양한 기업에서 개발자로서의 기회를 제공하고 있습니다.',
        },
        {
          rec_idx: '50296051',
          title: '선광티앤에스 기술연구소 연구직 채용(대전 근무)',
          url: 'https://www.saramin.co.kr/zf_user/jobs/relay/view?view_type=public-recruit&rec_idx=50296051',
          deadline: '2025.04.19 23:59',
          start_date: '2025.03.20 18:00',
          crawling_time: '2025-04-17 12:39:27',
          recommendation_reason:
            '신입과 경력을 모두 고려한 포지션이 있어, 현재의 능력에 맞는 적합한 직무를 찾을 수 있습니다.',
        },
        {
          rec_idx: '50331739',
          title: '(주)퓨리텍 그래핀사업부 연구원(정규직) 채용',
          url: 'https://www.saramin.co.kr/zf_user/jobs/relay/view?view_type=public-recruit&rec_idx=50331739',
          deadline: '',
          start_date: '2025.03.25 17:00',
          crawling_time: '2025-04-17 11:50:14',
          recommendation_reason:
            '정규직 전환 가능성이 있는 포지션으로 안정적인 경력 쌓기가 가능합니다.',
        },
      ],
      created_at: '2025-06-07T17:08:30.217613',
    },
    timestamp: '2024-01-15 14:36',
  },
  {
    id: 5,
    sender: 'user' as const,
    content: '면접에서 긴장하지 않는 방법이 있을까요?',
    timestamp: '2024-01-15 14:40',
  },
  {
    id: 6,
    sender: 'assistant' as const,
    content: '',
    apiResponse: {
      user_message: '면접에서 긴장하지 않는 방법이 있을까요?',
      llm_response: `면접에서 긴장을 줄이는 효과적인 방법들을 알려드리겠습니다:

**사전 준비:**
1. **충분한 연습**: 예상 질문에 대한 답변을 미리 준비하고 연습하세요
2. **회사 정보 숙지**: 지원하는 회사와 직무에 대해 충분히 조사하세요
3. **모의 면접**: 친구나 가족과 모의 면접을 해보세요

**당일 대처법:**
- 면접 30분 전에 도착해서 마음을 진정시키세요
- 깊게 숨을 들이쉬고 천천히 내쉬는 호흡법을 활용하세요
- 긍정적인 마인드셋을 유지하고, 대화한다는 생각으로 임하세요

**심리적 준비:**
- 완벽하지 않아도 괜찮다는 마음가짐
- 면접관도 사람이라는 점을 기억하세요
- 실패하더라도 경험이 된다는 생각으로 부담을 덜어내세요

충분한 준비와 긍정적인 마인드가 가장 중요합니다!`,
      recommended_jobs: [], // 일반 상담이므로 빈 배열
      created_at: '2024-01-15T14:41:00.000Z',
    },
    timestamp: '2024-01-15 14:41',
  },
]

export default function ChatroomPage() {
  const params = useParams()
  const chatroomId = params.chatroomId as string
  const chatroomIdNumber = parseInt(chatroomId)

  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [error, setError] = useState<string | null>(null)

  // 채팅방 상세 조회 (orval 생성 훅 사용)
  const {
    data: chatroomData,
    isLoading: isLoadingChatroom,
    error: chatroomError,
    refetch: refetchChatroom,
  } = useGetChatroomDetailChatroomsChatroomIdGet(chatroomIdNumber, {
    query: {
      enabled: chatroomId !== '123', // 123번은 더미데이터 사용
    },
  })

  // 메시지 전송 (orval 생성 훅 사용)
  const chatMutation = useChatWithLlmChatroomsChatroomIdChatPost({
    mutation: {
      onSuccess: (response) => {
        const aiMessage: Message = {
          id: Date.now() + 1,
          sender: 'assistant',
          content: '',
          apiResponse: {
            user_message: response.user_message,
            llm_response: response.llm_response,
            recommended_jobs: response.recommended_jobs || [],
            created_at: response.created_at,
          },
          timestamp: new Date().toLocaleString(),
        }
        setMessages((prev) => [...prev, aiMessage])
        setError(null)
      },
      onError: (error) => {
        console.error('메시지 전송 실패:', error)
        setError('메시지 전송에 실패했습니다. 다시 시도해주세요.')
      },
    },
  })

  // 채팅방 데이터 로딩
  useEffect(() => {
    if (chatroomId === '123') {
      // 123번 채팅방: 더미 데이터 사용
      setMessages(dummyMessages)
    } else if (chatroomData && chatroomData.messages) {
      // 실제 채팅방: API 데이터 변환
      const convertedMessages: Message[] = []

      for (let i = 0; i < chatroomData.messages.length; i++) {
        const message = chatroomData.messages[i]

        if (message.sender === 'user') {
          convertedMessages.push({
            id: message.id,
            sender: 'user',
            content: message.content || '',
            timestamp: new Date(message.created_at).toLocaleString(),
          })
        } else if (message.sender === 'llm') {
          // LLM 메시지인 경우 이전 사용자 메시지 찾기
          const prevUserMessage = chatroomData.messages
            .slice(0, i)
            .reverse()
            .find((m) => m.sender === 'user')

          convertedMessages.push({
            id: message.id,
            sender: 'assistant',
            content: '',
            apiResponse: {
              user_message: prevUserMessage?.content || '',
              llm_response: message.content || '',
              recommended_jobs: [], // 추후 추가 필요
              created_at: message.created_at,
            },
            timestamp: new Date(message.created_at).toLocaleString(),
          })
        }
      }

      setMessages(convertedMessages)
    }
  }, [chatroomId, chatroomData])

  // 에러 처리
  useEffect(() => {
    if (chatroomError) {
      setError('채팅방을 불러오는데 실패했습니다.')
    }
  }, [chatroomError])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputMessage.trim() || chatMutation.isPending) return

    // 사용자 메시지 즉시 추가
    const userMessage: Message = {
      id: Date.now(),
      sender: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleString(),
    }

    setMessages((prev) => [...prev, userMessage])
    const currentInput = inputMessage
    setInputMessage('')
    setError(null)

    if (chatroomId === '123') {
      // 123번 채팅방: 더미 응답
      setTimeout(() => {
        const aiMessage: Message = {
          id: Date.now() + 1,
          sender: 'assistant',
          content: '',
          apiResponse: {
            user_message: currentInput,
            llm_response:
              '안녕하세요! 저는 123번 더미 채팅방의 AI입니다. 이곳은 데모용 채팅방이에요. 궁금한 것이 있으시면 언제든 물어보세요! 📚',
            recommended_jobs: [],
            created_at: new Date().toISOString(),
          },
          timestamp: new Date().toLocaleString(),
        }
        setMessages((prev) => [...prev, aiMessage])
      }, 2000)
    } else {
      // 실제 채팅방: API 호출
      chatMutation.mutate({
        chatroomId: chatroomIdNumber,
        data: { message: currentInput },
      })
    }
  }

  const chatroomTitle =
    chatroomId === '123'
      ? '데모 채팅방'
      : chatroomData?.title || `채팅방 #${chatroomId}`

  const isLoading = isLoadingChatroom || chatMutation.isPending

  return (
    <div className="flex flex-col h-full bg-white">
      {/* 헤더 (채팅방 정보 표시) */}
      <div className="border-b border-gray-200 p-4 bg-gray-50">
        <div className="text-sm text-gray-600">
          {chatroomId === '123' ? (
            <span className="inline-flex items-center">
              📚 데모 채팅방 (더미데이터)
            </span>
          ) : (
            <span className="inline-flex items-center">💬 {chatroomTitle}</span>
          )}
        </div>
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 mx-6 mt-4 rounded">
          {error}
        </div>
      )}

      {/* 메시지 영역 */}
      <MessageList messages={messages} isLoading={isLoading} />

      {/* 입력 영역 */}
      <div className="border-t border-gray-200 p-6 bg-white">
        <ChatInput
          message={inputMessage}
          setMessage={setInputMessage}
          onSubmit={handleSubmit}
          isLoading={isLoading}
        />
      </div>
    </div>
  )
}
