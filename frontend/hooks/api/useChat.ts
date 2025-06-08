import { useChatWithLlmChatroomsChatroomIdChatPost } from '@/lib/api/generated/chat/chat'
import type { ChatRequest } from '@/lib/api/generated/model'

// 메시지 전송
export function useSendMessage(chatroomId: number) {
  return useChatWithLlmChatroomsChatroomIdChatPost({
    mutation: {
      onError: (error) => {
        console.error('메시지 전송 실패:', error)
      },
    },
  })
}

// 편의 함수
export function useChatActions(chatroomId: number) {
  const sendMessageMutation = useSendMessage(chatroomId)

  const sendMessage = async (message: string) => {
    try {
      const response = await sendMessageMutation.mutateAsync({
        chatroomId,
        data: { message },
      })
      return response
    } finally {
      // mutation 상태 초기화
      sendMessageMutation.reset()
    }
  }

  return {
    sendMessage,
    isSending: sendMessageMutation.isPending,
    sendMessageMutation,
  }
}
