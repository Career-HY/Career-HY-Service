'use client'

import { useState } from 'react'
import { useParams } from 'next/navigation'
import { ChatInput, MessageList } from '@/components/chat'

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

// 더미 메시지 데이터
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

  const [messages, setMessages] = useState<Message[]>(dummyMessages)
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputMessage.trim() || isLoading) return

    // 사용자 메시지 추가
    const userMessage: Message = {
      id: messages.length + 1,
      sender: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleString(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    // 임시: 2초 후 AI 응답 (나중에 실제 API로 대체)
    setTimeout(() => {
      const aiMessage: Message = {
        id: messages.length + 2,
        sender: 'assistant',
        content: '',
        apiResponse: {
          user_message: inputMessage,
          llm_response:
            '이것은 임시 AI 응답입니다. 나중에 실제 API로 연결할 예정입니다.',
          recommended_jobs: [],
          created_at: new Date().toISOString(),
        },
        timestamp: new Date().toLocaleString(),
      }
      setMessages((prev) => [...prev, aiMessage])
      setIsLoading(false)
    }, 2000)
  }

  return (
    <div className="flex flex-col h-full bg-white">
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
