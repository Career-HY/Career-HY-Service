import SignupForm from '@/components/ui/home/signup-form'
import Header from '@/components/ui/home/header'
import HeroSection from '@/components/ui/home/hero-section'
import FeatureList from '@/components/ui/home/feature-list'
import PortalCard from '@/components/ui/home/portal-card'
import ServiceNotice from '@/components/ui/home/service-notice'
import Footer from '@/components/ui/home/footer'

export default function SignupPage() {
  return (
    <div className="h-screen bg-gradient-to-br from-blue-50 via-white to-blue-50 flex flex-col">
      <Header />

      {/* 메인 컨텐츠 */}
      <div className="flex-1 container mx-auto px-4 py-4 flex flex-col">
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

          {/* 우측 회원가입 폼 */}
          <div className="flex-1 max-w-md w-full">
            <SignupForm />
          </div>
        </div>

        {/* 안내 문구 섹션 */}
        <ServiceNotice />
      </div>

      <Footer />
    </div>
  )
}
