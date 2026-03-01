import { useState } from 'react'

export default function LoginForm({ onLogin, loading, error }) {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')

  const submit = (event) => {
    event.preventDefault()
    onLogin(username, password)
  }

  return (
    <div className="login-shell">
      <div className="login-card">
        <p className="eyebrow">THALPO</p>
        <h1>Family Care Console</h1>
        <p className="subtext">Securely monitor cognitive and emotional trends.</p>

        <form onSubmit={submit} className="login-form">
          <label>
            Username
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </label>

          <button type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {error ? <p className="error">{error}</p> : null}
      </div>
    </div>
  )
}
