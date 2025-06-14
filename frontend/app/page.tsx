import LoginForm from '@/components/ui/home/login-form'
import Header from '@/components/ui/home/header'
import HeroSection from '@/components/ui/home/hero-section'
import FeatureList from '@/components/ui/chat/feature-list'
import PortalCard from '@/components/ui/home/portal-card'
import ServiceNotice from '@/components/ui/home/service-notice'
import Footer from '@/components/ui/home/footer'

export default function Home() {
  return (
    <div className="h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex flex-col">
      <Header />

      {/* 메인 컨텐츠 */}
      <div className="flex-1 container mx-auto px-4 py-4 flex flex-col">
        {/* 상단 섹션: 정보 + 로그인 */}
        <div className="flex flex-col lg:flex-row items-start justify-center gap-8">
          {/* 좌측 정보 섹션 */}
          <div className="flex-1 max-w-lg">
            <div className="space-y-6">
              <HeroSection />
              <FeatureList />
              <div className="pt-4">
                <PortalCard />
              </div>
            </div>
          </div>

          {/* 우측 섹션 */}
          <div className="flex-1 max-w-md w-full">
            <LoginForm />
          </div>
        </div>

        {/* 안내 문구 섹션 */}
        <ServiceNotice />
      </div>

      <Footer />
    </div>
  )
}
