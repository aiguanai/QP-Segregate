import { useState, useEffect } from 'react'
import Head from 'next/head'
import { useAuth } from '../../hooks/useAuth'
import { useRouter } from 'next/router'
import ThemeToggle from '../../components/ThemeToggle'
import { api } from '../../utils/api'
import { 
  DocumentTextIcon, 
  QuestionMarkCircleIcon, 
  ClockIcon,
  ChartBarIcon,
  PlusIcon
} from '@heroicons/react/24/outline'

interface DashboardStats {
  total_papers: number
  total_questions: number
  pending_reviews: number
  bloom_distribution: Record<string, number>
  course_breakdown: Record<string, number>
}

export default function AdminDashboard() {
  const { user, logout } = useAuth()
  const router = useRouter()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) {
      router.push('/admin/login')
      return
    }

    fetchDashboardStats()
  }, [user, router])

  const fetchDashboardStats = async () => {
    try {
      const response = await api.get('/api/admin/analytics/dashboard')
      setStats(response.data)
    } catch (error) {
      console.error('Failed to fetch dashboard stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    router.push('/')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center transition-colors">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>Admin Dashboard - QPaper AI</title>
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 transition-colors">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Admin Dashboard</h1>
              </div>
              <div className="flex items-center space-x-4">
                <ThemeToggle />
                <span className="text-sm text-gray-600 dark:text-gray-300">Welcome, {user?.username}</span>
                <button
                  onClick={handleLogout}
                  className="text-sm text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Quick Actions */}
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <button
                onClick={() => router.push('/admin/upload')}
                className="card dark:bg-gray-800 dark:border-gray-700 hover:shadow-md transition-shadow duration-200 text-left"
              >
                <div className="flex items-center">
                  <PlusIcon className="h-8 w-8 text-primary-600 dark:text-primary-400 mr-3" />
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">Upload Paper</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-300">Add new question paper</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => router.push('/admin/review')}
                className="card dark:bg-gray-800 dark:border-gray-700 hover:shadow-md transition-shadow duration-200 text-left"
              >
                <div className="flex items-center">
                  <QuestionMarkCircleIcon className="h-8 w-8 text-yellow-600 dark:text-yellow-500 mr-3" />
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">Review Queue</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-300">Review classifications</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => router.push('/admin/analytics')}
                className="card dark:bg-gray-800 dark:border-gray-700 hover:shadow-md transition-shadow duration-200 text-left"
              >
                <div className="flex items-center">
                  <ChartBarIcon className="h-8 w-8 text-green-600 dark:text-green-500 mr-3" />
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">Analytics</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-300">View detailed reports</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => router.push('/admin/courses')}
                className="card dark:bg-gray-800 dark:border-gray-700 hover:shadow-md transition-shadow duration-200 text-left"
              >
                <div className="flex items-center">
                  <DocumentTextIcon className="h-8 w-8 text-blue-600 dark:text-blue-400 mr-3" />
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">Manage Courses</h3>
                    <p className="text-sm text-gray-600 dark:text-gray-300">Course management</p>
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* Statistics */}
          {stats && (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              <div className="card dark:bg-gray-800 dark:border-gray-700">
                <div className="flex items-center">
                  <DocumentTextIcon className="h-8 w-8 text-primary-600 dark:text-primary-400" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Total Papers</p>
                    <p className="text-2xl font-semibold text-gray-900 dark:text-white">{stats.total_papers}</p>
                  </div>
                </div>
              </div>

              <div className="card dark:bg-gray-800 dark:border-gray-700">
                <div className="flex items-center">
                  <QuestionMarkCircleIcon className="h-8 w-8 text-green-600 dark:text-green-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Total Questions</p>
                    <p className="text-2xl font-semibold text-gray-900 dark:text-white">{stats.total_questions}</p>
                  </div>
                </div>
              </div>

              <div className="card dark:bg-gray-800 dark:border-gray-700">
                <div className="flex items-center">
                  <ClockIcon className="h-8 w-8 text-yellow-600 dark:text-yellow-500" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Pending Reviews</p>
                    <p className="text-2xl font-semibold text-gray-900 dark:text-white">{stats.pending_reviews}</p>
                  </div>
                </div>
              </div>

              <div className="card dark:bg-gray-800 dark:border-gray-700">
                <div className="flex items-center">
                  <ChartBarIcon className="h-8 w-8 text-blue-600 dark:text-blue-400" />
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-300">Active Courses</p>
                    <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                      {Object.keys(stats.course_breakdown).length}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Recent Activity */}
          <div className="mt-8">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Recent Activity</h2>
            <div className="card dark:bg-gray-800 dark:border-gray-700">
              <p className="text-gray-600 dark:text-gray-300">Recent activity will be displayed here...</p>
            </div>
          </div>
        </main>
      </div>
    </>
  )
}
