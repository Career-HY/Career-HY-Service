import ky from 'ky'

// API 기본 URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL

// ky 인스턴스 생성
export const api = ky.create({
  prefixUrl: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include', // 세션 쿠키 포함
  timeout: 120000, // 120초
  retry: {
    limit: 2,
    methods: ['get', 'post', 'put', 'delete', 'patch'],
  },
  hooks: {
    beforeError: [
      (error) => {
        const { response } = error
        if (response && response.body) {
          error.name = 'APIError'
          error.message = `${response.status} ${response.statusText}`
        }
        return error
      },
    ],
    beforeRequest: [
      (request) => {
        // CORS 관련 헤더 추가
        request.headers.set('Origin', window.location.origin)
      },
    ],
  },
})

// orval에서 사용할 커스텀 인스턴스
export const customInstance = <T>(config: {
  url: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  data?: unknown
  params?: Record<string, string | number | boolean>
  headers?: Record<string, string>
  signal?: AbortSignal
}): Promise<T> => {
  const { url, method, data, params, headers, signal } = config

  // URL에서 시작하는 슬래시 제거 (prefixUrl 사용 시 필요)
  const cleanUrl = url.startsWith('/') ? url.slice(1) : url

  return api(cleanUrl, {
    method: method.toLowerCase() as 'get' | 'post' | 'put' | 'delete' | 'patch',
    json: data,
    searchParams: params,
    headers,
    signal,
    credentials: 'include',
  }).json()
}

export default customInstance
