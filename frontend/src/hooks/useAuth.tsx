import { useState, useEffect, createContext, useContext } from 'react'
import { useRouter } from 'next/router'
import toast from 'react-hot-toast'
import { api } from '../utils/api'

interface User {
  user_id: number
  username: string
  email: string
  role: string
  branch_id?: number
  academic_year?: number
}

interface AuthContextType {
  user: User | null
  login: (username: string, password: string, role?: string) => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem('token')
    if (token) {
      // Verify token and get user info
      verifyToken()
    } else {
      setLoading(false)
    }
  }, [])

  const verifyToken = async () => {
    try {
      const response = await api.get('/api/auth/me')
      setUser(response.data)
    } catch (error) {
      localStorage.removeItem('token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (username: string, password: string, role?: string) => {
    setLoading(true)
    try {
      // OAuth2PasswordRequestForm expects URL-encoded form data
      const params = new URLSearchParams()
      params.append('username', username)
      params.append('password', password)

      const response = await api.post('/api/auth/login', params.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })

      const { access_token } = response.data
      localStorage.setItem('token', access_token)

      // Get user info
      const userResponse = await api.get('/api/auth/me')
      setUser(userResponse.data)
      toast.success('Login successful!')
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Login failed'
      throw new Error(message)
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
    toast.success('Logged out successfully')
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
