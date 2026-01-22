import { useState, useEffect } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { useAuth } from '../../hooks/useAuth'
import ThemeToggle from '../../components/ThemeToggle'
import { api } from '../../utils/api'
import { 
  ClockIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  XCircleIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  CloudArrowUpIcon
} from '@heroicons/react/24/outline'

interface ActivityLog {
  log_id: number
  user_id: number
  username: string
  activity_type: string
  entity_type?: string
  entity_id?: string
  description: string
  metadata?: any
  created_at: string
}

export default function AdminActivity() {
  const { user } = useAuth()
  const router = useRouter()
  const [logs, setLogs] = useState<ActivityLog[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [filter, setFilter] = useState<string>('')

  useEffect(() => {
    if (!user) {
      router.push('/admin/login')
      return
    }

    fetchActivityLogs()
  }, [user, router, page, filter])

  const fetchActivityLogs = async () => {
    try {
      const params: any = { page, limit: 50 }
      if (filter) {
        params.activity_type = filter
      }
      const response = await api.get('/api/admin/activity-logs', { params })
      setLogs(response.data.logs)
      setTotalPages(response.data.pages)
    } catch (error) {
      console.error('Failed to fetch activity logs:', error)
    } finally {
      setLoading(false)
    }
  }

  const getActivityIcon = (activityType: string) => {
    switch (activityType) {
      case 'COURSE_CREATED':
        return <PlusIcon className="h-5 w-5 text-green-600 dark:text-green-500" />
      case 'COURSE_UPDATED':
        return <PencilIcon className="h-5 w-5 text-blue-600 dark:text-blue-500" />
      case 'COURSE_DELETED':
        return <TrashIcon className="h-5 w-5 text-red-600 dark:text-red-500" />
      case 'PAPER_UPLOADED':
        return <CloudArrowUpIcon className="h-5 w-5 text-purple-600 dark:text-purple-500" />
      case 'REVIEW_RESOLVED':
        return <CheckCircleIcon className="h-5 w-5 text-yellow-600 dark:text-yellow-500" />
      default:
        return <DocumentTextIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
    }
  }

  const getActivityColor = (activityType: string) => {
    switch (activityType) {
      case 'COURSE_CREATED':
        return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
      case 'COURSE_UPDATED':
        return 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200'
      case 'COURSE_DELETED':
        return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200'
      case 'PAPER_UPLOADED':
        return 'bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200'
      case 'REVIEW_RESOLVED':
        return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
    }
  }

  if (!user) {
    return null
  }

  return (
    <>
      <Head>
        <title>Activity History - QPaper AI</title>
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
        {/* Header */}
        <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 transition-colors">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center">
                <button
                  onClick={() => router.push('/admin/dashboard')}
                  className="text-primary-600 dark:text-primary-400 hover:text-primary-500 dark:hover:text-primary-300 mr-4 transition-colors"
                >
                  ← Back to Dashboard
                </button>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Activity History</h1>
              </div>
              <ThemeToggle />
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Filters */}
          <div className="mb-6">
            <div className="flex items-center space-x-4">
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Filter by type:</label>
              <select
                value={filter}
                onChange={(e) => {
                  setFilter(e.target.value)
                  setPage(1)
                }}
                className="input-field dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              >
                <option value="">All Activities</option>
                <option value="COURSE_CREATED">Course Created</option>
                <option value="COURSE_UPDATED">Course Updated</option>
                <option value="COURSE_DELETED">Course Deleted</option>
                <option value="PAPER_UPLOADED">Paper Uploaded</option>
                <option value="REVIEW_RESOLVED">Review Resolved</option>
              </select>
            </div>
          </div>

          {/* Activity Logs */}
          {loading ? (
            <div className="card dark:bg-gray-800 dark:border-gray-700 text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 dark:border-primary-400 mx-auto"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-300">Loading activity logs...</p>
            </div>
          ) : logs.length > 0 ? (
            <>
              <div className="space-y-4">
                {logs.map((log) => (
                  <div
                    key={log.log_id}
                    className="card dark:bg-gray-800 dark:border-gray-700"
                  >
                    <div className="flex items-start space-x-4">
                      <div className="flex-shrink-0 mt-1">
                        {getActivityIcon(log.activity_type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getActivityColor(log.activity_type)}`}>
                            {log.activity_type.replace('_', ' ')}
                          </span>
                          <span className="text-sm text-gray-500 dark:text-gray-400">
                            by {log.username}
                          </span>
                        </div>
                        <p className="text-sm text-gray-900 dark:text-white mb-1">
                          {log.description}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {new Date(log.created_at).toLocaleString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit'
                          })}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="mt-6 flex items-center justify-between">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <span className="text-sm text-gray-600 dark:text-gray-300">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="card dark:bg-gray-800 dark:border-gray-700 text-center py-12">
              <ClockIcon className="h-12 w-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
              <p className="text-gray-600 dark:text-gray-300">No activity logs found</p>
            </div>
          )}
        </main>
      </div>
    </>
  )
}

