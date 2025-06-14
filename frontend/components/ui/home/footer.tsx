export default function Footer() {
  return (
    <footer className="py-4 bg-gray-50 border-t border-gray-200">
      <div className="container mx-auto px-4 text-center">
        <p className="text-gray-600 text-xs">
          © 2025 Career-HY. 한양대학교 취업지원 플랫폼
        </p>
        <div className="mt-1 space-x-4 text-xs text-gray-500">
          <a href="#" className="hover:text-gray-700 transition-colors">
            이용약관
          </a>
          <a href="#" className="hover:text-gray-700 transition-colors">
            개인정보처리방침
          </a>
          <a href="#" className="hover:text-gray-700 transition-colors">
            문의하기
          </a>
        </div>
      </div>
    </footer>
  )
}
