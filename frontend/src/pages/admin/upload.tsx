import { useState, useCallback } from 'react'
import Head from 'next/head'
import { useRouter } from 'next/router'
import { useDropzone } from 'react-dropzone'
import { useAuth } from '../../hooks/useAuth'
import { 
  DocumentTextIcon, 
  CloudArrowUpIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
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

export default function AdminUpload() {
  const { user } = useAuth()
  const router = useRouter()
  const [uploadState, setUploadState] = useState<UploadState>({ step: 'upload' })
  const [metadata, setMetadata] = useState({
    course_code: '',
    academic_year: '',
    semester_type: '',
    exam_type: '',
    exam_date: ''
  })
  const [uploading, setUploading] = useState(false)
  const [processing, setProcessing] = useState(false)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return

    const file = acceptedFiles[0]
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      toast.error('Only PDF files are allowed')
      return
    }

    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('/api/admin/upload-pdf', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const result = await response.json()
      setUploadState({
        step: 'metadata',
        uploadId: result.upload_id,
        pageCount: result.page_count,
        fileSize: result.file_size
      })
      toast.success('PDF uploaded successfully!')
    } catch (error) {
      toast.error('Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false,
    disabled: uploadState.step !== 'upload'
  })

  const handleMetadataSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setProcessing(true)

    try {
      const response = await fetch('/api/admin/submit-metadata', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          upload_id: uploadState.uploadId,
          ...metadata
        })
      })

      if (!response.ok) {
        throw new Error('Metadata submission failed')
      }

      const result = await response.json()
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
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/admin/processing-status/${paperId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        })

        if (!response.ok) return

        const status = await response.json()
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
        }
      } catch (error) {
        console.error('Failed to poll status:', error)
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
    router.push('/admin/login')
    return null
  }

  return (
    <>
      <Head>
        <title>Upload Question Paper - QPaper AI</title>
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
                <h1 className="text-2xl font-bold text-gray-900">Upload Question Paper</h1>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Step 1: PDF Upload */}
          {uploadState.step === 'upload' && (
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Step 1: Upload PDF</h2>
              
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors duration-200 ${
                  isDragActive
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-300 hover:border-primary-400'
                } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <input {...getInputProps()} />
                <CloudArrowUpIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                {uploading ? (
                  <p className="text-gray-600">Uploading...</p>
                ) : isDragActive ? (
                  <p className="text-primary-600">Drop the PDF here...</p>
                ) : (
                  <div>
                    <p className="text-gray-600 mb-2">
                      Drag & drop a PDF file here, or click to browse
                    </p>
                    <p className="text-sm text-gray-500">
                      Only PDF files are supported
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 2: Metadata Form */}
          {uploadState.step === 'metadata' && (
            <div className="card">
              <div className="flex items-center mb-6">
                <CheckCircleIcon className="h-6 w-6 text-green-600 mr-2" />
                <h2 className="text-lg font-semibold text-gray-900">Step 2: Paper Details</h2>
              </div>

              <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center">
                  <DocumentTextIcon className="h-5 w-5 text-green-600 mr-2" />
                  <div>
                    <p className="text-sm font-medium text-green-800">PDF uploaded successfully</p>
                    <p className="text-xs text-green-600">
                      {uploadState.pageCount} pages • {(uploadState.fileSize! / 1024 / 1024).toFixed(1)} MB
                    </p>
                  </div>
                </div>
              </div>

              <form onSubmit={handleMetadataSubmit} className="space-y-6">
                <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                  <div>
                    <label htmlFor="course_code" className="block text-sm font-medium text-gray-700">
                      Course Code *
                    </label>
                    <select
                      id="course_code"
                      name="course_code"
                      required
                      className="input-field mt-1"
                      value={metadata.course_code}
                      onChange={handleChange}
                    >
                      <option value="">Select Course</option>
                      <option value="CS301">CS301 - Database Management Systems</option>
                      <option value="CS302">CS302 - Computer Networks</option>
                      <option value="CS303">CS303 - Software Engineering</option>
                      <option value="MA201">MA201 - Mathematics</option>
                      <option value="EC301">EC301 - Digital Electronics</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="academic_year" className="block text-sm font-medium text-gray-700">
                      Academic Year *
                    </label>
                    <select
                      id="academic_year"
                      name="academic_year"
                      required
                      className="input-field mt-1"
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
                    <label htmlFor="semester_type" className="block text-sm font-medium text-gray-700">
                      Semester *
                    </label>
                    <select
                      id="semester_type"
                      name="semester_type"
                      required
                      className="input-field mt-1"
                      value={metadata.semester_type}
                      onChange={handleChange}
                    >
                      <option value="">Select Semester</option>
                      <option value="ODD">ODD</option>
                      <option value="EVEN">EVEN</option>
                    </select>
                  </div>

                  <div>
                    <label htmlFor="exam_type" className="block text-sm font-medium text-gray-700">
                      Exam Type *
                    </label>
                    <select
                      id="exam_type"
                      name="exam_type"
                      required
                      className="input-field mt-1"
                      value={metadata.exam_type}
                      onChange={handleChange}
                    >
                      <option value="">Select Exam Type</option>
                      <option value="CIE 1">CIE 1 (Continuous Internal Evaluation 1)</option>
                      <option value="CIE 2">CIE 2 (Continuous Internal Evaluation 2)</option>
                      <option value="Improvement CIE">Improvement CIE (Re-test for CIE)</option>
                      <option value="SEE">SEE (Semester End Examination)</option>
                    </select>
                  </div>

                  <div className="sm:col-span-2">
                    <label htmlFor="exam_date" className="block text-sm font-medium text-gray-700">
                      Exam Date (Optional)
                    </label>
                    <input
                      type="date"
                      id="exam_date"
                      name="exam_date"
                      className="input-field mt-1"
                      value={metadata.exam_date}
                      onChange={handleChange}
                    />
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
            <div className="card">
              <div className="flex items-center mb-6">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mr-2"></div>
                <h2 className="text-lg font-semibold text-gray-900">Processing Question Paper</h2>
              </div>

              <div className="space-y-4">
                <div className="flex items-center">
                  <CheckCircleIcon className="h-5 w-5 text-green-600 mr-3" />
                  <span className="text-sm text-gray-600">PDF Uploaded</span>
                </div>

                <div className="flex items-center">
                  <CheckCircleIcon className="h-5 w-5 text-green-600 mr-3" />
                  <span className="text-sm text-gray-600">OCR Extraction</span>
                </div>

                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600 mr-3"></div>
                  <span className="text-sm text-gray-600">Classifying Questions...</span>
                </div>

                <div className="flex items-center">
                  <div className="h-5 w-5 border-2 border-gray-300 rounded mr-3"></div>
                  <span className="text-sm text-gray-600">Duplicate Detection Pending</span>
                </div>

                {uploadState.progress !== undefined && (
                  <div className="mt-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-2">
                      <span>Progress</span>
                      <span>{Math.round(uploadState.progress)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary-600 h-2 rounded-full transition-all duration-300"
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
            <div className="card">
              <div className="text-center">
                <CheckCircleIcon className="h-16 w-16 text-green-600 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Processing Completed!</h2>
                <p className="text-gray-600 mb-6">
                  Your question paper has been successfully processed and added to the database.
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
                    Upload Another Paper
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
