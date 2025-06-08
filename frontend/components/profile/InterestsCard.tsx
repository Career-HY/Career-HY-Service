import { Plus, X } from 'lucide-react'
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

export default function InterestsCard() {
  const [interestInput, setInterestInput] = useState('')
  const [interests, setInterests] = useState<string[]>([])

  const handleAddInterest = () => {
    if (interestInput.trim()) {
      setInterests([...interests, interestInput.trim()])
      setInterestInput('')
    }
  }

  const handleRemoveInterest = (index: number) => {
    setInterests(interests.filter((_, i) => i !== index))
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
            />
            <Button onClick={handleAddInterest}>
              <Plus className="h-4 w-4 mr-2" />
              추가
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
