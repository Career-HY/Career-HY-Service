import { X } from 'lucide-react'

interface Course {
  id: number
  course_name: string
  course_code: string
  credit_units: string
  instructor: string
  offering_department: string
  total_credits: string | null
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
    <div className="space-y-1.5">
      {courses.map((course) => (
        <div
          key={course.id}
          className="group px-4 py-2.5 bg-white border border-gray-200 hover:border-gray-300 rounded-lg flex justify-between items-center transition-colors duration-200"
        >
          <div className="text-sm flex-1 truncate">
            <span className="font-semibold text-gray-900">
              {course.course_name}
            </span>
            <span className="text-gray-500"> ({course.course_code})</span>
            <span className="text-gray-400"> | </span>
            <span className="text-gray-500">{course.offering_department}</span>
            <span className="text-gray-400"> | </span>
            <span className="text-gray-500">{course.instructor}</span>
            <span className="text-gray-400"> | </span>
            <span className="text-gray-500">{course.credit_units}</span>
            <span className="text-gray-400"> | </span>
            <span className="text-gray-500">{course.total_credits}학점</span>
          </div>
          <button
            className="ml-2 hover:bg-gray-100 rounded-full p-1.5 transition-all duration-200"
            onClick={() => onRemoveCourse(course.id)}
            disabled={disabled}
          >
            <X className="h-4 w-4 text-gray-500" />
          </button>
        </div>
      ))}
      {courses.length === 0 && (
        <div className="text-center text-gray-500 py-8 bg-gray-50 rounded-lg border border-dashed border-gray-300">
          아직 추가된 과목이 없습니다.
        </div>
      )}
    </div>
  )
}
