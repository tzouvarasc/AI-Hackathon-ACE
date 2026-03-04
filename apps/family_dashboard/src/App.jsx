import { useEffect, useState } from 'react'
import DashboardView from './components/DashboardView'
import LoginForm from './components/LoginForm'
import ElderSelector from './components/ElderSelector'
import { getDashboard, getHistory, getInsights, login, me } from './api'

const STORAGE_KEY = 'thalpo_dashboard_auth'

// Elders are stored per user account
const elderKey = (profile) =>
  `thalpo_elders_${profile?.username || profile?.display_name || 'default'}`

export default function App() {
  const [token, setToken]               = useState(localStorage.getItem(STORAGE_KEY) || '')
  const [profile, setProfile]           = useState(null)
  const [elders, setElders]             = useState([])
  const [selectedElder, setSelectedElder] = useState(null)
  const [elderlyId, setElderlyId]       = useState('')
  const [snapshot, setSnapshot]         = useState(null)
  const [history, setHistory]           = useState([])
  const [insights, setInsights]         = useState(null)
  const [loading, setLoading]           = useState(false)
  const [authLoading, setAuthLoading]   = useState(false)
  const [error, setError]               = useState('')

  /* ── load elders when profile is ready ────────────── */
  useEffect(() => {
    if (profile) {
      try {
        const saved = JSON.parse(localStorage.getItem(elderKey(profile)) || '[]')
        setElders(saved)
      } catch {
        setElders([])
      }
    } else {
      setElders([])
    }
  }, [profile])

  /* ── elder management ──────────────────────────────── */
  const saveElders = (list) => {
    if (!profile) return
    localStorage.setItem(elderKey(profile), JSON.stringify(list))
    setElders(list)
  }

  const addElder = (data) => {
    saveElders([...elders, { ...data, id: crypto.randomUUID() }])
  }

  const removeElder = (id) => {
    saveElders(elders.filter((e) => e.id !== id))
    if (selectedElder?.id === id) setSelectedElder(null)
  }

  const onSelectElder = (elder) => {
    setSelectedElder(elder)
    setElderlyId(elder.elderlyId || elder.phone.replace(/\D/g, ''))
  }

  const onBackToElders = () => {
    setSelectedElder(null)
    setSnapshot(null)
    setHistory([])
    setInsights(null)
    setError('')
  }

  /* ── auth ──────────────────────────────────────────── */
  const loadProfile = async (activeToken) => {
    const data = await me(activeToken)
    setProfile(data)
  }

  const refreshDashboard = async () => {
    if (!token || !elderlyId.trim()) return
    setLoading(true)
    setError('')
    try {
      const [dashboard, timeline, insightReport] = await Promise.all([
        getDashboard(elderlyId, token),
        getHistory(elderlyId, token, 20),
        getInsights(elderlyId, token, 30),
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

  // Initial load when elder selected
  useEffect(() => {
    if (profile && selectedElder) refreshDashboard()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [profile, selectedElder, elderlyId])

  // Auto-refresh every 2 minutes while viewing a dashboard
  useEffect(() => {
    if (!profile || !selectedElder) return
    const interval = setInterval(() => {
      refreshDashboard()
    }, 2 * 60 * 1000)
    return () => clearInterval(interval)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [profile, selectedElder, elderlyId])

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
    setSelectedElder(null)
    setSnapshot(null)
    setHistory([])
    setInsights(null)
  }

  /* ── routing ───────────────────────────────────────── */
  if (!token || !profile) {
    return <LoginForm onLogin={onLogin} loading={authLoading} error={error} />
  }

  if (!selectedElder) {
    return (
      <ElderSelector
        profile={profile}
        elders={elders}
        onSelect={onSelectElder}
        onAdd={addElder}
        onRemove={removeElder}
        onLogout={onLogout}
      />
    )
  }

  return (
    <DashboardView
      profile={profile}
      elderName={selectedElder.name}
      elderlyId={elderlyId}
      setElderlyId={setElderlyId}
      snapshot={snapshot}
      history={history}
      insights={insights}
      loading={loading}
      error={error}
      onRefresh={refreshDashboard}
      onLogout={onLogout}
      onBack={onBackToElders}
    />
  )
}
