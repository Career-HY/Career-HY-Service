import { Plus } from 'lucide-react'
import { useState } from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/shadcn/card'
import { Input } from '@/components/shadcn/input'
import { Button } from '@/components/shadcn/button'

export default function ActivitiesCard() {
  const [activityInput, setActivityInput] = useState('')
  const [activities, setActivities] = useState<string[]>([])

  const handleAddActivity = () => {
    if (activityInput.trim()) {
      setActivities([...activities, activityInput.trim()])
      setActivityInput('')
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
            />
            <Button onClick={handleAddActivity}>
              <Plus className="h-4 w-4 mr-2" />
              추가
            </Button>
          </div>
          <div className="space-y-2">
            {activities.map((activity, index) => (
              <div key={index} className="p-3 bg-gray-50 rounded-lg">
                {activity}
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
