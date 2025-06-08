import { Plus, X } from 'lucide-react'
import { useState, useEffect } from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/shadcn/card'
import { Input } from '@/components/shadcn/input'
import { Button } from '@/components/shadcn/button'
import { editProfileProfilesPatch } from '@/lib/api/generated/profiles/profiles'
import { useQueryClient } from '@tanstack/react-query'

interface Props {
  initialInterests: string[]
}

export default function InterestsCard({ initialInterests }: Props) {
  const queryClient = useQueryClient()
  const [interestInput, setInterestInput] = useState('')
  const [interests, setInterests] = useState<string[]>(initialInterests)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    setInterests(initialInterests)
  }, [initialInterests])

  const handleAddInterest = async () => {
    if (interestInput.trim()) {
      const newInterests = [...interests, interestInput.trim()]
      try {
        setIsSaving(true)
        await editProfileProfilesPatch({
          job_interests: newInterests,
        })
        await queryClient.invalidateQueries({ queryKey: ['profile'] })
        setInterests(newInterests)
        setInterestInput('')
      } catch (error) {
        console.error('관심직무 추가 중 오류 발생:', error)
      } finally {
        setIsSaving(false)
      }
    }
  }

  const handleRemoveInterest = async (index: number) => {
    try {
      setIsSaving(true)
      const newInterests = interests.filter((_, i) => i !== index)
      await editProfileProfilesPatch({
        job_interests: newInterests,
      })
      await queryClient.invalidateQueries({ queryKey: ['profile'] })
      setInterests(newInterests)
    } catch (error) {
      console.error('관심직무 삭제 중 오류 발생:', error)
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>관심직무</CardTitle>
        <CardDescription>관심 있는 직무를 등록해주세요.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="관심 직무를 입력하세요"
              className="flex-1"
              value={interestInput}
              onChange={(e) => setInterestInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleAddInterest()
                }
              }}
              disabled={isSaving}
            />
            <Button onClick={handleAddInterest} disabled={isSaving}>
              <Plus className="h-4 w-4 mr-2" />
              {isSaving ? '저장 중...' : '추가'}
            </Button>
          </div>
          <div className="flex flex-wrap gap-2">
            {interests.map((interest, index) => (
              <div
                key={index}
                className="bg-gray-100 px-3 py-1 rounded-full flex items-center gap-1"
              >
                {interest}
                <button
                  className="hover:bg-gray-200 rounded-full p-1"
                  onClick={() => handleRemoveInterest(index)}
                  disabled={isSaving}
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
