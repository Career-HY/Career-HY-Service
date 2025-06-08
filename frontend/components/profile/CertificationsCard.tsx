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

export default function CertificationsCard() {
  const [certInput, setCertInput] = useState('')
  const [certifications, setCertifications] = useState<string[]>([])

  const handleAddCertification = () => {
    if (certInput.trim()) {
      setCertifications([...certifications, certInput.trim()])
      setCertInput('')
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
            />
            <Button onClick={handleAddCertification}>
              <Plus className="h-4 w-4 mr-2" />
              추가
            </Button>
          </div>
          <div className="space-y-2">
            {certifications.map((cert, index) => (
              <div key={index} className="p-3 bg-gray-50 rounded-lg">
                {cert}
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
