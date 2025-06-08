import { Plus, Search } from 'lucide-react'
import { useState, useEffect } from 'react'
import { Input } from '@/components/shadcn/input'
import { Button } from '@/components/shadcn/button'
import { searchCourseCatalogCoursesSearchGet } from '@/lib/api/generated/courses/courses'
import { useDebounce } from '@/hooks/useDebounce'

interface Course {
  id: number
  course_name: string
  course_code: string
  credit_units: string
  instructor: string
  offering_department: string
}

interface Props {
  onAddCourse: (course: Course) => void
  disabled?: boolean
}

export default function CourseSearch({ onAddCourse, disabled }: Props) {
  const [searchQuery, setSearchQuery] = useState('')
  const [showSearchResults, setShowSearchResults] = useState(false)
  const [searchResults, setSearchResults] = useState<Course[]>([])
  const [isSearching, setIsSearching] = useState(false)
  const debouncedSearchQuery = useDebounce(searchQuery, 300)

  useEffect(() => {
    const handleSearch = async () => {
      if (!debouncedSearchQuery.trim()) {
        setSearchResults([])
        return
      }

      try {
        setIsSearching(true)
        const results = await searchCourseCatalogCoursesSearchGet({
          q: debouncedSearchQuery,
          limit: 10,
        })
        setSearchResults(
          results.map((result) => ({
            id: result.id,
            course_name: result.course_name || '',
            course_code: result.course_code || '',
            credit_units: result.credit_units || '',
            instructor: result.instructor || '',
            offering_department: result.offering_department || '',
          }))
        )
      } catch (error) {
        console.error('과목 검색 중 오류 발생:', error)
        setSearchResults([])
      } finally {
        setIsSearching(false)
      }
    }

    handleSearch()
  }, [debouncedSearchQuery])

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
          disabled={disabled}
        />
      </div>

      {/* 검색 결과 */}
      {showSearchResults && searchQuery && (
        <div className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg">
          {isSearching ? (
            <div className="p-4 text-sm text-gray-500">검색 중...</div>
          ) : searchResults.length === 0 ? (
            <div className="p-4 text-sm text-gray-500">
              검색 결과가 없습니다.
            </div>
          ) : (
            <div className="max-h-[300px] overflow-y-auto">
              {searchResults.map((course) => (
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
                      disabled={disabled}
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
