import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// 인증이 필요하지 않은 public 경로들
const publicPaths = ['/', '/signup']

// 정적 파일 경로
const staticPaths = ['/_next/', '/images/']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  console.log('🚀 미들웨어 실행 - 현재 경로:', pathname)
  console.log('📝 전체 쿠키 목록:', request.cookies.getAll())

  // 정적 파일 요청은 통과
  if (staticPaths.some((path) => pathname.startsWith(path))) {
    console.log('✅ 정적 파일 요청 - 통과')
    return NextResponse.next()
  }

  // public 경로는 세션 체크 없이 통과
  if (publicPaths.includes(pathname)) {
    console.log('✅ public 경로 - 통과')
    return NextResponse.next()
  }

  // 세션 토큰 확인 (값이 존재하고 비어있지 않은지 확인)
  const sessionCookie = request.cookies.get('session')
  console.log('🔑 세션 쿠키:', sessionCookie)
  if (sessionCookie) {
    console.log('📦 세션 쿠키 상세 정보:', {
      name: sessionCookie.name,
      value: sessionCookie.value,
    })
  }

  const hasValidSession =
    sessionCookie && sessionCookie.value && sessionCookie.value.length > 0

  // 유효한 세션이 없으면 홈(로그인 페이지)으로 리다이렉트
  if (!hasValidSession) {
    console.log('❌ 유효하지 않은 세션 - 홈으로 리다이렉트')
    const homeUrl = new URL('/', request.url)
    return NextResponse.redirect(homeUrl)
  }

  console.log('✅ 유효한 세션 확인 - 통과')
  return NextResponse.next()
}

// 미들웨어가 실행될 경로 설정
export const config = {
  matcher: [
    /*
     * Match all page routes except:
     * 1. _next/static (static files)
     * 2. _next/image (image optimization files)
     * 3. favicon.ico (favicon file)
     * 4. API routes
     */
    '/((?!_next/static|_next/image|favicon.ico|api).*)',
  ],
}
