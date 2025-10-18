import { useState } from 'react'
import { useRouter } from 'next/router'
import Head from 'next/head'
import { DocumentTextIcon, AcademicCapIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'

export default function Home() {
  const router = useRouter()
  const [userType, setUserType] = useState<'admin' | 'student' | null>(null)

  const handleLogin = (type: 'admin' | 'student') => {
    setUserType(type)
    router.push(`/${type}/login`)
  }

  return (
    <>
      <Head>
        <title>QPaper AI - Automated Question Paper Management</title>
        <meta name="description" content="Intelligent question paper extraction, classification, and management system" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
        {/* Header */}
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div className="flex items-center">
                <AcademicCapIcon className="h-8 w-8 text-primary-600" />
                <h1 className="ml-2 text-2xl font-bold text-gray-900">QPaper AI</h1>
              </div>
              <div className="flex space-x-4">
                <button
                  onClick={() => handleLogin('admin')}
                  className="btn-primary"
                >
                  Admin Login
                </button>
                <button
                  onClick={() => handleLogin('student')}
                  className="btn-secondary"
                >
                  Student Login
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <h2 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
              Automated Question Paper
              <span className="text-primary-600"> Management</span>
            </h2>
            <p className="mt-6 text-xl text-gray-600 max-w-3xl mx-auto">
              Extract, classify, and organize university question papers using AI-powered OCR, 
              NLP, and machine learning technologies.
            </p>
          </div>

          {/* Features */}
          <div className="mt-16 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            <div className="card text-center">
              <DocumentTextIcon className="h-12 w-12 text-primary-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Extraction</h3>
              <p className="text-gray-600">
                Automatically extract questions from scanned PDFs using advanced OCR technology
              </p>
            </div>

            <div className="card text-center">
              <AcademicCapIcon className="h-12 w-12 text-primary-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Intelligent Classification</h3>
              <p className="text-gray-600">
                Classify questions by unit, Bloom taxonomy level, and difficulty automatically
              </p>
            </div>

            <div className="card text-center">
              <MagnifyingGlassIcon className="h-12 w-12 text-primary-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Semantic Search</h3>
              <p className="text-gray-600">
                Find similar questions and detect duplicates using AI-powered similarity matching
              </p>
            </div>
          </div>

          {/* CTA Section */}
          <div className="mt-16 text-center">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Ready to get started?
            </h3>
            <p className="text-gray-600 mb-8">
              Choose your role to access the system
            </p>
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => handleLogin('admin')}
                className="btn-primary text-lg px-8 py-3"
              >
                Admin Portal
              </button>
              <button
                onClick={() => handleLogin('student')}
                className="btn-secondary text-lg px-8 py-3"
              >
                Student Portal
              </button>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-secondary-200 mt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center text-gray-600">
              <p>&copy; 2024 QPaper AI. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </div>
    </>
  )
}
