import { useState, useEffect } from 'react'
import Head from 'next/head'
import { useAuth } from '../../hooks/useAuth'
import { useRouter } from 'next/router'
import { 
  MagnifyingGlassIcon, 
  BookmarkIcon, 
  AcademicCapIcon,
  ClockIcon,
  StarIcon
} from '@heroicons/react/24/outline'

interface Course {
  course_code: string
  course_name: string
  credits: number
  course_type: string
}

export default function StudentDashboard() {
  const { user, logout } = useAuth()
  const router = useRouter()
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    if (!user) {
      router.push('/student/login')
      return
    }

    fetchMyCourses()
  }, [user, router])

  const fetchMyCourses = async () => {
    try {
      const response = await fetch('/api/student/my-courses', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      const data = await response.json()
      setCourses(data)
    } catch (error) {
      console.error('Failed to fetch courses:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    router.push('/')
  }

  const handleSearch = () => {
    if (searchQuery.trim()) {
      router.push(`/student/search?q=${encodeURIComponent(searchQuery)}`)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>Student Dashboard - QPaper AI</title>
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-gray-900">Student Dashboard</h1>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">Welcome, {user?.username}</span>
                <button
                  onClick={handleLogout}
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Search Section */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Search Questions</h2>
            <div className="card">
              <div className="flex space-x-4">
                <div className="flex-1">
                  <input
                    type="text"
                    placeholder="Search for questions (e.g., 'explain database joins')"
                    className="input-field"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  />
                </div>
                <button
                  onClick={handleSearch}
                  className="btn-primary flex items-center"
                >
                  <MagnifyingGlassIcon className="h-5 w-5 mr-2" />
                  Search
                </button>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <button
                onClick={() => router.push('/student/search')}
                className="card hover:shadow-md transition-shadow duration-200 text-left"
              >
                <div className="flex items-center">
                  <MagnifyingGlassIcon className="h-8 w-8 text-primary-600 mr-3" />
                  <div>
                    <h3 className="font-medium text-gray-900">Search Questions</h3>
                    <p className="text-sm text-gray-600">Find specific questions</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => router.push('/student/bookmarks')}
                className="card hover:shadow-md transition-shadow duration-200 text-left"
              >
                <div className="flex items-center">
                  <BookmarkIcon className="h-8 w-8 text-yellow-600 mr-3" />
                  <div>
                    <h3 className="font-medium text-gray-900">My Bookmarks</h3>
                    <p className="text-sm text-gray-600">Saved questions</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => router.push('/student/practice')}
                className="card hover:shadow-md transition-shadow duration-200 text-left"
              >
                <div className="flex items-center">
                  <AcademicCapIcon className="h-8 w-8 text-green-600 mr-3" />
                  <div>
                    <h3 className="font-medium text-gray-900">Practice Mode</h3>
                    <p className="text-sm text-gray-600">Random questions</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => router.push('/student/courses')}
                className="card hover:shadow-md transition-shadow duration-200 text-left"
              >
                <div className="flex items-center">
                  <StarIcon className="h-8 w-8 text-blue-600 mr-3" />
                  <div>
                    <h3 className="font-medium text-gray-900">My Courses</h3>
                    <p className="text-sm text-gray-600">View course details</p>
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* My Courses */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">My Courses</h2>
            {courses.length > 0 ? (
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {courses.map((course) => (
                  <div key={course.course_code} className="card">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-medium text-gray-900">{course.course_code}</h3>
                        <p className="text-sm text-gray-600 mt-1">{course.course_name}</p>
                        <p className="text-xs text-gray-500 mt-2">
                          {course.credits} credits • {course.course_type}
                        </p>
                      </div>
                      <button
                        onClick={() => router.push(`/student/search?course=${course.course_code}`)}
                        className="text-primary-600 hover:text-primary-500 text-sm"
                      >
                        View Questions
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="card text-center py-8">
                <AcademicCapIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No courses found for your profile</p>
              </div>
            )}
          </div>

          {/* Recent Activity */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
            <div className="card">
              <p className="text-gray-600">Recent activity will be displayed here...</p>
            </div>
          </div>
        </main>
      </div>
    </>
  )
}
