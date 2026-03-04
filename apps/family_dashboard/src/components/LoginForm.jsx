import { useMemo, useState } from 'react'
import logoImg from '../assets/logo.png'

function UserIcon() {
  return (
    <svg viewBox="0 0 24 24" className="auth-icon" aria-hidden="true">
      <circle cx="12" cy="7" r="4" />
      <path d="M4 20c1.8-4.4 5.1-6.5 8-6.5S18.2 15.6 20 20" />
    </svg>
  )
}

function LockIcon() {
  return (
    <svg viewBox="0 0 24 24" className="auth-icon" aria-hidden="true">
      <rect x="4" y="10" width="16" height="10" rx="2" />
      <path d="M8 10V7a4 4 0 0 1 8 0v3" />
    </svg>
  )
}

function MailIcon() {
  return (
    <svg viewBox="0 0 24 24" className="auth-icon" aria-hidden="true">
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <path d="m3 8 9 6 9-6" />
    </svg>
  )
}

export default function LoginForm({ onLogin, onSignup, loading, error }) {
  const [mode, setMode] = useState('signin')

  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')

  const [suName, setSuName] = useState('')
  const [suUser, setSuUser] = useState('')
  const [suEmail, setSuEmail] = useState('')
  const [suPass, setSuPass] = useState('')
  const [suConfirm, setSuConfirm] = useState('')
  const [localErr, setLocalErr] = useState('')

  const shownError = useMemo(() => localErr || error || '', [localErr, error])

  const submitSignin = (event) => {
    event.preventDefault()
    setLocalErr('')
    onLogin(username.trim(), password)
  }

  const submitSignup = (event) => {
    event.preventDefault()
    setLocalErr('')

    if (!suUser.trim() || !suPass.trim()) {
      setLocalErr('Συμπλήρωσε όνομα χρήστη και κωδικό.')
      return
    }
    if (suPass !== suConfirm) {
      setLocalErr('Οι κωδικοί δεν ταιριάζουν.')
      return
    }

    onSignup({
      username: suUser.trim(),
      password: suPass,
      displayName: suName.trim() || suUser.trim(),
      email: suEmail.trim(),
    })
  }

  return (
    <div className="auth-root">
      <div className="auth-layout">
        <section className="auth-media">
          <div className="auth-media-frame">
            <img src={logoImg} alt="Thalpo" className="auth-media-logo" />
            <div className="auth-media-grid" aria-hidden="true">
              {Array.from({ length: 8 }).map((_, i) => (
                <span key={i} />
              ))}
            </div>
          </div>
          <div className="auth-media-caption">
            <h2>Thalpo</h2>
            <p>Voice that warms.</p>
          </div>
        </section>

        <section className="auth-panel">
          <div className="auth-watermark">Thalpo</div>
          <div className="auth-form-wrap">
            <h1>{mode === 'signin' ? 'Σύνδεση' : 'Εγγραφή'}</h1>

            <div className="auth-toggle">
              <button
                type="button"
                className={mode === 'signin' ? 'active' : ''}
                onClick={() => {
                  setMode('signin')
                  setLocalErr('')
                }}
              >
                Είσοδος
              </button>
              <button
                type="button"
                className={mode === 'signup' ? 'active' : ''}
                onClick={() => {
                  setMode('signup')
                  setLocalErr('')
                }}
              >
                Δημιουργία
              </button>
            </div>

            {mode === 'signin' ? (
              <form className="auth-form" onSubmit={submitSignin}>
                <label>
                  Όνομα χρήστη
                  <div className="auth-input-wrap">
                    <input
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      placeholder="π.χ. areti"
                      autoComplete="username"
                    />
                    <UserIcon />
                  </div>
                </label>

                <label>
                  Κωδικός
                  <div className="auth-input-wrap">
                    <input
                      type="password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Ο κωδικός σου"
                      autoComplete="current-password"
                    />
                    <LockIcon />
                  </div>
                </label>

                {shownError ? <p className="error">{shownError}</p> : null}

                <button type="submit" className="auth-submit" disabled={loading}>
                  {loading ? 'Σύνδεση...' : 'Είσοδος'}
                </button>

                <p className="auth-switch-line">
                  Δεν έχεις λογαριασμό;{' '}
                  <button type="button" className="link-btn" onClick={() => setMode('signup')}>
                    Εγγραφή
                  </button>
                </p>
              </form>
            ) : (
              <form className="auth-form" onSubmit={submitSignup}>
                <label>
                  Ονοματεπώνυμο
                  <div className="auth-input-wrap">
                    <input
                      value={suName}
                      onChange={(e) => setSuName(e.target.value)}
                      placeholder="π.χ. Αρετή Κυρπίτσα"
                    />
                    <UserIcon />
                  </div>
                </label>

                <label>
                  Όνομα χρήστη
                  <div className="auth-input-wrap">
                    <input
                      value={suUser}
                      onChange={(e) => setSuUser(e.target.value)}
                      placeholder="π.χ. areti"
                      required
                    />
                    <UserIcon />
                  </div>
                </label>

                <label>
                  Email
                  <div className="auth-input-wrap">
                    <input
                      value={suEmail}
                      onChange={(e) => setSuEmail(e.target.value)}
                      placeholder="π.χ. areti@email.com"
                      type="email"
                    />
                    <MailIcon />
                  </div>
                </label>

                <label>
                  Κωδικός
                  <div className="auth-input-wrap">
                    <input
                      type="password"
                      value={suPass}
                      onChange={(e) => setSuPass(e.target.value)}
                      placeholder="Νέος κωδικός"
                      required
                    />
                    <LockIcon />
                  </div>
                </label>

                <label>
                  Επιβεβαίωση κωδικού
                  <div className="auth-input-wrap">
                    <input
                      type="password"
                      value={suConfirm}
                      onChange={(e) => setSuConfirm(e.target.value)}
                      placeholder="Επανάληψη κωδικού"
                      required
                    />
                    <LockIcon />
                  </div>
                </label>

                {shownError ? <p className="error">{shownError}</p> : null}

                <button type="submit" className="auth-submit" disabled={loading}>
                  {loading ? 'Δημιουργία...' : 'Εγγραφή'}
                </button>

                <p className="auth-switch-line">
                  Έχεις ήδη λογαριασμό;{' '}
                  <button type="button" className="link-btn" onClick={() => setMode('signin')}>
                    Είσοδος
                  </button>
                </p>
              </form>
            )}
          </div>
        </section>
      </div>
    </div>
  )
}
