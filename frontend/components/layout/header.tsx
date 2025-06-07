export default function Header() {
  return (
    <div className="pt-8 pb-6">
      <div className="text-center">
        <div className="inline-flex items-center space-x-3 mb-4">
          {/* 한양대 로고 영역 */}
          <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-800 rounded-full flex items-center justify-center">
            <span className="text-white font-bold text-lg">한</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900">Career-HY</h1>
        </div>
      </div>
    </div>
  )
}
