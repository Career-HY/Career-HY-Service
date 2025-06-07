import { useQueryClient } from '@tanstack/react-query'
import {
  useGetMyChatroomsChatroomsGet,
  useGetChatroomDetailChatroomsChatroomIdGet,
  useCreateNewChatroomChatroomsPost,
  useUpdateChatroomInfoChatroomsChatroomIdPatch,
  useDeleteChatroomByIdChatroomsChatroomIdDelete,
} from '@/lib/api/generated/chatrooms/chatrooms'
import type { ChatroomCreate, ChatroomUpdate } from '@/lib/api/generated/model'

// 채팅방 목록 조회
export function useChatroomList() {
  return useGetMyChatroomsChatroomsGet()
}

// 채팅방 상세 조회 (메시지 포함)
export function useChatroomDetail(chatroomId: number, enabled = true) {
  return useGetChatroomDetailChatroomsChatroomIdGet(chatroomId, {
    query: {
      enabled,
    },
  })
}

// 새 채팅방 생성
export function useCreateChatroom() {
  const queryClient = useQueryClient()

  return useCreateNewChatroomChatroomsPost({
    mutation: {
      onSuccess: () => {
        // 채팅방 목록 새로고침
        queryClient.invalidateQueries({
          queryKey: ['/chatrooms'],
        })
      },
      onError: (error) => {
        console.error('채팅방 생성 실패:', error)
      },
    },
  })
}

// 채팅방 정보 수정
export function useUpdateChatroom() {
  const queryClient = useQueryClient()

  return useUpdateChatroomInfoChatroomsChatroomIdPatch({
    mutation: {
      onSuccess: () => {
        // 채팅방 목록 새로고침
        queryClient.invalidateQueries({
          queryKey: ['/chatrooms'],
        })
      },
      onError: (error) => {
        console.error('채팅방 수정 실패:', error)
      },
    },
  })
}

// 채팅방 삭제
export function useDeleteChatroom() {
  const queryClient = useQueryClient()

  return useDeleteChatroomByIdChatroomsChatroomIdDelete({
    mutation: {
      onSuccess: () => {
        // 채팅방 목록 새로고침
        queryClient.invalidateQueries({
          queryKey: ['/chatrooms'],
        })
      },
      onError: (error) => {
        console.error('채팅방 삭제 실패:', error)
      },
    },
  })
}

// 편의 함수들
export function useChatroomActions() {
  const createMutation = useCreateChatroom()
  const updateMutation = useUpdateChatroom()
  const deleteMutation = useDeleteChatroom()

  const createChatroom = (data: ChatroomCreate) => {
    return createMutation.mutate({ data })
  }

  const updateChatroom = (chatroomId: number, data: ChatroomUpdate) => {
    return updateMutation.mutate({ chatroomId, data })
  }

  const deleteChatroom = (chatroomId: number) => {
    return deleteMutation.mutate({ chatroomId })
  }

  return {
    createChatroom,
    updateChatroom,
    deleteChatroom,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    createMutation,
    updateMutation,
    deleteMutation,
  }
}
