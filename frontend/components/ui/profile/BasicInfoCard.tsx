import { Save } from 'lucide-react'
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
  initialGrade: string
  initialDepartment: string
}

export default function BasicInfoCard({
  initialGrade,
  initialDepartment,
}: Props) {
  const queryClient = useQueryClient()
  const [grade, setGrade] = useState(initialGrade)
  const [department, setDepartment] = useState(initialDepartment)
  const [isBasicInfoEdited, setIsBasicInfoEdited] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    setGrade(initialGrade)
    setDepartment(initialDepartment)
  }, [initialGrade, initialDepartment])

  const handleBasicInfoChange = (
    field: 'grade' | 'department',
    value: string
  ) => {
    if (field === 'grade') setGrade(value)
    else setDepartment(value)
    setIsBasicInfoEdited(true)
  }

  const handleBasicInfoSave = async () => {
    try {
      setIsSaving(true)
      await editProfileProfilesPatch({
        grade,
        department,
      })
      await queryClient.invalidateQueries({ queryKey: ['profile'] })
      setIsBasicInfoEdited(false)
    } catch (error) {
      console.error('프로필 수정 중 오류 발생:', error)
    } finally {
      setIsSaving(false)
    }
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
            <Button
              onClick={handleBasicInfoSave}
              disabled={!isBasicInfoEdited || isSaving}
            >
              <Save className="h-4 w-4 mr-2" />
              {isSaving ? '저장 중...' : '저장'}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
