import { useState } from 'react'
import Head from 'next/head'
import { AcademicCapIcon, DocumentTextIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline'

const themes = {
  'Academic Blue (Current)': {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      200: '#bfdbfe',
      300: '#93c5fd',
      400: '#60a5fa',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
      800: '#1e40af',
      900: '#1e3a8a',
    },
  },
  'Emerald Green': {
    primary: {
      50: '#ecfdf5',
      100: '#d1fae5',
      200: '#a7f3d0',
      300: '#6ee7b7',
      400: '#34d399',
      500: '#10b981',
      600: '#059669',
      700: '#047857',
      800: '#065f46',
      900: '#064e3b',
    },
  },
  'Purple': {
    primary: {
      50: '#faf5ff',
      100: '#f3e8ff',
      200: '#e9d5ff',
      300: '#d8b4fe',
      400: '#c084fc',
      500: '#a855f7',
      600: '#9333ea',
      700: '#7e22ce',
      800: '#6b21a8',
      900: '#581c87',
    },
  },
  'Indigo': {
    primary: {
      50: '#eef2ff',
      100: '#e0e7ff',
      200: '#c7d2fe',
      300: '#a5b4fc',
      400: '#818cf8',
      500: '#6366f1',
      600: '#4f46e5',
      700: '#4338ca',
      800: '#3730a3',
      900: '#312e81',
    },
  },
  'Orange/Amber': {
    primary: {
      50: '#fffbeb',
      100: '#fef3c7',
      200: '#fde68a',
      300: '#fcd34d',
      400: '#fbbf24',
      500: '#f59e0b',
      600: '#d97706',
      700: '#b45309',
      800: '#92400e',
      900: '#78350f',
    },
  },
  'Rose/Pink': {
    primary: {
      50: '#fff1f2',
      100: '#ffe4e6',
      200: '#fecdd3',
      300: '#fda4af',
      400: '#fb7185',
      500: '#f43f5e',
      600: '#e11d48',
      700: '#be123c',
      800: '#9f1239',
      900: '#881337',
    },
  },
  'Teal/Cyan': {
    primary: {
      50: '#f0fdfa',
      100: '#ccfbf1',
      200: '#99f6e4',
      300: '#5eead4',
      400: '#2dd4bf',
      500: '#14b8a6',
      600: '#0d9488',
      700: '#0f766e',
      800: '#115e59',
      900: '#134e4a',
    },
  },
}

export default function ThemePreview() {
  const [selectedTheme, setSelectedTheme] = useState<string | null>(null)

  const ThemeCard = ({ themeName, colors }: { themeName: string; colors: any }) => {
    const primary = colors.primary
    const isSelected = selectedTheme === themeName

    return (
      <div
        className={`border-2 rounded-lg p-6 cursor-pointer transition-all bg-white ${
          isSelected ? 'border-primary-600 shadow-lg scale-105' : 'border-gray-200 hover:border-gray-300'
        }`}
        onClick={() => setSelectedTheme(themeName)}
      >
        <h3 className="text-xl font-bold mb-4">{themeName}</h3>
        
        {/* Color Swatches */}
        <div className="grid grid-cols-5 gap-2 mb-6">
          {[50, 100, 500, 600, 700].map((shade) => (
            <div key={shade} className="text-center">
              <div
                className="w-full h-12 rounded-md mb-1 border border-gray-200"
                style={{ backgroundColor: primary[shade] }}
              />
              <p className="text-xs text-gray-600">{shade}</p>
            </div>
          ))}
        </div>

        {/* UI Preview */}
        <div className="space-y-3">
          {/* Button */}
          <button
            className="w-full py-2 px-4 rounded-lg text-white font-medium transition-colors"
            style={{ backgroundColor: primary[600] }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = primary[700])}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = primary[600])}
          >
            Primary Button
          </button>

          {/* Card */}
          <div
            className="p-4 rounded-lg border"
            style={{
              backgroundColor: primary[50],
              borderColor: primary[200],
            }}
          >
            <div className="flex items-center mb-2">
              <AcademicCapIcon className="h-6 w-6 mr-2" style={{ color: primary[600] }} />
              <h4 className="font-semibold" style={{ color: primary[900] }}>
                Sample Card
              </h4>
            </div>
            <p className="text-sm" style={{ color: primary[700] }}>
              This is how content looks with this theme
            </p>
          </div>

          {/* Badge */}
          <div className="flex items-center space-x-2">
            <span
              className="px-3 py-1 rounded-full text-xs font-medium text-white"
              style={{ backgroundColor: primary[500] }}
            >
              Badge
            </span>
            <span
              className="px-3 py-1 rounded-full text-xs font-medium"
              style={{ backgroundColor: primary[100], color: primary[800] }}
            >
              Light Badge
            </span>
          </div>
        </div>

        {isSelected && (
          <div className="mt-4 p-3 rounded bg-green-50 border border-green-200">
            <p className="text-sm text-green-800 font-medium">✓ Selected</p>
          </div>
        )}
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>Theme Preview - QPaper AI</title>
      </Head>

      <div className="min-h-screen bg-gray-50 py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Color Theme Preview</h1>
            <p className="text-gray-600">Click on any theme to select it and view the color codes</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {Object.entries(themes).map(([themeName, colors]) => (
              <ThemeCard key={themeName} themeName={themeName} colors={colors} />
            ))}
          </div>

          {selectedTheme && (
            <div className="mt-12 p-6 bg-white rounded-lg shadow-lg border-2 border-primary-600">
              <h2 className="text-2xl font-bold mb-4">Selected: {selectedTheme}</h2>
              <p className="text-gray-600 mb-4">
                To apply this theme, update the <code className="bg-gray-100 px-2 py-1 rounded">tailwind.config.js</code> file
                with the colors shown below.
              </p>
              <div className="bg-gray-900 rounded p-4 overflow-x-auto">
                <pre className="text-green-400 text-sm">
                  {JSON.stringify(themes[selectedTheme as keyof typeof themes], null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

