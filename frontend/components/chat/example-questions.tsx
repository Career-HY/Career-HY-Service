interface ExampleQuestionsProps {
  onQuestionClick: (question: string) => void
  isLoading: boolean
}

export default function ExampleQuestions({
  onQuestionClick,
  isLoading,
}: ExampleQuestionsProps) {
  const exampleQuestions = [
    '머신러닝 엔지니어링에 관심이 많은데 지금 지원할 수 있는 기업의 채용공고를 보여줄래?',
    '나는 신소재공학과 졸업생이야 내가 수강한 과목들을 바탕으로 내가 지원할 수 있는 기업의 채용공고를 보여줘',
    '백엔드 개발자가 되기 위해 필요한 역량은 무엇인가요?',
    '나는 융합전자공학을 전공했고 공기업 채용 공고를 찾고있어 몇 개 추천해줄래?',
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
      {exampleQuestions.map((question, index) => (
        <button
          key={index}
          onClick={() => onQuestionClick(question)}
          disabled={isLoading}
          className="p-4 text-left border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <div className="text-gray-700">{question}</div>
        </button>
      ))}
    </div>
  )
}
