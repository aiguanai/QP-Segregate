import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import { useAuth } from '../../hooks/useAuth'
import { api } from '../../utils/api'
import ThemeToggle from '../../components/ThemeToggle'
import { 
  DocumentTextIcon,
  ArrowLeftIcon,
  ArrowDownTrayIcon,
  FunnelIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface QuestionPaper {
  paper_id: number
  course_code: string
  course_name?: string
  academic_year: number
  semester_type: string
  exam_type: string
  exam_date?: string
  total_questions_extracted: number
  processing_status: string
  created_at: string
}

export default function StudentPapers() {
  const { user, logout } = useAuth()
  const router = useRouter()
  const [papers, setPapers] = useState<QuestionPaper[]>([])
  const [loading, setLoading] = useState(true)
  const [filterCourse, setFilterCourse] = useState('')
  const [courses, setCourses] = useState<Array<{course_code: string, course_name: string}>>([])
  const [selectedCourses, setSelectedCourses] = useState<string[]>([])

  useEffect(() => {
    if (!user) {
      router.push('/student/login')
      return
    }
    fetchMyCourses()
    fetchCourses()
  }, [user, router])

  useEffect(() => {
    if (selectedCourses.length > 0 || filterCourse) {
      fetchPapers()
    } else {
      setPapers([])
      setLoading(false)
    }
  }, [selectedCourses, filterCourse])

  const fetchMyCourses = async () => {
    try {
      const response = await api.get('/api/student/my-courses')
      if (response.data && Array.isArray(response.data)) {
        const courseCodes = response.data.map((item: any) => 
          item.course_code || item
        )
        setSelectedCourses(courseCodes)
      }
    } catch (error) {
      console.log('My courses not available')
    }
  }

  const fetchCourses = async () => {
    try {
      const response = await api.get('/api/courses')
      setCourses(response.data.map((c: any) => ({ 
        course_code: c.course_code, 
        course_name: c.course_name 
      })))
    } catch (error) {
      console.error('Failed to fetch courses:', error)
    }
  }

  const fetchPapers = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (selectedCourses.length > 0) {
        selectedCourses.forEach(code => params.append('course_codes', code))
      }
      if (filterCourse) {
        params.append('course_codes', filterCourse)
      }
      
      const response = await api.get(`/api/student/papers?${params.toString()}`)
      setPapers(response.data)
    } catch (error: any) {
      console.error('Failed to fetch papers:', error)
      toast.error(error.response?.data?.detail || 'Failed to load question papers')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async (paperId: number) => {
    try {
      const response = await api.get(`/api/student/papers/${paperId}/download`, {
        responseType: 'blob'
      })
      
      // Create blob URL and download
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `question-paper-${paperId}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast.success('Question paper downloaded')
    } catch (error: any) {
      console.error('Failed to download paper:', error)
      toast.error('Failed to download question paper')
    }
  }

  if (!user) {
    return null
  }

  return (
    <>
      <Head>
        <title>Question Papers - QPaper AI</title>
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 transition-colors">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => router.push('/student/dashboard')}
                  className="text-primary-600 dark:text-primary-400 hover:text-primary-500 dark:hover:text-primary-300 transition-colors"
                >
                  <ArrowLeftIcon className="h-5 w-5" />
                </button>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Question Papers</h1>
              </div>
              <div className="flex items-center space-x-4">
                <ThemeToggle />
                <button
                  onClick={logout}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Filter */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-6">
            <div className="flex items-center space-x-4">
              <FunnelIcon className="h-5 w-5 text-gray-500 dark:text-gray-400" />
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Filter by Course
                </label>
                <select
                  value={filterCourse}
                  onChange={(e) => setFilterCourse(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="">All Courses</option>
                  {courses.map(course => (
                    <option key={course.course_code} value={course.course_code}>
                      {course.course_code} - {course.course_name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            {selectedCourses.length > 0 && !filterCourse && (
              <div className="mt-3 text-sm text-gray-600 dark:text-gray-400">
                Showing papers for your selected courses: {selectedCourses.join(', ')}
              </div>
            )}
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 dark:border-primary-400 mx-auto"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">Loading question papers...</p>
            </div>
          ) : papers.length === 0 ? (
            <div className="text-center py-12">
              <DocumentTextIcon className="h-16 w-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                No Question Papers Found
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                {selectedCourses.length === 0 && !filterCourse
                  ? 'Select your courses first to see relevant question papers.'
                  : 'No question papers available for the selected courses.'}
              </p>
              {selectedCourses.length === 0 && (
                <button
                  onClick={() => router.push('/student/courses')}
                  className="btn-primary"
                >
                  Select Courses
                </button>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {papers.length} question paper{papers.length !== 1 ? 's' : ''} found
              </div>
              {papers.map((paper) => (
                <div
                  key={paper.paper_id}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {paper.course_code}
                        </h3>
                        {paper.course_name && (
                          <span className="text-sm text-gray-600 dark:text-gray-400">
                            - {paper.course_name}
                          </span>
                        )}
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Exam Type:</span>
                          <span className="ml-2 text-gray-900 dark:text-white">{paper.exam_type}</span>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Year:</span>
                          <span className="ml-2 text-gray-900 dark:text-white">Year {paper.academic_year}</span>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Semester:</span>
                          <span className="ml-2 text-gray-900 dark:text-white">{paper.semester_type}</span>
                        </div>
                        {paper.exam_date && (
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Date:</span>
                            <span className="ml-2 text-gray-900 dark:text-white">
                              {new Date(paper.exam_date).toLocaleDateString()}
                            </span>
                          </div>
                        )}
                      </div>
                      {paper.total_questions_extracted > 0 && (
                        <div className="mt-3 text-sm text-gray-600 dark:text-gray-400">
                          {paper.total_questions_extracted} questions extracted
                        </div>
                      )}
                    </div>
                    <button
                      onClick={() => handleDownload(paper.paper_id)}
                      className="ml-4 p-2 text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded transition-colors"
                      title="Download question paper"
                    >
                      <ArrowDownTrayIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>
    </>
  )
}

