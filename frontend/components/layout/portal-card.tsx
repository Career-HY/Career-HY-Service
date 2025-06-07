import Image from 'next/image'

export default function PortalCard() {
  return (
    <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl p-5 border border-blue-200">
      <div className="text-center">
        <div className="flex items-center justify-center space-x-3 mb-3">
          <div className="w-12 h-12 flex items-center justify-center">
            <Image
              src="/images/logos/HYU-logo.png"
              alt="한양대학교"
              width={48}
              height={48}
              className="object-contain rounded-full"
            />
          </div>
          <h3 className="text-lg font-bold text-blue-900">
            한양대학교 재학생/졸업생
          </h3>
        </div>
        <p className="text-blue-800 text-xs mb-3 leading-relaxed">
          학과 정보와 수강이력 데이터를 기반으로 채용 공고를 추천합니다.
          <br />
          한양대학교 포털 사이트에서 관련 정보를 확인하실수 있습니다.
        </p>
        <a
          href="https://portal.hanyang.ac.kr/sso/lgin.do"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center px-5 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
        >
          <span className="mr-2">🏫</span>
          한양대학교 포털 바로가기
        </a>
      </div>
    </div>
  )
}
