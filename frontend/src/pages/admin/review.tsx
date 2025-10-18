import { useState, useEffect } from 'react'
import Head from 'next/head'
import { useAuth } from '../../hooks/useAuth'
import { useRouter } from 'next/router'
import { 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XMarkIcon,
  PencilIcon
} from '@heroicons/react/24/outline'

interface ReviewItem {
  review_id: number
  question_id: number
  question_text: string
  issue_type: string
  suggested_correction: any
  priority: number
  created_at: string
}

export default function AdminReview() {
  const { user } = useAuth()
  const router = useRouter()
  const [reviewItems, setReviewItems] = useState<ReviewItem[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedItem, setSelectedItem] = useState<ReviewItem | null>(null)
  const [corrections, setCorrections] = useState({
    unit_id: '',
    bloom_level: '',
    marks: ''
  })

  useEffect(() => {
    if (!user) {
      router.push('/admin/login')
      return
    }

    fetchReviewQueue()
  }, [user, router])

  const fetchReviewQueue = async () => {
    try {
      const response = await fetch('/api/admin/review-queue', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      const data = await response.json()
      setReviewItems(data)
    } catch (error) {
      console.error('Failed to fetch review queue:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (questionId: number, approved: boolean) => {
    try {
      await fetch(`/api/admin/approve-question/${questionId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          approved,
          ...(approved && {
            unit_id: corrections.unit_id ? parseInt(corrections.unit_id) : undefined,
            bloom_level: corrections.bloom_level ? parseInt(corrections.bloom_level) : undefined,
            marks: corrections.marks ? parseInt(corrections.marks) : undefined
          })
        })
      })

      // Remove from list
      setReviewItems(prev => prev.filter(item => item.question_id !== questionId))
      setSelectedItem(null)
    } catch (error) {
      console.error('Failed to approve question:', error)
    }
  }

  const getPriorityColor = (priority: number) => {
    switch (priority) {
      case 1: return 'bg-red-100 text-red-800'
      case 2: return 'bg-yellow-100 text-yellow-800'
      case 3: return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getIssueTypeColor = (issueType: string) => {
    switch (issueType) {
      case 'LOW_CONFIDENCE': return 'bg-yellow-100 text-yellow-800'
      case 'AMBIGUOUS_UNIT': return 'bg-blue-100 text-blue-800'
      case 'OCR_ERROR': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (!user) {
    return null
  }

  return (
    <>
      <Head>
        <title>Review Queue - QPaper AI</title>
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center">
                <button
                  onClick={() => router.push('/admin/dashboard')}
                  className="text-primary-600 hover:text-primary-500 mr-4"
                >
                  ← Back to Dashboard
                </button>
                <h1 className="text-2xl font-bold text-gray-900">Review Queue</h1>
              </div>
              <div className="text-sm text-gray-600">
                {reviewItems.length} items pending review
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading review queue...</p>
            </div>
          ) : reviewItems.length > 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Review Items List */}
              <div className="space-y-4">
                <h2 className="text-lg font-semibold text-gray-900">Items to Review</h2>
                {reviewItems.map((item) => (
                  <div
                    key={item.review_id}
                    className={`card cursor-pointer transition-colors duration-200 ${
                      selectedItem?.review_id === item.review_id
                        ? 'ring-2 ring-primary-500 bg-primary-50'
                        : 'hover:shadow-md'
                    }`}
                    onClick={() => setSelectedItem(item)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityColor(item.priority)}`}>
                            Priority {item.priority}
                          </span>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getIssueTypeColor(item.issue_type)}`}>
                            {item.issue_type.replace('_', ' ')}
                          </span>
                        </div>
                        <p className="text-sm text-gray-900 line-clamp-3">
                          {item.question_text}
                        </p>
                        <p className="text-xs text-gray-500 mt-2">
                          {new Date(item.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Review Panel */}
              {selectedItem && (
                <div className="card">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">Review Question</h3>
                    <button
                      onClick={() => setSelectedItem(null)}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <XMarkIcon className="h-5 w-5" />
                    </button>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Question Text
                      </label>
                      <div className="p-3 bg-gray-50 rounded-lg text-sm text-gray-900">
                        {selectedItem.question_text}
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Issue Type
                      </label>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getIssueTypeColor(selectedItem.issue_type)}`}>
                        {selectedItem.issue_type.replace('_', ' ')}
                      </span>
                    </div>

                    {selectedItem.suggested_correction && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Suggested Corrections
                        </label>
                        <div className="p-3 bg-blue-50 rounded-lg text-sm">
                          <pre className="whitespace-pre-wrap">
                            {JSON.stringify(selectedItem.suggested_correction, null, 2)}
                          </pre>
                        </div>
                      </div>
                    )}

                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Unit ID (Optional)
                        </label>
                        <input
                          type="number"
                          className="input-field"
                          value={corrections.unit_id}
                          onChange={(e) => setCorrections(prev => ({ ...prev, unit_id: e.target.value }))}
                          placeholder="Enter unit ID"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Bloom Level (Optional)
                        </label>
                        <select
                          className="input-field"
                          value={corrections.bloom_level}
                          onChange={(e) => setCorrections(prev => ({ ...prev, bloom_level: e.target.value }))}
                        >
                          <option value="">Select Bloom Level</option>
                          <option value="1">L1 - Remembering</option>
                          <option value="2">L2 - Understanding</option>
                          <option value="3">L3 - Applying</option>
                          <option value="4">L4 - Analyzing</option>
                          <option value="5">L5 - Evaluating</option>
                          <option value="6">L6 - Creating</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Marks (Optional)
                        </label>
                        <input
                          type="number"
                          className="input-field"
                          value={corrections.marks}
                          onChange={(e) => setCorrections(prev => ({ ...prev, marks: e.target.value }))}
                          placeholder="Enter marks"
                        />
                      </div>
                    </div>

                    <div className="flex space-x-3 pt-4">
                      <button
                        onClick={() => handleApprove(selectedItem.question_id, true)}
                        className="flex-1 btn-primary flex items-center justify-center"
                      >
                        <CheckCircleIcon className="h-4 w-4 mr-2" />
                        Approve
                      </button>
                      <button
                        onClick={() => handleApprove(selectedItem.question_id, false)}
                        className="flex-1 btn-secondary flex items-center justify-center"
                      >
                        <XMarkIcon className="h-4 w-4 mr-2" />
                        Reject
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-12">
              <CheckCircleIcon className="h-16 w-16 text-green-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">All Caught Up!</h2>
              <p className="text-gray-600">No items in the review queue.</p>
            </div>
          )}
        </main>
      </div>
    </>
  )
}
