import ky from 'ky'

// API 베이스 인스턴스 생성
export const api = ky.create({
  prefixUrl: process.env.NEXT_PUBLIC_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  retry: {
    limit: 2,
    methods: ['get'],
  },
  timeout: 10000,
  hooks: {
    beforeRequest: [
      (request) => {
        // 인증 토큰이 있다면 헤더에 추가
        const token = localStorage.getItem('authToken')
        if (token) {
          request.headers.set('Authorization', `Bearer ${token}`)
        }
      },
    ],
    afterResponse: [
      async (request, options, response) => {
        // 401 에러 시 토큰 제거 및 리다이렉트
        if (response.status === 401) {
          localStorage.removeItem('authToken')
          window.location.href = '/login'
        }
        return response
      },
    ],
  },
})

// orval에서 사용할 custom instance
export const customInstance = <T>(config: {
  url: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  params?: Record<string, string | number | boolean>
  data?: unknown
  headers?: Record<string, string>
  signal?: AbortSignal
}): Promise<T> => {
  const { url, method, params, data, headers, signal } = config

  return api(url, {
    method: method.toLowerCase() as 'get' | 'post' | 'put' | 'delete' | 'patch',
    searchParams: params,
    json: data,
    headers,
    signal,
  }).json<T>()
}

export default customInstance
