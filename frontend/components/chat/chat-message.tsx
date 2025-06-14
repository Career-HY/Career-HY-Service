import ReactMarkdown from 'react-markdown'
import JobRecommendations from './job-recommendations'
import type { RecommendedJob } from '@/lib/api/generated/model'
import JobRecommendationFeedback from '../ui/JobRecommendationFeedback'
import { useSubmitJobRecommendationFeedbackFeedbackJobRecommendationPost } from '@/lib/api/generated/feedback/feedback'

interface ApiResponse {
  id?: number
  user_message: string
  llm_response: string
  recommended_jobs: RecommendedJob[]
  created_at: string
}

interface ChatMessageProps {
  content: string
  apiResponse?: ApiResponse
  timestamp: string
}

// LLM 응답의 과도한 공백 정리 함수
const cleanLLMResponse = (text: string): string => {
  return (
    text
      // 먼저 전체 텍스트 앞뒤 공백 제거
      .trim()
      // 탭을 공백으로 변환
      .replace(/\t/g, ' ')
      // 줄바꿈 앞뒤의 공백 제거
      .replace(/[ \t]*\n[ \t]*/g, '\n')
      // 줄바꿈 후 많은 공백 제거 (2개 이상의 연속 공백을 1개로)
      .replace(/\n\s{2,}/g, '\n')
      // 일반적인 연속 공백을 1개로 압축 (2개 이상)
      .replace(/[ ]{2,}/g, ' ')
      // 연속된 줄바꿈을 최대 2개로 제한
      .replace(/\n{3,}/g, '\n\n')
  )
}

export default function ChatMessage({
  content,
  apiResponse,
  timestamp,
}: ChatMessageProps) {
  // 별점 평가 UI 노출 확률 (상위에서 props로 받을 수도 있음)
  const FEEDBACK_PROBABILITY = 1.0 // 테스트를 위해 1.0으로 고정

  // orval mutation 훅
  const feedbackMutation =
    useSubmitJobRecommendationFeedbackFeedbackJobRecommendationPost()

  // chat_history_id는 실제 DB id 사용
  const chatHistoryId = apiResponse?.id

  return (
    <div className="w-full">
      <div className="p-6 text-gray-900">
        {/* AI 응답 텍스트 */}
        {apiResponse ? (
          <>
            <div className="prose prose-gray max-w-none mb-6">
              <ReactMarkdown
                components={{
                  h1: ({ children }) => (
                    <h1 className="text-2xl font-bold mb-4">{children}</h1>
                  ),
                  h2: ({ children }) => (
                    <h2 className="text-xl font-semibold mb-3">{children}</h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-lg font-medium mb-2">{children}</h3>
                  ),
                  p: ({ children }) => (
                    <p className="mb-3 leading-relaxed">{children}</p>
                  ),
                  strong: ({ children }) => (
                    <strong className="font-semibold text-gray-900">
                      {children}
                    </strong>
                  ),
                  ul: ({ children }) => (
                    <ul className="list-disc list-inside mb-3 space-y-1">
                      {children}
                    </ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="list-decimal list-inside mb-3 space-y-1">
                      {children}
                    </ol>
                  ),
                  li: ({ children }) => (
                    <li className="leading-relaxed">{children}</li>
                  ),
                }}
              >
                {cleanLLMResponse(apiResponse.llm_response)}
              </ReactMarkdown>
            </div>

            {/* 추천 채용공고 */}
            {apiResponse.recommended_jobs &&
              apiResponse.recommended_jobs.length > 0 && (
                <>
                  <JobRecommendations jobs={apiResponse.recommended_jobs} />
                  {/* 별점 평가 UI: chatHistoryId가 있으면 노출 */}
                  {typeof chatHistoryId === 'number' && (
                    <JobRecommendationFeedback
                      chatHistoryId={chatHistoryId}
                      probability={FEEDBACK_PROBABILITY}
                      onSubmit={async (rating, reason) => {
                        return new Promise<void>((resolve, reject) => {
                          feedbackMutation.mutate(
                            {
                              data: {
                                chat_history_id: chatHistoryId,
                                rating,
                                reason,
                              },
                            },
                            {
                              onSuccess: () => resolve(),
                              onError: (err) => reject(err),
                            }
                          )
                        })
                      }}
                      disabled={feedbackMutation.isPending}
                    />
                  )}
                </>
              )}
          </>
        ) : (
          <div className="whitespace-pre-wrap">{content}</div>
        )}

        <div className="text-xs mt-3 text-gray-500">{timestamp}</div>
      </div>
    </div>
  )
}
