import ReactMarkdown from 'react-markdown'
import JobRecommendations from './job-recommendations'

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

interface ChatMessageProps {
  content: string
  apiResponse?: ApiResponse
  timestamp: string
}

export default function ChatMessage({
  content,
  apiResponse,
  timestamp,
}: ChatMessageProps) {
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
                {apiResponse.llm_response}
              </ReactMarkdown>
            </div>

            {/* 추천 채용공고 */}
            <JobRecommendations jobs={apiResponse.recommended_jobs} />
          </>
        ) : (
          <div className="whitespace-pre-wrap">{content}</div>
        )}

        <div className="text-xs mt-3 text-gray-500">{timestamp}</div>
      </div>
    </div>
  )
}
