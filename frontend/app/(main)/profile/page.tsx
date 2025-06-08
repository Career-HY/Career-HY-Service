'use client'

import { useState } from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/shadcn/card'
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/shadcn/tabs'
import BasicInfoCard from '@/components/profile/BasicInfoCard'
import InterestsCard from '@/components/profile/InterestsCard'
import ActivitiesCard from '@/components/profile/ActivitiesCard'
import CertificationsCard from '@/components/profile/CertificationsCard'
import CourseSearch from '@/components/profile/CourseSearch'
import SelectedCourses from '@/components/profile/SelectedCourses'

// 더미 데이터
const DUMMY_SELECTED_COURSES = [
  {
    id: 4,
    course_name: '운영체제',
    course_code: 'CS3004',
    credit_units: '3',
    instructor: '최교수',
    offering_department: '컴퓨터공학과',
  },
  {
    id: 5,
    course_name: '컴퓨터네트워크',
    course_code: 'CS3005',
    credit_units: '3',
    instructor: '정교수',
    offering_department: '컴퓨터공학과',
  },
]

interface Course {
  id: number
  course_name: string
  course_code: string
  credit_units: string
  instructor: string
  offering_department: string
}

export default function ProfilePage() {
  const [selectedCourses, setSelectedCourses] = useState<Course[]>(
    DUMMY_SELECTED_COURSES
  )

  const handleAddCourse = (course: Course) => {
    if (!selectedCourses.some((c) => c.id === course.id)) {
      setSelectedCourses([...selectedCourses, course])
    }
  }

  const handleRemoveCourse = (courseId: number) => {
    setSelectedCourses(
      selectedCourses.filter((course) => course.id !== courseId)
    )
  }

  return (
    <div className="container mx-auto p-6">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">내 프로필</h1>

        <Tabs defaultValue="basic" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="basic">기본 정보</TabsTrigger>
            <TabsTrigger value="courses">수강 이력</TabsTrigger>
          </TabsList>

          {/* 기본 정보 탭 */}
          <TabsContent value="basic">
            <div className="space-y-6">
              <BasicInfoCard />
              <InterestsCard />
              <ActivitiesCard />
              <CertificationsCard />
            </div>
          </TabsContent>

          {/* 수강 이력 탭 */}
          <TabsContent value="courses">
            <Card>
              <CardHeader>
                <CardTitle>수강 이력</CardTitle>
                <CardDescription>수강한 과목들을 관리합니다.</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <CourseSearch onAddCourse={handleAddCourse} />
                  <SelectedCourses
                    courses={selectedCourses}
                    onRemoveCourse={handleRemoveCourse}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
