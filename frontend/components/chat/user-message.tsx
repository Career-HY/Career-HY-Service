interface UserMessageProps {
  content: string
  timestamp: string
}

export default function UserMessage({ content, timestamp }: UserMessageProps) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[70%] p-4 rounded-2xl bg-gray-100 text-gray-900">
        <div className="whitespace-pre-wrap">{content}</div>
        <div className="text-xs mt-2 text-gray-500">{timestamp}</div>
      </div>
    </div>
  )
}
