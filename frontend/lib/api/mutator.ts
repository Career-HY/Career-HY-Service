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
  },
})

// orval에서 사용할 커스텀 인스턴스
export const customInstance = <T>(config: {
  url: string
  method: 'get' | 'post' | 'put' | 'delete' | 'patch'
  data?: any
  params?: any
}): Promise<T> => {
  const { url, method, data, params } = config

  return api(url, {
    method,
    json: data,
    searchParams: params,
  }).json()
}

export default customInstance
