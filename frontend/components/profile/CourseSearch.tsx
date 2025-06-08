import { Plus, Search } from 'lucide-react'
import { useState } from 'react'
import { Input } from '@/components/shadcn/input'
import { Button } from '@/components/shadcn/button'

interface Course {
  id: number
  course_name: string
  course_code: string
  credit_units: string
  instructor: string
  offering_department: string
}

// 더미 데이터
const DUMMY_SEARCH_RESULTS = [
  {
    id: 1,
    course_name: '인공지능과 기계학습',
    course_code: 'CS4001',
    credit_units: '3',
    instructor: '김교수',
    offering_department: '컴퓨터공학과',
  },
  {
    id: 2,
    course_name: '웹 프로그래밍',
    course_code: 'CS3002',
    credit_units: '3',
    instructor: '이교수',
    offering_department: '소프트웨어학과',
  },
  {
    id: 3,
    course_name: '데이터베이스 시스템',
    course_code: 'CS3003',
    credit_units: '3',
    instructor: '박교수',
    offering_department: '컴퓨터공학과',
  },
]

interface Props {
  onAddCourse: (course: Course) => void
}

export default function CourseSearch({ onAddCourse }: Props) {
  const [searchQuery, setSearchQuery] = useState('')
  const [showSearchResults, setShowSearchResults] = useState(false)

  // 검색 결과 필터링
  const filteredResults = DUMMY_SEARCH_RESULTS.filter(
    (course) =>
      course.course_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      course.offering_department
        .toLowerCase()
        .includes(searchQuery.toLowerCase())
  )

  return (
    <div className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
        <Input
          placeholder="과목명 또는 개설학과로 검색"
          className="pl-10"
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value)
            setShowSearchResults(true)
          }}
          onFocus={() => setShowSearchResults(true)}
        />
      </div>

      {/* 검색 결과 */}
      {showSearchResults && searchQuery && (
        <div className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg">
          {filteredResults.length === 0 ? (
            <div className="p-4 text-sm text-gray-500">
              검색 결과가 없습니다.
            </div>
          ) : (
            <div className="max-h-[300px] overflow-y-auto">
              {filteredResults.map((course) => (
                <div
                  key={course.id}
                  className="p-3 hover:bg-gray-50 cursor-pointer border-b last:border-b-0"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{course.course_name}</div>
                      <div className="text-sm text-gray-500">
                        {course.course_code} • {course.offering_department} •{' '}
                        {course.instructor} • {course.credit_units}학점
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        onAddCourse(course)
                        setShowSearchResults(false)
                        setSearchQuery('')
                      }}
                    >
                      <Plus className="h-4 w-4 mr-1" />
                      추가
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
