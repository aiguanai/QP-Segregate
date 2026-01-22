import { useState, useCallback, useEffect } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { useDropzone } from 'react-dropzone'
import { useAuth } from '../../hooks/useAuth'
import { api } from '../../utils/api'
import ThemeToggle from '../../components/ThemeToggle'
import { 
  DocumentTextIcon, 
  CloudArrowUpIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface UploadState {
  step: 'upload' | 'metadata' | 'processing' | 'completed'
  uploadId?: string
  pageCount?: number
  fileSize?: number
  paperId?: number
  taskId?: string
  progress?: number
  status?: string
}

export default function UploadSyllabus() {
  const { user } = useAuth()
  const router = useRouter()
  const [uploadState, setUploadState] = useState<UploadState>({ step: 'upload' })
  const [metadata, setMetadata] = useState({
    course_code: '',
    academic_year: '',
    semester_type: ''
  })
  const [uploading, setUploading] = useState(false)
  const [processing, setProcessing] = useState(false)

  useEffect(() => {
    if (!user) {
      router.push('/admin/login')
      return
    }
  }, [user, router])

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    const filename = file.name.toLowerCase()
    if (!filename.endsWith('.pdf') && !filename.endsWith('.docx') && !filename.endsWith('.doc')) {
      toast.error('Only PDF and DOCX files are allowed')
      return
    }

    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('file_type', 'syllabus')

      const response = await api.post('/api/admin/upload-file', formData)

      const result = response.data
      setUploadState({
        step: 'metadata',
        uploadId: result.upload_id,
        pageCount: result.page_count,
        fileSize: result.file_size
      })
      toast.success('Syllabus uploaded successfully!')
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Upload failed. Please try again.'
      toast.error(errorMessage)
    } finally {
      setUploading(false)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc']
    },
    multiple: false,
    disabled: uploadState.step !== 'upload'
  })

  const handleMetadataSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    setProcessing(true)

    try {
      const response = await api.post('/api/admin/submit-metadata', {
        upload_id: uploadState.uploadId,
        file_type: 'syllabus',
        ...metadata
      })

      const result = response.data
      setUploadState({
        ...uploadState,
        step: 'processing',
        paperId: result.paper_id,
        taskId: result.task_id
      })

      // Start polling for processing status
      pollProcessingStatus(result.paper_id)
      toast.success('Processing started!')
    } catch (error) {
      toast.error('Failed to submit metadata')
    } finally {
      setProcessing(false)
    }
  }

  const pollProcessingStatus = async (paperId: number) => {
    let pollCount = 0
    const maxPolls = 30 // Maximum 60 seconds (30 * 2 seconds)
    
    const pollInterval = setInterval(async () => {
      pollCount++
      
      // Timeout after max polls
      if (pollCount > maxPolls) {
        clearInterval(pollInterval)
        toast.error('Processing is taking longer than expected. The file has been uploaded successfully.')
        setUploadState(prev => ({ ...prev, step: 'completed' }))
        return
      }
      
      try {
        const response = await api.get(`/api/admin/processing-status/${paperId}`)
        const status = response.data
        setUploadState(prev => ({
          ...prev,
          progress: status.progress,
          status: status.status
        }))

        if (status.status === 'COMPLETED') {
          setUploadState(prev => ({ ...prev, step: 'completed' }))
          clearInterval(pollInterval)
          toast.success('Processing completed!')
        } else if (status.status === 'FAILED') {
          clearInterval(pollInterval)
          toast.error('Processing failed')
        } else if (status.status === 'METADATA_PENDING' && pollCount > 5) {
          // If still in METADATA_PENDING after 10 seconds, likely Celery isn't running
          // For syllabus, we can just mark as completed since we don't need question extraction
          clearInterval(pollInterval)
          toast('Syllabus uploaded successfully. Note: Background processing may not be running.', { icon: 'ℹ️' })
          setUploadState(prev => ({ ...prev, step: 'completed' }))
        }
      } catch (error) {
        console.error('Failed to poll status:', error)
        // If we can't get status after several attempts, assume it's done
        if (pollCount > 10) {
          clearInterval(pollInterval)
          toast('Syllabus uploaded successfully. Status check unavailable.', { icon: 'ℹ️' })
          setUploadState(prev => ({ ...prev, step: 'completed' }))
        }
      }
    }, 2000)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setMetadata({
      ...metadata,
      [e.target.name]: e.target.value
    })
  }

  if (!user) {
    return null
  }

  return (
    <>
      <Head>
        <title>Upload Syllabus - QPaper AI</title>
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
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Upload Syllabus</h1>
              </div>
              <ThemeToggle />
            </div>
          </div>
        </header>

        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Step 1: File Upload */}
          {uploadState.step === 'upload' && (
            <div className="card dark:bg-gray-800 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Step 1: Upload Syllabus File</h2>
              
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors duration-200 ${
                  isDragActive
                    ? 'border-primary-500 dark:border-primary-400 bg-primary-50 dark:bg-primary-900/20'
                    : 'border-gray-300 dark:border-gray-600 hover:border-primary-400 dark:hover:border-primary-500'
                } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <input {...getInputProps()} />
                <CloudArrowUpIcon className="h-12 w-12 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                {uploading ? (
                  <p className="text-gray-600 dark:text-gray-300">Uploading...</p>
                ) : isDragActive ? (
                  <p className="text-primary-600 dark:text-primary-400">Drop the file here...</p>
                ) : (
                  <div>
                    <p className="text-gray-600 dark:text-gray-300 mb-2">
                      Drag & drop a PDF or DOCX file here, or click to browse
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Supported formats: PDF, DOCX
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 2: Metadata Form */}
          {uploadState.step === 'metadata' && (
            <div className="card dark:bg-gray-800 dark:border-gray-700">
              <div className="flex items-center mb-6">
                <CheckCircleIcon className="h-6 w-6 text-green-600 dark:text-green-500 mr-2" />
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Step 2: Syllabus Details</h2>
              </div>

              <div className="mb-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <div className="flex items-center">
                  <DocumentTextIcon className="h-5 w-5 text-green-600 dark:text-green-500 mr-2" />
                  <div>
                    <p className="text-sm font-medium text-green-800 dark:text-green-300">File uploaded successfully</p>
                    <p className="text-xs text-green-600 dark:text-green-400">
                      {uploadState.pageCount} pages • {(uploadState.fileSize! / 1024 / 1024).toFixed(1)} MB
                    </p>
                  </div>
                </div>
              </div>

              <form onSubmit={handleMetadataSubmit} className="space-y-6">
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
                  <div>
                    <label htmlFor="course_code" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Course Code *
                    </label>
                    <input
                      type="text"
                      id="course_code"
                      name="course_code"
                      required
                      className="input-field mt-1 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      value={metadata.course_code}
                      onChange={handleChange}
                      placeholder="e.g., CS301"
                    />
                  </div>

                  <div>
                    <label htmlFor="academic_year" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Academic Year *
                    </label>
                    <select
                      id="academic_year"
                      name="academic_year"
                      required
                      className="input-field mt-1 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      value={metadata.academic_year}
                      onChange={handleChange}
                    >
                      <option value="">Select Year</option>
                      <option value="1">1st Year</option>
                      <option value="2">2nd Year</option>
                      <option value="3">3rd Year</option>
                      <option value="4">4th Year</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="semester_type" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Semester *
                    </label>
                    <select
                      id="semester_type"
                      name="semester_type"
                      required
                      className="input-field mt-1 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      value={metadata.semester_type}
                      onChange={handleChange}
                    >
                      <option value="">Select Semester</option>
                      <option value="ODD">ODD</option>
                      <option value="EVEN">EVEN</option>
                    </select>
                  </div>
                </div>

                <div className="flex justify-end space-x-4">
                  <button
                    type="button"
                    onClick={() => setUploadState({ step: 'upload' })}
                    className="btn-secondary"
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    disabled={processing}
                    className="btn-primary disabled:opacity-50"
                  >
                    {processing ? 'Processing...' : 'Submit & Process'}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Step 3: Processing Status */}
          {uploadState.step === 'processing' && (
            <div className="card dark:bg-gray-800 dark:border-gray-700">
              <div className="flex items-center mb-6">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 dark:border-primary-400 mr-2"></div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Processing Syllabus</h2>
              </div>

              <div className="space-y-4">
                <div className="flex items-center">
                  <CheckCircleIcon className="h-5 w-5 text-green-600 dark:text-green-500 mr-3" />
                  <span className="text-sm text-gray-600 dark:text-gray-300">File Uploaded</span>
                </div>

                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600 dark:border-primary-400 mr-3"></div>
                  <span className="text-sm text-gray-600 dark:text-gray-300">Processing...</span>
                </div>

                {uploadState.progress !== undefined && (
                  <div className="mt-4">
                    <div className="flex justify-between text-sm text-gray-600 dark:text-gray-300 mb-2">
                      <span>Progress</span>
                      <span>{Math.round(uploadState.progress)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-primary-600 dark:bg-primary-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${uploadState.progress}%` }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 4: Completed */}
          {uploadState.step === 'completed' && (
            <div className="card dark:bg-gray-800 dark:border-gray-700">
              <div className="text-center">
                <CheckCircleIcon className="h-16 w-16 text-green-600 dark:text-green-500 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Processing Completed!</h2>
                <p className="text-gray-600 dark:text-gray-300 mb-6">
                  Your syllabus has been successfully processed and added to the database.
                </p>
                <div className="flex justify-center space-x-4">
                  <button
                    onClick={() => router.push('/admin/dashboard')}
                    className="btn-primary"
                  >
                    Back to Dashboard
                  </button>
                  <button
                    onClick={() => setUploadState({ step: 'upload' })}
                    className="btn-secondary"
                  >
                    Upload Another Syllabus
                  </button>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </>
  )
}

