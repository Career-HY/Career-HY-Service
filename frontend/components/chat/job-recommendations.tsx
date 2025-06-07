import JobCard from './job-card'

interface JobRecommendation {
  rec_idx: string
  title: string
  url: string
  deadline: string
  start_date: string
  crawling_time: string
  recommendation_reason: string
}

interface JobRecommendationsProps {
  jobs: JobRecommendation[]
}

export default function JobRecommendations({ jobs }: JobRecommendationsProps) {
  if (!jobs || jobs.length === 0) {
    return null
  }

  return (
    <div className="space-y-4">
      <h3 className="text-xl font-bold text-gray-800 border-b border-gray-200 pb-3 mb-6">
        💼 추천 채용공고
      </h3>
      <div className="grid gap-6">
        {jobs.map((job) => (
          <JobCard key={job.rec_idx} job={job} />
        ))}
      </div>
    </div>
  )
}
