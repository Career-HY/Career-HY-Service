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
  initialActivities: string[]
}

export default function ActivitiesCard({ initialActivities }: Props) {
  const queryClient = useQueryClient()
  const [activityInput, setActivityInput] = useState('')
  const [activities, setActivities] = useState<string[]>(initialActivities)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    setActivities(initialActivities)
  }, [initialActivities])

  const handleAddActivity = async () => {
    if (activityInput.trim()) {
      const newActivities = [...activities, activityInput.trim()]
      try {
        setIsSaving(true)
        await editProfileProfilesPatch({
          club_activities: newActivities.map((content) => ({ content })),
        })
        await queryClient.invalidateQueries({ queryKey: ['profile'] })
        setActivities(newActivities)
        setActivityInput('')
      } catch (error) {
        console.error('동아리/대외활동 추가 중 오류 발생:', error)
      } finally {
        setIsSaving(false)
      }
    }
  }

  const handleRemoveActivity = async (index: number) => {
    try {
      setIsSaving(true)
      const newActivities = activities.filter((_, i) => i !== index)
      await editProfileProfilesPatch({
        club_activities: newActivities.map((content) => ({ content })),
      })
      await queryClient.invalidateQueries({ queryKey: ['profile'] })
      setActivities(newActivities)
    } catch (error) {
      console.error('동아리/대외활동 삭제 중 오류 발생:', error)
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>동아리/대외활동</CardTitle>
        <CardDescription>
          참여한 동아리와 대외활동을 관리합니다.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="활동 내용을 입력하세요"
              className="flex-1"
              value={activityInput}
              onChange={(e) => setActivityInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleAddActivity()
                }
              }}
              disabled={isSaving}
            />
            <Button onClick={handleAddActivity} disabled={isSaving}>
              <Plus className="h-4 w-4 mr-2" />
              {isSaving ? '저장 중...' : '추가'}
            </Button>
          </div>
          <div className="space-y-2">
            {activities.map((activity, index) => (
              <div
                key={index}
                className="p-3 bg-gray-50 rounded-lg flex justify-between items-center"
              >
                <span>{activity}</span>
                <button
                  className="hover:bg-gray-200 rounded-full p-1"
                  onClick={() => handleRemoveActivity(index)}
                  disabled={isSaving}
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
