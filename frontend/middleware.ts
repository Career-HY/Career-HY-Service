import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// 인증이 필요하지 않은 public 경로들
const publicPaths = ['/', '/signup']

// API 요청 경로
const apiPaths = ['/api/']

// 정적 파일 경로
const staticPaths = ['/_next/', '/images/']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // API 요청이나 정적 파일 요청은 통과
  if (
    apiPaths.some((path) => pathname.startsWith(path)) ||
    staticPaths.some((path) => pathname.startsWith(path))
  ) {
    return NextResponse.next()
  }

  // 세션 토큰 확인
  const token = request.cookies.get('session')

  // 이미 로그인된 상태에서 홈페이지(로그인 페이지)나 회원가입 페이지 접근 시 채팅 페이지로 리다이렉트
  //   if (token && publicPaths.includes(pathname)) {
  //     const chatUrl = new URL('/chat', request.url)
  //     return NextResponse.redirect(chatUrl)
  //   }

  // public 경로는 세션 체크 없이 통과
  if (publicPaths.includes(pathname)) {
    return NextResponse.next()
  }

  // 인증이 필요한 페이지에서 토큰이 없으면 홈(로그인 페이지)으로 리다이렉트
  if (!token) {
    const homeUrl = new URL('/', request.url)
    return NextResponse.redirect(homeUrl)
  }

  return NextResponse.next()
}

// 미들웨어가 실행될 경로 설정
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * 1. _next/static (static files)
     * 2. _next/image (image optimization files)
     * 3. favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
}
