import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import { useAuth } from '../../hooks/useAuth'
import { api } from '../../utils/api'
import ThemeToggle from '../../components/ThemeToggle'
import { 
  AcademicCapIcon,
  ArrowLeftIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface Course {
  course_code: string
  course_name: string
  credits: number
  course_type: string
  description?: string
}

export default function StudentCourses() {
  const { user, logout } = useAuth()
  const router = useRouter()
  const [courses, setCourses] = useState<Course[]>([])
  const [selectedCourses, setSelectedCourses] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!user) {
      router.push('/student/login')
      return
    }
    fetchCourses()
    fetchMyCourses()
  }, [user, router])

  const fetchCourses = async () => {
    try {
      const response = await api.get('/api/courses')
      setCourses(response.data)
    } catch (error: any) {
      console.error('Failed to fetch courses:', error)
      toast.error('Failed to load courses')
    } finally {
      setLoading(false)
    }
  }

  const fetchMyCourses = async () => {
    try {
      const response = await api.get('/api/student/my-courses')
      // Assuming the response contains course codes
      if (response.data && Array.isArray(response.data)) {
        const courseCodes = response.data.map((item: any) => 
          item.course_code || item
        )
        setSelectedCourses(courseCodes)
      }
    } catch (error: any) {
      // If endpoint doesn't exist or returns error, that's okay
      console.log('My courses not available:', error)
    }
  }

  const handleToggleCourse = (courseCode: string) => {
    setSelectedCourses(prev => {
      if (prev.includes(courseCode)) {
        return prev.filter(c => c !== courseCode)
      } else {
        return [...prev, courseCode]
      }
    })
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await api.post('/api/student/select-courses', selectedCourses)
      toast.success('Courses saved successfully!')
      // Refresh the selected courses to reflect the saved state
      await fetchMyCourses()
      // Navigate back to dashboard after a short delay
      setTimeout(() => {
        router.push('/student/dashboard')
      }, 1000)
    } catch (error: any) {
      console.error('Failed to save courses:', error)
      toast.error(error.response?.data?.detail || 'Failed to save courses')
    } finally {
      setSaving(false)
    }
  }

  if (!user) {
    return null
  }

  return (
    <>
      <Head>
        <title>My Courses - QPaper AI</title>
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
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">My Courses</h1>
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
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Select Your Courses
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Select the courses you are enrolled in. This will help filter questions and papers relevant to you.
              </p>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 dark:border-primary-400 mx-auto"></div>
                <p className="mt-4 text-gray-600 dark:text-gray-400">Loading courses...</p>
              </div>
            ) : courses.length === 0 ? (
              <div className="text-center py-12">
                <AcademicCapIcon className="h-16 w-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                <p className="text-gray-600 dark:text-gray-400">No courses available</p>
              </div>
            ) : (
              <>
                <div className="space-y-3 mb-6 max-h-96 overflow-y-auto">
                  {courses.map((course) => (
                    <label
                      key={course.course_code}
                      className={`flex items-start p-4 border rounded-lg cursor-pointer transition-colors ${
                        selectedCourses.includes(course.course_code)
                          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                          : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={selectedCourses.includes(course.course_code)}
                        onChange={() => handleToggleCourse(course.course_code)}
                        className="mt-1 h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <div className="ml-3 flex-1">
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="flex items-center space-x-2">
                              <span className="font-medium text-gray-900 dark:text-white">
                                {course.course_code}
                              </span>
                              <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded">
                                {course.course_type}
                              </span>
                              <span className="text-xs text-gray-500 dark:text-gray-400">
                                {course.credits} credits
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                              {course.course_name}
                            </p>
                            {course.description && (
                              <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                                {course.description}
                              </p>
                            )}
                          </div>
                          {selectedCourses.includes(course.course_code) && (
                            <CheckCircleIcon className="h-5 w-5 text-primary-600 dark:text-primary-400" />
                          )}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {selectedCourses.length} course{selectedCourses.length !== 1 ? 's' : ''} selected
                  </div>
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="btn-primary disabled:opacity-50"
                  >
                    {saving ? 'Saving...' : 'Save Selection'}
                  </button>
                </div>
              </>
            )}
          </div>
        </main>
      </div>
    </>
  )
}

