import JobCard from './job-card'
import type { RecommendedJob } from '@/lib/api/generated/model'

interface JobRecommendationsProps {
  jobs: RecommendedJob[]
}

export default function JobRecommendations({ jobs }: JobRecommendationsProps) {
  if (!jobs || jobs.length === 0) {
    return null
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-3">
        🎯 추천 채용공고
      </h3>
      <div className="grid gap-3">
        {jobs.map((job, index) => (
          <JobCard key={job.rec_idx || `job-${index}`} job={job} />
        ))}
      </div>
    </div>
  )
}
