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
  initialCertifications: string[]
}

export default function CertificationsCard({ initialCertifications }: Props) {
  const queryClient = useQueryClient()
  const [certInput, setCertInput] = useState('')
  const [certifications, setCertifications] = useState<string[]>(
    initialCertifications
  )
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    setCertifications(initialCertifications)
  }, [initialCertifications])

  const handleAddCertification = async () => {
    if (certInput.trim()) {
      const newCertifications = [...certifications, certInput.trim()]
      try {
        setIsSaving(true)
        await editProfileProfilesPatch({
          certifications: newCertifications.map((content) => ({ content })),
        })
        await queryClient.invalidateQueries({ queryKey: ['profile'] })
        setCertifications(newCertifications)
        setCertInput('')
      } catch (error) {
        console.error('자격증 추가 중 오류 발생:', error)
      } finally {
        setIsSaving(false)
      }
    }
  }

  const handleRemoveCertification = async (index: number) => {
    try {
      setIsSaving(true)
      const newCertifications = certifications.filter((_, i) => i !== index)
      await editProfileProfilesPatch({
        certifications: newCertifications.map((content) => ({ content })),
      })
      await queryClient.invalidateQueries({ queryKey: ['profile'] })
      setCertifications(newCertifications)
    } catch (error) {
      console.error('자격증 삭제 중 오류 발생:', error)
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>자격증</CardTitle>
        <CardDescription>취득한 자격증 정보를 관리합니다.</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="자격증명을 입력하세요"
              className="flex-1"
              value={certInput}
              onChange={(e) => setCertInput(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleAddCertification()
                }
              }}
              disabled={isSaving}
            />
            <Button onClick={handleAddCertification} disabled={isSaving}>
              <Plus className="h-4 w-4 mr-2" />
              {isSaving ? '저장 중...' : '추가'}
            </Button>
          </div>
          <div className="space-y-2">
            {certifications.map((cert, index) => (
              <div
                key={index}
                className="p-3 bg-gray-50 rounded-lg flex justify-between items-center"
              >
                <span>{cert}</span>
                <button
                  className="hover:bg-gray-200 rounded-full p-1"
                  onClick={() => handleRemoveCertification(index)}
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
