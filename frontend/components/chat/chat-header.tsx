import { SparklesIcon } from 'lucide-react'

export default function ChatHeader() {
  return (
    <div className="text-center mb-12">
      <div className="w-12 h-12 mx-auto mb-4 bg-blue-100 rounded-full flex items-center justify-center">
        <SparklesIcon className="w-6 h-6 text-blue-600" />
      </div>
      <h1 className="text-3xl font-bold text-gray-900 mb-2">
        Career-HY와 대화해보세요
      </h1>
      <p className="text-lg text-gray-600">
        진로 상담, 채용 공고 추천, 취업 준비 등 궁금한 것을 물어보세요
      </p>
    </div>
  )
}
