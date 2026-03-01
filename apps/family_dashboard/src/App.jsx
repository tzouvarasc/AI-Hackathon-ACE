import { useEffect, useState } from 'react'
import DashboardView from './components/DashboardView'
import LoginForm from './components/LoginForm'
import { getDashboard, getHistory, getInsights, login, me } from './api'

const STORAGE_KEY = 'thalpo_dashboard_auth'

export default function App() {
  const [token, setToken] = useState(localStorage.getItem(STORAGE_KEY) || '')
  const [profile, setProfile] = useState(null)
  const [elderlyId, setElderlyId] = useState('demo-user')
  const [snapshot, setSnapshot] = useState(null)
  const [history, setHistory] = useState([])
  const [insights, setInsights] = useState(null)
  const [loading, setLoading] = useState(false)
  const [authLoading, setAuthLoading] = useState(false)
  const [error, setError] = useState('')

  const loadProfile = async (activeToken) => {
    const data = await me(activeToken)
    setProfile(data)
  }

  const refreshDashboard = async () => {
    if (!token || !elderlyId.trim()) {
      return
    }

    setLoading(true)
    setError('')
    try {
      const [dashboard, timeline, insightReport] = await Promise.all([
        getDashboard(elderlyId, token),
        getHistory(elderlyId, token, 20),
        getInsights(elderlyId, token, 30)
      ])
      setSnapshot(dashboard)
      setHistory(timeline)
      setInsights(insightReport)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!token) {
      setProfile(null)
      setSnapshot(null)
      setHistory([])
      setInsights(null)
      return
    }

    loadProfile(token).catch((err) => {
      setError(err.message)
      setToken('')
      localStorage.removeItem(STORAGE_KEY)
    })
  }, [token])

  useEffect(() => {
    if (profile) {
      refreshDashboard()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [profile, elderlyId])

  const onLogin = async (username, password) => {
    setAuthLoading(true)
    setError('')
    try {
      const response = await login(username, password)
      localStorage.setItem(STORAGE_KEY, response.access_token)
      setToken(response.access_token)
    } catch (err) {
      setError(err.message)
    } finally {
      setAuthLoading(false)
    }
  }

  const onLogout = () => {
    localStorage.removeItem(STORAGE_KEY)
    setToken('')
    setProfile(null)
    setSnapshot(null)
    setHistory([])
    setInsights(null)
  }

  if (!token || !profile) {
    return <LoginForm onLogin={onLogin} loading={authLoading} error={error} />
  }

  return (
    <DashboardView
      profile={profile}
      elderlyId={elderlyId}
      setElderlyId={setElderlyId}
      snapshot={snapshot}
      history={history}
      insights={insights}
      loading={loading}
      error={error}
      onRefresh={refreshDashboard}
      onLogout={onLogout}
    />
  )
}
