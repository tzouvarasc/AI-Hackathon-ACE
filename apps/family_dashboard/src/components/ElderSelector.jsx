import { useMemo, useState } from 'react'
import logoImg from '../assets/logo.png'

function PhoneIcon() {
  return (
    <svg viewBox="0 0 24 24" className="field-icon" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
      <rect x="5" y="2" width="14" height="20" rx="3" />
      <circle cx="12" cy="17" r="1" fill="currentColor" stroke="none" />
    </svg>
  )
}

function UserIcon() {
  return (
    <svg viewBox="0 0 24 24" className="field-icon" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
      <circle cx="12" cy="7" r="4" />
      <path d="M4 20c1.8-4.4 5.1-6.5 8-6.5s6.2 2.1 8 6.5" />
    </svg>
  )
}

function getInitials(name) {
  if (!name) return '?'
  return name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

const AVATAR_COLORS = [
  ['#a41623', '#fdf0d5'],
  ['#003049', '#669bbc'],
  ['#669bbc', '#003049'],
  ['#780000', '#fdf0d5'],
  ['#d97706', '#1a2c44'],
]

export default function ElderSelector({
  profile,
  elders,
  selectedId,
  onSelect,
  onAdd,
  onRemove,
  onLogout,
}) {
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const canAdd = useMemo(() => name.trim() && phone.trim(), [name, phone])

  const submitAdd = (event) => {
    event.preventDefault()
    if (!canAdd) return
    onAdd({ name: name.trim(), elderlyId: phone.trim() })
    setName('')
    setPhone('')
  }

  return (
    <div className="selector-shell">
      {/* decorative blobs */}
      <div className="selector-blob selector-blob-1" aria-hidden="true" />
      <div className="selector-blob selector-blob-2" aria-hidden="true" />

      {/* ── header ── */}
      <header className="selector-header">
        <div className="selector-brand">
          <img src={logoImg} alt="Thalpo" className="selector-logo-img" />
          <div className="selector-brand-text">
            <h1>Καλωσήρθες, <span className="brand-accent">{profile?.display_name || 'Φροντιστή'}</span>!</h1>
            <p>Επίλεξε ηλικιωμένο για να δεις κλινική εικόνα, τάσεις και ειδοποιήσεις.</p>
          </div>
        </div>
        <div className="selector-header-actions">
          <span className="elder-count-badge">{elders.length} ηλικιωμένοι</span>
          <button className="signout-pill" onClick={onLogout}>Αποσύνδεση</button>
        </div>
      </header>

      {/* ── divider ── */}
      <div className="selector-section-label">
        <span>Ηλικιωμένοι σου</span>
        <div className="section-line" />
      </div>

      {/* ── elder cards ── */}
      <section className="elder-card-grid">
        {elders.map((elder, idx) => {
          const [bg, fg] = AVATAR_COLORS[idx % AVATAR_COLORS.length]
          const isActive = selectedId === elder.id
          return (
            <div
              key={elder.id}
              className={`elder-select-card ${isActive ? 'active' : ''}`}
            >
              <button type="button" className="elder-main-hit" onClick={() => onSelect(elder)}>
                <span
                  className="elder-avatar-initials"
                  style={{ background: bg, color: fg }}
                >
                  {getInitials(elder.name || elder.label || elder.elderlyId)}
                </span>
                <div className="elder-card-body">
                  <span className="elder-name">{elder.name || elder.label || elder.elderlyId}</span>
                  <span className="elder-sub">{elder.elderlyId}</span>
                </div>
                <span className={`elder-status-dot ${isActive ? 'active' : ''}`} />
              </button>
              <button
                type="button"
                className="elder-remove"
                onClick={() => onRemove(elder.id)}
                aria-label={`Διαγραφή ${elder.name || elder.elderlyId}`}
              >
                ✕
              </button>
            </div>
          )
        })}
      </section>

      {/* ── add elder ── */}
      <div className="selector-section-label" style={{ marginTop: 40 }}>
        <span>Προσθήκη ηλικιωμένου</span>
        <div className="section-line" />
      </div>

      <section className="elder-add-panel">
        <form className="elder-add-form" onSubmit={submitAdd}>
          <label className="add-field-label">
            <span>Ονοματεπώνυμο</span>
            <div className="add-input-wrap">
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="π.χ. Μαρία Γεωργίου"
              />
              <UserIcon />
            </div>
          </label>

          <label className="add-field-label">
            <span>Τηλέφωνο</span>
            <div className="add-input-wrap">
              <input
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="π.χ. +30 697 000 0000"
                type="tel"
              />
              <PhoneIcon />
            </div>
          </label>

          <button type="submit" className="add-submit-btn" disabled={!canAdd}>
            <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18" aria-hidden="true">
              <path d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" />
            </svg>
            Προσθήκη
          </button>
        </form>
      </section>
    </div>
  )
}
