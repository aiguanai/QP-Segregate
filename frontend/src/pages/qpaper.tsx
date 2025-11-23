import { useState, useEffect } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { 
  MagnifyingGlassIcon, 
  FunnelIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  AcademicCapIcon
} from '@heroicons/react/24/outline'

interface Question {
  question_id: number
  question_text: string
  marks?: number
  bloom_level?: number
  course_code: string
  unit_name?: string
  exam_type: string
  academic_year: number
  semester_type: string
  exam_date?: string
  variant_count: number
}

interface SearchFilters {
  course_codes: string[]
  unit_ids: number[]
  marks_min?: number
  marks_max?: number
  bloom_levels: number[]
  exam_types: string[]
  year_from?: number
  year_to?: number
}

export default function QPaperAI() {
  const router = useRouter()
  const [questions, setQuestions] = useState<Question[]>([])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState<SearchFilters>({
    course_codes: [],
    unit_ids: [],
    bloom_levels: [],
    exam_types: []
  })
  const [courses, setCourses] = useState<any[]>([])
  const [totalResults, setTotalResults] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)

  useEffect(() => {
    // Get search query from URL
    const { q } = router.query
    if (q && typeof q === 'string') {
      setSearchQuery(q)
      performSearch(q)
    }

    fetchCourses()
  }, [router])

  const fetchCourses = async () => {
    try {
      const response = await fetch('/api/courses')
      const data = await response.json()
      setCourses(data)
    } catch (error) {
      console.error('Failed to fetch courses:', error)
    }
  }

  const performSearch = async (query: string = searchQuery) => {
    if (!query.trim()) return

    setLoading(true)
    try {
      const response = await fetch('/api/public/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query,
          filters,
          page: currentPage,
          limit: 20
        })
      })

      if (!response.ok) {
        throw new Error('Search failed')
      }

      const data = await response.json()
      setQuestions(data.questions)
      setTotalResults(data.total)
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setCurrentPage(1)
    performSearch()
  }

  const handleFilterChange = (filterType: keyof SearchFilters, value: any) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }))
  }

  const clearFilters = () => {
    setFilters({
      course_codes: [],
      unit_ids: [],
      bloom_levels: [],
      exam_types: []
    })
  }

  const getBloomLevelColor = (level?: number) => {
    if (!level) return 'bg-gray-100 text-gray-800'
    
    const colors = {
      1: 'bg-red-100 text-red-800',
      2: 'bg-orange-100 text-orange-800',
      3: 'bg-yellow-100 text-yellow-800',
      4: 'bg-blue-100 text-blue-800',
      5: 'bg-purple-100 text-purple-800',
      6: 'bg-green-100 text-green-800'
    }
    return colors[level as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  return (
    <>
      <Head>
        <title>QPaper AI - Search Questions</title>
        <meta name="description" content="Search and explore question papers using AI-powered search" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center">
                <AcademicCapIcon className="h-8 w-8 text-primary-600 mr-2" />
                <h1 className="text-2xl font-bold text-gray-900">QPaper AI</h1>
              </div>
              <div className="flex space-x-4">
                <button
                  onClick={() => router.push('/')}
                  className="text-gray-600 hover:text-gray-900"
                >
                  Home
                </button>
                <button
                  onClick={() => router.push('/admin/login')}
                  className="btn-primary"
                >
                  Admin Login
                </button>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Search Form */}
          <div className="card mb-6">
            <form onSubmit={handleSearch} className="space-y-4">
              <div className="flex space-x-4">
                <div className="flex-1">
                  <input
                    type="text"
                    placeholder="Search for questions (e.g., 'explain database joins')"
                    className="input-field"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary flex items-center"
                >
                  <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
                  {loading ? 'Searching...' : 'Search'}
                </button>
              </div>

              <div className="flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => setShowFilters(!showFilters)}
                  className="flex items-center text-sm text-gray-600 hover:text-gray-900"
                >
                  <FunnelIcon className="h-4 w-4 mr-2" />
                  Filters
                  {showFilters ? (
                    <ChevronUpIcon className="h-4 w-4 ml-1" />
                  ) : (
                    <ChevronDownIcon className="h-4 w-4 ml-1" />
                  )}
                </button>

                {Object.values(filters).some(arr => Array.isArray(arr) ? arr.length > 0 : arr !== undefined && arr !== '') && (
                  <button
                    type="button"
                    onClick={clearFilters}
                    className="text-sm text-primary-600 hover:text-primary-500"
                  >
                    Clear Filters
                  </button>
                )}
              </div>
            </form>
          </div>

          {/* Filters */}
          {showFilters && (
            <div className="card mb-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Filters</h3>
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Course
                  </label>
                  <select
                    multiple
                    className="input-field"
                    value={filters.course_codes}
                    onChange={(e) => handleFilterChange('course_codes', Array.from(e.target.selectedOptions, option => option.value))}
                  >
                    {courses.map(course => (
                      <option key={course.course_code} value={course.course_code}>
                        {course.course_code} - {course.course_name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Marks Range
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="number"
                      placeholder="Min"
                      className="input-field"
                      value={filters.marks_min || ''}
                      onChange={(e) => handleFilterChange('marks_min', e.target.value ? parseInt(e.target.value) : undefined)}
                    />
                    <input
                      type="number"
                      placeholder="Max"
                      className="input-field"
                      value={filters.marks_max || ''}
                      onChange={(e) => handleFilterChange('marks_max', e.target.value ? parseInt(e.target.value) : undefined)}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Bloom Level
                  </label>
                  <div className="space-y-2">
                    {[1, 2, 3, 4, 5, 6].map(level => (
                      <label key={level} className="flex items-center">
                        <input
                          type="checkbox"
                          className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                          checked={filters.bloom_levels.includes(level)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              handleFilterChange('bloom_levels', [...filters.bloom_levels, level])
                            } else {
                              handleFilterChange('bloom_levels', filters.bloom_levels.filter(l => l !== level))
                            }
                          }}
                        />
                        <span className="ml-2 text-sm text-gray-700">L{level}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Exam Type
                  </label>
                  <div className="space-y-2">
                    {['CIE 1', 'CIE 2', 'Improvement CIE', 'SEE'].map(type => (
                      <label key={type} className="flex items-center">
                        <input
                          type="checkbox"
                          className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                          checked={filters.exam_types.includes(type)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              handleFilterChange('exam_types', [...filters.exam_types, type])
                            } else {
                              handleFilterChange('exam_types', filters.exam_types.filter(t => t !== type))
                            }
                          }}
                        />
                        <span className="ml-2 text-sm text-gray-700">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Results */}
          <div className="space-y-4">
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">Searching questions...</p>
              </div>
            ) : questions.length > 0 ? (
              <>
                <div className="flex justify-between items-center">
                  <p className="text-sm text-gray-600">
                    {totalResults} questions found
                  </p>
                </div>

                {questions.map((question) => (
                  <div key={question.question_id} className="card">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className="text-sm font-medium text-gray-900">
                            {question.course_code}
                          </span>
                          {question.unit_name && (
                            <span className="text-sm text-gray-600">
                              • {question.unit_name}
                            </span>
                          )}
                        </div>

                        <p className="text-gray-900 mb-3 line-clamp-3">
                          {question.question_text}
                        </p>

                        <div className="flex items-center space-x-4 text-sm">
                          {question.marks && (
                            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                              {question.marks} marks
                            </span>
                          )}
                          {question.bloom_level && (
                            <span className={`px-2 py-1 rounded ${getBloomLevelColor(question.bloom_level)}`}>
                              L{question.bloom_level}
                            </span>
                          )}
                          <span className="text-gray-600">
                            {question.exam_type} • {question.academic_year}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2 ml-4">
                        {question.variant_count > 0 && (
                          <button className="text-sm text-primary-600 hover:text-primary-500">
                            +{question.variant_count} variants
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </>
            ) : searchQuery ? (
              <div className="text-center py-8">
                <p className="text-gray-600">No questions found for your search.</p>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-600">Enter a search query to find questions.</p>
              </div>
            )}
          </div>
        </main>
      </div>
    </>
  )
}

