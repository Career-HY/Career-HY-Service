export default function Header() {
  return (
    <div className="pt-8 pb-6">
      <div className="text-center">
        <div className="inline-flex items-center space-x-3 mb-4">
          {/* Career-HY 로고 영역 */}
          {/* 여기서는 일단 로고 사용 안함 (svg가 아니라 흰 배경이 아닐때 로고 사용하면 어색함) */}
          {/* <div className="w-12 h-12 flex items-center justify-center">
            <Image
              src="/images/logos/careerhy.png"
              alt="Career-HY"
              width={48}
              height={48}
              className="object-contain"
            />
          </div> */}
          <h1 className="text-3xl font-bold text-gray-900">Career-HY</h1>
        </div>
      </div>
    </div>
  )
}
