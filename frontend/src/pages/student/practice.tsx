import { useState, useEffect } from 'react'
import Head from 'next/head'
import { useAuth } from '../../hooks/useAuth'
import { useRouter } from 'next/router'
import { 
  AcademicCapIcon,
  ClockIcon,
  StarIcon,
  ArrowRightIcon,
  ArrowLeftIcon
} from '@heroicons/react/24/outline'

interface Question {
  question_id: number
  question_text: string
  marks?: number
  bloom_level?: number
  bloom_category?: string
  difficulty_level?: string
  course_code: string
  unit_name?: string
  exam_type: string
  academic_year: number
}

interface PracticeSettings {
  course_code: string
  unit_ids: number[]
  count: number
  bloom_levels: number[]
}

export default function StudentPractice() {
  const { user } = useAuth()
  const router = useRouter()
  const [questions, setQuestions] = useState<Question[]>([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [showAnswer, setShowAnswer] = useState(false)
  const [settings, setSettings] = useState<PracticeSettings>({
    course_code: '',
    unit_ids: [],
    count: 10,
    bloom_levels: []
  })
  const [courses, setCourses] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [practiceStarted, setPracticeStarted] = useState(false)
  const [timeElapsed, setTimeElapsed] = useState(0)
  const [timer, setTimer] = useState<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!user) {
      router.push('/student/login')
      return
    }

    fetchCourses()
  }, [user, router])

  useEffect(() => {
    if (practiceStarted && questions.length > 0) {
      const interval = setInterval(() => {
        setTimeElapsed(prev => prev + 1)
      }, 1000)
      setTimer(interval)
      return () => clearInterval(interval)
    }
  }, [practiceStarted, questions])

  const fetchCourses = async () => {
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
    }
  }

  const startPractice = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/student/random-questions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(settings)
      })

      const data = await response.json()
      setQuestions(data)
      setCurrentQuestionIndex(0)
      setShowAnswer(false)
      setPracticeStarted(true)
      setTimeElapsed(0)
    } catch (error) {
      console.error('Failed to start practice:', error)
    } finally {
      setLoading(false)
    }
  }

  const nextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1)
      setShowAnswer(false)
    }
  }

  const previousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1)
      setShowAnswer(false)
    }
  }

  const endPractice = () => {
    setPracticeStarted(false)
    setQuestions([])
    setCurrentQuestionIndex(0)
    setShowAnswer(false)
    setTimeElapsed(0)
    if (timer) {
      clearInterval(timer)
      setTimer(null)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
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

  const getDifficultyColor = (level?: string) => {
    switch (level) {
      case 'Easy': return 'bg-green-100 text-green-800'
      case 'Medium': return 'bg-yellow-100 text-yellow-800'
      case 'Hard': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (!user) {
    return null
  }

  return (
    <>
      <Head>
        <title>Practice Mode - QPaper AI</title>
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-4">
              <div className="flex items-center">
                <button
                  onClick={() => router.push('/student/dashboard')}
                  className="text-primary-600 hover:text-primary-500 mr-4"
                >
                  ← Back to Dashboard
                </button>
                <h1 className="text-2xl font-bold text-gray-900">Practice Mode</h1>
              </div>
              {practiceStarted && (
                <div className="flex items-center space-x-4">
                  <div className="flex items-center text-sm text-gray-600">
                    <ClockIcon className="h-4 w-4 mr-1" />
                    {formatTime(timeElapsed)}
                  </div>
                  <button
                    onClick={endPractice}
                    className="text-sm text-gray-600 hover:text-gray-900"
                  >
                    End Practice
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {!practiceStarted ? (
            /* Practice Settings */
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-6">Practice Settings</h2>
              
              <form onSubmit={(e) => { e.preventDefault(); startPractice(); }} className="space-y-6">
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Course *
                    </label>
                    <select
                      required
                      className="input-field"
                      value={settings.course_code}
                      onChange={(e) => setSettings(prev => ({ ...prev, course_code: e.target.value }))}
                    >
                      <option value="">Select Course</option>
                      {courses.map(course => (
                        <option key={course.course_code} value={course.course_code}>
                          {course.course_code} - {course.course_name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Number of Questions
                    </label>
                    <select
                      className="input-field"
                      value={settings.count}
                      onChange={(e) => setSettings(prev => ({ ...prev, count: parseInt(e.target.value) }))}
                    >
                      <option value={5}>5 Questions</option>
                      <option value={10}>10 Questions</option>
                      <option value={15}>15 Questions</option>
                      <option value={20}>20 Questions</option>
                      <option value={30}>30 Questions</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Bloom Levels (Optional)
                  </label>
                  <div className="grid grid-cols-3 gap-2">
                    {[1, 2, 3, 4, 5, 6].map(level => (
                      <label key={level} className="flex items-center">
                        <input
                          type="checkbox"
                          className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                          checked={settings.bloom_levels.includes(level)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSettings(prev => ({ ...prev, bloom_levels: [...prev.bloom_levels, level] }))
                            } else {
                              setSettings(prev => ({ ...prev, bloom_levels: prev.bloom_levels.filter(l => l !== level) }))
                            }
                          }}
                        />
                        <span className="ml-2 text-sm text-gray-700">L{level}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={loading || !settings.course_code}
                    className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? 'Starting...' : 'Start Practice'}
                  </button>
                </div>
              </form>
            </div>
          ) : questions.length > 0 ? (
            /* Practice Session */
            <div className="space-y-6">
              {/* Progress Bar */}
              <div className="card">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-700">
                    Question {currentQuestionIndex + 1} of {questions.length}
                  </span>
                  <span className="text-sm text-gray-600">
                    {Math.round(((currentQuestionIndex + 1) / questions.length) * 100)}% Complete
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
                  ></div>
                </div>
              </div>

              {/* Question Card */}
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <AcademicCapIcon className="h-5 w-5 text-primary-600" />
                    <span className="text-sm font-medium text-gray-700">
                      {questions[currentQuestionIndex].course_code}
                    </span>
                    {questions[currentQuestionIndex].unit_name && (
                      <span className="text-sm text-gray-600">
                        • {questions[currentQuestionIndex].unit_name}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    {questions[currentQuestionIndex].marks && (
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                        {questions[currentQuestionIndex].marks} marks
                      </span>
                    )}
                    {questions[currentQuestionIndex].bloom_level && (
                      <span className={`px-2 py-1 rounded text-xs ${getBloomLevelColor(questions[currentQuestionIndex].bloom_level)}`}>
                        L{questions[currentQuestionIndex].bloom_level}
                      </span>
                    )}
                    {questions[currentQuestionIndex].difficulty_level && (
                      <span className={`px-2 py-1 rounded text-xs ${getDifficultyColor(questions[currentQuestionIndex].difficulty_level)}`}>
                        {questions[currentQuestionIndex].difficulty_level}
                      </span>
                    )}
                  </div>
                </div>

                <div className="mb-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    {questions[currentQuestionIndex].question_text}
                  </h3>
                </div>

                <div className="flex justify-between items-center">
                  <div className="flex space-x-3">
                    <button
                      onClick={previousQuestion}
                      disabled={currentQuestionIndex === 0}
                      className="btn-secondary flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ArrowLeftIcon className="h-4 w-4 mr-2" />
                      Previous
                    </button>
                    <button
                      onClick={nextQuestion}
                      disabled={currentQuestionIndex === questions.length - 1}
                      className="btn-primary flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next
                      <ArrowRightIcon className="h-4 w-4 ml-2" />
                    </button>
                  </div>

                  <div className="text-sm text-gray-600">
                    {questions[currentQuestionIndex].exam_type} • {questions[currentQuestionIndex].academic_year}
                  </div>
                </div>
              </div>

              {/* Session Summary */}
              <div className="card">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Session Summary</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Questions Completed:</span>
                    <span className="ml-2 font-medium">{currentQuestionIndex + 1}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Time Elapsed:</span>
                    <span className="ml-2 font-medium">{formatTime(timeElapsed)}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Remaining:</span>
                    <span className="ml-2 font-medium">{questions.length - currentQuestionIndex - 1}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Average Time per Question:</span>
                    <span className="ml-2 font-medium">
                      {currentQuestionIndex > 0 ? formatTime(Math.round(timeElapsed / (currentQuestionIndex + 1))) : '0:00'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <AcademicCapIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">No Questions Found</h2>
              <p className="text-gray-600 mb-6">
                No questions match your current settings. Try adjusting your filters.
              </p>
              <button
                onClick={() => setPracticeStarted(false)}
                className="btn-primary"
              >
                Adjust Settings
              </button>
            </div>
          )}
        </main>
      </div>
    </>
  )
}
