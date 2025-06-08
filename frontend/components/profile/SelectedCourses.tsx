import { X } from 'lucide-react'

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
  disabled?: boolean
}

export default function SelectedCourses({
  courses,
  onRemoveCourse,
  disabled,
}: Props) {
  return (
    <div className="space-y-2">
      {courses.map((course) => (
        <div
          key={course.id}
          className="p-3 bg-gray-50 rounded-lg flex justify-between items-center"
        >
          <div>
            <div className="font-medium">{course.course_name}</div>
            <div className="text-sm text-gray-500">
              {course.course_code} • {course.offering_department} •{' '}
              {course.instructor} • {course.credit_units}학점
            </div>
          </div>
          <button
            className="hover:bg-gray-200 rounded-full p-1"
            onClick={() => onRemoveCourse(course.id)}
            disabled={disabled}
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}
      {courses.length === 0 && (
        <div className="text-center text-gray-500 py-4">
          아직 추가된 과목이 없습니다.
        </div>
      )}
    </div>
  )
}
