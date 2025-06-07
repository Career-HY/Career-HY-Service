import LoginForm from '@/components/ui/login-form'
import Header from '@/components/layout/header'
import HeroSection from '@/components/layout/hero-section'
import FeatureList from '@/components/layout/feature-list'
import PortalCard from '@/components/layout/portal-card'
import Footer from '@/components/layout/footer'

export default function Home() {
  return (
    <div className="h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex flex-col">
      <Header />

      {/* 메인 컨텐츠 */}
      <div className="flex-1 container mx-auto px-4 py-4">
        <div className="flex flex-col lg:flex-row items-start justify-center gap-8 h-full">
          {/* 좌측 정보 섹션 */}
          <div className="flex-1 max-w-lg">
            <div className="space-y-6">
              <HeroSection />
              <FeatureList />
              <PortalCard />
            </div>
          </div>

          {/* 우측 로그인 폼 */}
          <div className="flex-1 max-w-md w-full">
            <LoginForm />
          </div>
        </div>
      </div>

      <Footer />
    </div>
  )
}
