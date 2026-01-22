import { useRouter } from 'next/router'
import Head from 'next/head'
import { HomeIcon, ArrowLeftIcon } from '@heroicons/react/24/outline'
import ThemeToggle from '../components/ThemeToggle'

export default function Custom404() {
  const router = useRouter()

  return (
    <>
      <Head>
        <title>404 - Page Not Found</title>
      </Head>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="mb-8">
            <ThemeToggle />
          </div>
          <h1 className="text-9xl font-bold text-primary-600 dark:text-primary-400 mb-4">404</h1>
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            Page Not Found
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-8">
            The page you're looking for doesn't exist or has been moved.
          </p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={() => router.back()}
              className="btn-secondary flex items-center"
            >
              <ArrowLeftIcon className="h-5 w-5 mr-2" />
              Go Back
            </button>
            <button
              onClick={() => router.push('/')}
              className="btn-primary flex items-center"
            >
              <HomeIcon className="h-5 w-5 mr-2" />
              Go Home
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

