import { ExternalLinkIcon, CalendarIcon } from 'lucide-react'

interface JobRecommendation {
  rec_idx: string
  title: string
  url: string
  deadline: string
  start_date: string
  crawling_time: string
  recommendation_reason: string
}

interface JobCardProps {
  job: JobRecommendation
}

export default function JobCard({ job }: JobCardProps) {
  const formatDeadline = (deadline: string) => {
    if (!deadline) return '상시채용'
    return deadline
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg hover:border-blue-200 transition-all duration-200">
      <div className="mb-4">
        <h4 className="text-lg font-semibold text-gray-900 leading-7 mb-3">
          {job.title}
        </h4>

        <div className="flex items-center text-sm text-gray-600">
          <CalendarIcon className="w-4 h-4 mr-2 text-blue-500" />
          <span className="font-medium">마감일:</span>
          <span className="ml-2">{formatDeadline(job.deadline)}</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex-1 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100 p-4 rounded-lg">
          <div className="flex items-start">
            <div className="text-blue-500 mr-2 mt-0.5">💡</div>
            <div>
              <p className="text-sm font-medium text-blue-900 mb-1">
                추천 이유
              </p>
              <p className="text-sm text-blue-800 leading-relaxed">
                {job.recommendation_reason}
              </p>
            </div>
          </div>
        </div>

        <div className="flex-shrink-0">
          <a
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white text-sm font-semibold rounded-lg hover:from-blue-700 hover:to-blue-800 transform hover:scale-105 transition-all duration-200 shadow-md hover:shadow-lg"
          >
            지원하기
            <ExternalLinkIcon className="w-4 h-4 ml-2" />
          </a>
        </div>
      </div>
    </div>
  )
}
