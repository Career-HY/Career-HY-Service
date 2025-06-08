interface PendingMessage {
  chatroomId: number
  message: string
}

// 전역 상태로 초기 메시지 관리
export let pendingMessage: PendingMessage | null = null

// 초기 메시지 설정
export const setPendingMessage = (chatroomId: number, message: string) => {
  pendingMessage = { chatroomId, message }
}

// 초기 메시지 초기화
export const clearPendingMessage = () => {
  pendingMessage = null
}
