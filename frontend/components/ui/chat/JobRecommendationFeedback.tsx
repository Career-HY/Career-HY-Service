import React, { useState } from 'react'

interface JobRecommendationFeedbackProps {
  probability: number // 0~1 사이 확률 (ex: 0.5)
  onSubmit: (rating: number, reason: string) => void
  disabled?: boolean
}

const JobRecommendationFeedback: React.FC<JobRecommendationFeedbackProps> = ({
  probability,
  onSubmit,
  disabled = false,
}) => {
  // 확률에 따라 렌더링 결정 (최초 마운트 시)
  const [show] = useState(() => Math.random() < probability)
  const [rating, setRating] = useState<number>(0)
  const [reason, setReason] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  if (!show) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (rating < 1 || rating > 5) return
    setSubmitting(true)
    try {
      await onSubmit(rating, reason)
      setSubmitted(true)
    } finally {
      setSubmitting(false)
    }
  }

  if (submitted) {
    return (
      <div className="mt-4 p-4 bg-blue-50 rounded text-blue-700 text-center">
        소중한 평가 감사합니다!
      </div>
    )
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mt-4 p-4 bg-gray-50 rounded shadow"
    >
      <div className="mb-2 font-semibold">
        이 채용공고 추천은 얼마나 만족스러웠나요?
      </div>
      <div className="flex items-center mb-2">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            type="button"
            key={star}
            className={`text-2xl mx-1 ${rating >= star ? 'text-yellow-400' : 'text-gray-300'}`}
            onClick={() => setRating(star)}
            disabled={disabled || submitting}
            aria-label={`${star}점`}
          >
            ★
          </button>
        ))}
      </div>
      <textarea
        className="w-full border rounded p-2 mb-2"
        placeholder="별점을 준 이유를 적어주세요 (선택)"
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        rows={2}
        disabled={disabled || submitting}
      />
      <button
        type="submit"
        className="w-full bg-blue-600 text-white py-2 rounded disabled:opacity-50"
        disabled={disabled || submitting || rating === 0}
      >
        {submitting ? '제출 중...' : '평가 제출'}
      </button>
    </form>
  )
}

export default JobRecommendationFeedback
