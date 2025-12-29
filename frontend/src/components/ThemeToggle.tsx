import { useState } from 'react'
import { useTheme } from '../hooks/useTheme'
import { SunIcon, MoonIcon, ComputerDesktopIcon } from '@heroicons/react/24/outline'

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        aria-label="Toggle theme"
      >
        {theme === 'light' && <SunIcon className="h-5 w-5 text-gray-700 dark:text-gray-300" />}
        {theme === 'dark' && <MoonIcon className="h-5 w-5 text-gray-700 dark:text-gray-300" />}
        {theme === 'system' && <ComputerDesktopIcon className="h-5 w-5 text-gray-700 dark:text-gray-300" />}
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">{theme}</span>
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-20 py-1">
            <button
              onClick={() => {
                setTheme('light')
                setIsOpen(false)
              }}
              className={`w-full flex items-center space-x-3 px-4 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                theme === 'light' ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400' : 'text-gray-700 dark:text-gray-300'
              }`}
            >
              <SunIcon className="h-5 w-5" />
              <span>Light</span>
              {theme === 'light' && <span className="ml-auto">✓</span>}
            </button>
            <button
              onClick={() => {
                setTheme('dark')
                setIsOpen(false)
              }}
              className={`w-full flex items-center space-x-3 px-4 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                theme === 'dark' ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400' : 'text-gray-700 dark:text-gray-300'
              }`}
            >
              <MoonIcon className="h-5 w-5" />
              <span>Dark</span>
              {theme === 'dark' && <span className="ml-auto">✓</span>}
            </button>
            <button
              onClick={() => {
                setTheme('system')
                setIsOpen(false)
              }}
              className={`w-full flex items-center space-x-3 px-4 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                theme === 'system' ? 'bg-primary-50 dark:bg-primary-900/20 text-primary-600 dark:text-primary-400' : 'text-gray-700 dark:text-gray-300'
              }`}
            >
              <ComputerDesktopIcon className="h-5 w-5" />
              <span>System</span>
              {theme === 'system' && <span className="ml-auto">✓</span>}
            </button>
          </div>
        </>
      )}
    </div>
  )
}

