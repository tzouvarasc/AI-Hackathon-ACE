import { useState } from 'react'
import logoImg from '../assets/logo.png'

/* Simple person-outline SVG icon (matches mockup) */
function PersonIcon() {
  return (
    <svg viewBox="0 0 64 64" width="44" height="44" fill="none">
      <circle cx="32" cy="22" r="12" stroke="#FDF0D5" strokeWidth="2.5" />
      <path
        d="M10 56c0-12.15 9.85-22 22-22s22 9.85 22 22"
        stroke="#FDF0D5"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
    </svg>
  )
}

export default function ElderSelector({
  profile,
  elders,
  onSelect,
  onAdd,
  onRemove,
  onLogout,
}) {
  const [showForm, setShowForm] = useState(false)
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [phone, setPhone] = useState('')
  const [gender, setGender] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!firstName.trim() || !lastName.trim() || !phone.trim() || !gender)
      return
    const fullName = `${firstName.trim()} ${lastName.trim()}`
    onAdd({
      name: fullName,
      firstName: firstName.trim(),
      lastName: lastName.trim(),
      phone: phone.trim(),
      gender,
      elderlyId: phone.trim().replace(/\D/g, ''),
    })
    setFirstName('')
    setLastName('')
    setPhone('')
    setGender('')
    setShowForm(false)
  }

  const handleCancel = () => {
    setFirstName('')
    setLastName('')
    setPhone('')
    setGender('')
    setShowForm(false)
  }

  return (
    <div className="es-shell">
      {/* ── Header ── */}
      <header className="es-header">
        <div className="es-brand">
          <img src={logoImg} alt="Thalpo" className="es-logo" />
          <span className="es-brand-name">Thalpo</span>
        </div>

        <button className="es-signout" onClick={onLogout}>
          Sign Out
        </button>
      </header>

      {/* ── Main ── */}
      <main className="es-main">
        <div className="es-intro">
          <h2 className="es-welcome">Welcome!</h2>
          <p className="es-subtitle">Select dashboard</p>
        </div>

        {/* Elder cards */}
        <div className="es-grid">
          {elders.map((elder) => (
            <div
              key={elder.id}
              className="es-card"
              onClick={() => onSelect(elder)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && onSelect(elder)}
            >
              <button
                className="es-card-remove"
                title="Remove"
                onClick={(ev) => {
                  ev.stopPropagation()
                  if (window.confirm(`Remove "${elder.name}"?`))
                    onRemove(elder.id)
                }}
              >
                ✕
              </button>
              <div className="es-avatar">
                <PersonIcon />
              </div>
              <span className="es-card-name">{elder.name}</span>
            </div>
          ))}

          {/* Add card */}
          {!showForm && (
            <div
              className="es-card es-add-card"
              onClick={() => setShowForm(true)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && setShowForm(true)}
            >
              <div className="es-avatar es-add-icon">＋</div>
              <span className="es-card-name">Προσθήκη</span>
            </div>
          )}
        </div>

        {/* Add form */}
        {showForm && (
          <form className="es-add-form" onSubmit={handleSubmit}>
            <h3>Νέος ηλικιωμένος</h3>

            <div className="es-gender-row">
              <button
                type="button"
                className={`es-gender-btn${gender === 'male' ? ' selected' : ''}`}
                onClick={() => setGender('male')}
              >
                👴 Άνδρας
              </button>
              <button
                type="button"
                className={`es-gender-btn${gender === 'female' ? ' selected' : ''}`}
                onClick={() => setGender('female')}
              >
                👵 Γυναίκα
              </button>
            </div>

            <div className="es-form-row">
              <label>
                Όνομα *
                <input
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  placeholder="π.χ. Γιώργης"
                  required
                  autoFocus
                />
              </label>
              <label>
                Επώνυμο *
                <input
                  value={lastName}
                  onChange={(e) => setLastName(e.target.value)}
                  placeholder="π.χ. Παπαδόπουλος"
                  required
                />
              </label>
            </div>

            <label>
              Τηλέφωνο *
              <input
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="π.χ. 6912345678"
                type="tel"
                required
              />
            </label>

            <div className="es-form-actions">
              <button
                type="submit"
                disabled={!gender || !firstName || !lastName || !phone}
              >
                Προσθήκη →
              </button>
              <button
                type="button"
                className="secondary"
                onClick={handleCancel}
              >
                Ακύρωση
              </button>
            </div>
          </form>
        )}

        {/* Empty state */}
        {elders.length === 0 && !showForm && (
          <div style={{ textAlign: 'center', marginTop: '40px' }}>
            <p style={{ fontSize: '15px', color: 'var(--text-mid)', marginBottom: '8px' }}>
              Δεν έχετε προσθέσει ακόμη κανέναν ηλικιωμένο.
            </p>
            <p style={{ fontSize: '13.5px', color: 'var(--text-muted)' }}>
              Κάντε κλικ στο <strong>＋</strong> παραπάνω για να ξεκινήσετε.
            </p>
          </div>
        )}
      </main>
    </div>
  )
}
