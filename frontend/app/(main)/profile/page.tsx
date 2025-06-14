'use client'

import { useState, useEffect } from 'react'
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
import BasicInfoCard from '@/components/ui/profile/BasicInfoCard'
import InterestsCard from '@/components/ui/profile/InterestsCard'
import ActivitiesCard from '@/components/ui/profile/ActivitiesCard'
import CertificationsCard from '@/components/ui/profile/CertificationsCard'
import CourseSearch from '@/components/ui/profile/CourseSearch'
import SelectedCourses from '@/components/ui/profile/SelectedCourses'
import { useProfile } from '@/hooks/useProfile'
import { editProfileProfilesPatch } from '@/lib/api/generated/profiles/profiles'
import { useQueryClient } from '@tanstack/react-query'
import {
  type CourseCatalogRead,
  type CourseCatalogSearchResult,
} from '@/lib/api/generated/model'
import { Course } from '@/types/course'

const mapCourseCatalogToCourse = (
  catalog: CourseCatalogRead | CourseCatalogSearchResult
): Course => {
  return {
    id: catalog.id,
    course_name: catalog.course_name || '',
    course_code: catalog.course_code || '',
    credit_units: catalog.credit_units || '',
    instructor: catalog.instructor || '',
    offering_department: catalog.offering_department || '',
    total_credits: catalog.total_credits?.toString() || null,
  }
}

export default function ProfilePage() {
  const queryClient = useQueryClient()
  const { data: profile, isLoading } = useProfile()
  const [selectedCourses, setSelectedCourses] = useState<Course[]>([])
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    if (profile?.course_catalogs) {
      setSelectedCourses(profile.course_catalogs.map(mapCourseCatalogToCourse))
    }
  }, [profile?.course_catalogs])

  const handleAddCourse = async (course: Course) => {
    if (!selectedCourses.some((c) => c.id === course.id)) {
      try {
        setIsSaving(true)
        const newCourses = [...selectedCourses, course]
        await editProfileProfilesPatch({
          course_catalog_ids: newCourses.map((c) => c.id),
        })
        await queryClient.invalidateQueries({ queryKey: ['profile'] })
        setSelectedCourses(newCourses)
      } catch (error) {
        console.error('과목 추가 중 오류 발생:', error)
      } finally {
        setIsSaving(false)
      }
    }
  }

  const handleRemoveCourse = async (courseId: number) => {
    try {
      setIsSaving(true)
      const newCourses = selectedCourses.filter(
        (course) => course.id !== courseId
      )
      await editProfileProfilesPatch({
        course_catalog_ids: newCourses.map((c) => c.id),
      })
      await queryClient.invalidateQueries({ queryKey: ['profile'] })
      setSelectedCourses(newCourses)
    } catch (error) {
      console.error('과목 삭제 중 오류 발생:', error)
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return <div>로딩 중...</div>
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
              <BasicInfoCard
                initialGrade={profile?.grade || ''}
                initialDepartment={profile?.department || ''}
              />
              <InterestsCard
                initialInterests={
                  profile?.job_interests?.map((i) => i.interest) || []
                }
              />
              <ActivitiesCard
                initialActivities={
                  profile?.club_activities?.map((a) => a.content || '') || []
                }
              />
              <CertificationsCard
                initialCertifications={
                  profile?.certifications?.map((c) => c.content || '') || []
                }
              />
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
                  <CourseSearch
                    onAddCourse={handleAddCourse}
                    disabled={isSaving}
                  />
                  <SelectedCourses
                    courses={selectedCourses}
                    onRemoveCourse={handleRemoveCourse}
                    disabled={isSaving}
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
