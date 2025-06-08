import { X } from 'lucide-react'
import { Button } from '@/components/shadcn/button'

interface Course {
  id: number
  course_name: string
  course_code: string
  credit_units: string
  instructor: string
  offering_department: string
}

interface Props {
  courses: Course[]
  onRemoveCourse: (courseId: number) => void
}

export default function SelectedCourses({ courses, onRemoveCourse }: Props) {
  return (
    <div>
      <h3 className="font-medium mb-3">선택된 과목</h3>
      <div className="space-y-2">
        {courses.map((course) => (
          <div
            key={course.id}
            className="flex items-center justify-between p-3 border rounded-lg bg-blue-50 border-blue-200"
          >
            <div className="flex items-center gap-2 text-sm">
              <span className="font-medium">{course.course_name}</span>
              <span className="text-gray-500">
                ({course.course_code} • {course.offering_department} •{' '}
                {course.instructor} • {course.credit_units}학점)
              </span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="text-red-600 hover:text-red-700 hover:bg-red-50"
              onClick={() => onRemoveCourse(course.id)}
            >
              <X className="h-4 w-4 mr-1" />
              삭제
            </Button>
          </div>
        ))}
      </div>
    </div>
  )
}
