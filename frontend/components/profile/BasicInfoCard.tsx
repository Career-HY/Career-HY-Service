import { Save } from 'lucide-react'
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

export default function BasicInfoCard() {
  const [grade, setGrade] = useState('')
  const [department, setDepartment] = useState('')
  const [isBasicInfoEdited, setIsBasicInfoEdited] = useState(false)

  const handleBasicInfoChange = (
    field: 'grade' | 'department',
    value: string
  ) => {
    if (field === 'grade') setGrade(value)
    else setDepartment(value)
    setIsBasicInfoEdited(true)
  }

  const handleBasicInfoSave = () => {
    // TODO: API 호출
    console.log('기본 정보 저장:', { grade, department })
    setIsBasicInfoEdited(false)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>기본 정보</CardTitle>
        <CardDescription>
          학년, 학과 등 기본적인 정보를 관리합니다.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">학년</label>
              <Input
                placeholder="학년을 입력하세요"
                value={grade}
                onChange={(e) => handleBasicInfoChange('grade', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">학과</label>
              <Input
                placeholder="학과를 입력하세요"
                value={department}
                onChange={(e) =>
                  handleBasicInfoChange('department', e.target.value)
                }
              />
            </div>
          </div>
          <div className="flex justify-end">
            <Button onClick={handleBasicInfoSave} disabled={!isBasicInfoEdited}>
              <Save className="h-4 w-4 mr-2" />
              저장
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
