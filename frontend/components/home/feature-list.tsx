interface FeatureItemProps {
  title: string
  description: string
}

function FeatureItem({ title, description }: FeatureItemProps) {
  return (
    <div className="flex items-start space-x-3">
      <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
        <span className="text-blue-600 text-sm">✓</span>
      </div>
      <div>
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <p className="text-gray-600 text-sm">{description}</p>
      </div>
    </div>
  )
}

export default function FeatureList() {
  const features = [
    {
      title: '개인 맞춤형 채용 공고 정보 제공',
      description: '전공과 수강이력, 관심사에 맞는 채용공고를 추천받으세요.',
    },
    {
      title: '커리어 상담',
      description: '챗봇과의 커리어 상담을 통해 취업 전략을 수립하세요.',
    },
    {
      title: '채용공고 스크랩',
      description: 'AI에게 추천받은 채용공고를 스크랩하고 관리할 수 있습니다.',
    },
  ]

  return (
    <div className="space-y-3 mb-2">
      {features.map((feature, index) => (
        <FeatureItem
          key={index}
          title={feature.title}
          description={feature.description}
        />
      ))}
    </div>
  )
}
