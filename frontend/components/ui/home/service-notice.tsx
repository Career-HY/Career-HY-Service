export default function ServiceNotice() {
  return (
    <div className="mt-8 max-w-6xl mx-auto w-full">
      <div className="bg-white/80 backdrop-blur-sm p-8 rounded-lg border border-gray-200">
        <div className="grid grid-cols-3 gap-12">
          {/* 서비스 이용 안내 */}
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-gray-900">
              로그인 정보 처리 안내
            </h3>
            <ul className="text-xs text-gray-600 space-y-1">
              <li>• 현재는 로그인한 사용자만 이용 가능합니다.</li>
              <li>
                • 이메일 인증 절차가 없어 실제 이메일이 아니어도 가입
                가능합니다.
              </li>
              <li>• 이메일 정보는 어떠한 목적으로도 사용되지 않습니다.</li>
              <li className="text-blue-600">
                • 추후 비로그인 사용자도 이용 가능하도록 확장 예정입니다.
              </li>
            </ul>
          </div>

          {/* 데이터 범위 안내 */}
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-gray-900">
              수강편람 데이터 범위 안내
            </h3>
            <ul className="text-xs text-gray-600 space-y-1">
              <li>• 현재 2025년도 1학기 수강편람 데이터만 제공됩니다.</li>
              <li>
                • 2025년도 1학기 기준 폐강 과목은 프로필에 등록할 수 없습니다.
              </li>
              <li>
                • 프로필에 등록된 수강 이력 데이터는 채용공고 추천에 사용됩니다.
              </li>
              <li className="text-blue-600">
                • 추후 과거 수강편람 데이터까지 모두 확보 예정입니다.
              </li>
            </ul>
          </div>

          {/* 세 번째 섹션 */}
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-gray-900">
              서비스 이용 대상 안내
            </h3>
            <ul className="text-xs text-gray-600 space-y-1">
              <li>• 한양대학교 학생이 아니어도 이용 가능합니다.</li>
              <li>
                • 한양대학교 학생이 아니실 경우 프로필 페이지에서 본인 대학에서
                수강한 과목과 유사한 수강 편람 데이터를 등록해주세요.
              </li>
              <li className="text-blue-600">• 많은 이용 부탁드립니다.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
