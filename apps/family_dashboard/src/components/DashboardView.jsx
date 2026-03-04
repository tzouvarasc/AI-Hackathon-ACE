import { useMemo, useState } from 'react'
import logoImg from '../assets/logo.png'

function formatValue(value) {
  if (value === null || value === undefined || value === '') {
    return 'Μ/Δ'
  }
  if (typeof value === 'number') {
    return Number.isInteger(value) ? `${value}` : value.toFixed(2)
  }
  return `${value}`
}

function statusLabel(value) {
  if (!value) return 'Μ/Δ'
  if (value === 'good') return 'Καλή'
  if (value === 'watch') return 'Παρακολούθηση'
  if (value === 'risk') return 'Κίνδυνος'
  return value
}

function toPercent(value) {
  if (value === null || value === undefined) return 'Μ/Δ'
  const num = Number(value)
  if (Number.isNaN(num)) return 'Μ/Δ'
  return `${Math.round(num)}%`
}

function toNumber(value, fallback = 0) {
  const num = Number(value)
  return Number.isFinite(num) ? num : fallback
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value))
}

function formatDateGreek(dateStr) {
  if (!dateStr) return 'Μ/Δ'
  try {
    const d = new Date(dateStr)
    if (isNaN(d)) return dateStr
    return d.toLocaleDateString('el-GR', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' })
  } catch { return dateStr }
}

function formatTimeGreek(dateStr) {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr)
    if (isNaN(d)) return ''
    return d.toLocaleTimeString('el-GR', { hour: '2-digit', minute: '2-digit' })
  } catch { return '' }
}

function groupHistoryByDate(items) {
  const groups = new Map()
  ;(items || []).forEach((item) => {
    const raw = item.analysis?.created_at || ''
    let dateKey = 'Άγνωστη ημερομηνία'
    let dateSort = 'zzz'
    try {
      const d = new Date(raw)
      if (!isNaN(d)) {
        dateKey = d.toLocaleDateString('el-GR', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' })
        dateSort = d.toISOString().slice(0, 10)
      }
    } catch {}
    if (!groups.has(dateSort)) groups.set(dateSort, { label: dateKey, sort: dateSort, items: [] })
    groups.get(dateSort).items.push(item)
  })
  return [...groups.values()].sort((a, b) => b.sort.localeCompare(a.sort))
}

function scoreTo100(value) {
  const num = toNumber(value, 0)
  if (num <= 1) return Math.round(num * 100)
  return Math.round(num)
}

function buildLinePath(values, width = 640, height = 240, padding = 24) {
  const points = values.map((item) => toNumber(item, 0))
  if (points.length === 0) return ''

  const min = Math.min(...points)
  const max = Math.max(...points)
  const range = max - min || 1

  return points
    .map((value, index) => {
      const x = padding + (index / Math.max(points.length - 1, 1)) * (width - padding * 2)
      const y = height - padding - ((value - min) / range) * (height - padding * 2)
      return `${index === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`
    })
    .join(' ')
}

function ClinicalTrendChart({ emotionSeries, cognitiveSeries }) {
  const width = 640
  const height = 240
  const emotionPath = buildLinePath(emotionSeries, width, height)
  const cognitivePath = buildLinePath(cognitiveSeries, width, height)

  return (
    <div className="clinical-trend-chart">
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Τάσεις ευεξίας">
        <rect x="0" y="0" width={width} height={height} rx="18" ry="18" fill="rgba(245,241,234,0.72)" />

        {[0.2, 0.4, 0.6, 0.8].map((line) => {
          const y = (height * line).toFixed(1)
          return (
            <line
              key={`grid-${line}`}
              x1="20"
              x2={String(width - 20)}
              y1={y}
              y2={y}
              stroke="rgba(196,124,62,0.14)"
              strokeDasharray="5 6"
            />
          )
        })}

        {cognitivePath ? (
          <path
            d={cognitivePath}
            fill="none"
            stroke="#c47c3e"
            strokeWidth="3"
            strokeLinecap="round"
          />
        ) : null}

        {emotionPath ? (
          <path
            d={emotionPath}
            fill="none"
            stroke="#4e8c6e"
            strokeWidth="3"
            strokeLinecap="round"
          />
        ) : null}
      </svg>

      <div className="chart-legend">
        <span><i className="legend-dot cognitive" />Γνωστικό</span>
        <span><i className="legend-dot emotion" />Συναίσθημα</span>
      </div>
    </div>
  )
}

function DistributionBars({ title, data, emptyLabel = 'Δεν υπάρχουν ακόμη δεδομένα' }) {
  const entries = Object.entries(data || {})
    .map(([label, value]) => [label, toNumber(value, 0)])
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)

  const max = Math.max(...entries.map(([, value]) => value), 1)

  return (
    <div className="distribution-chart">
      <h3>{title}</h3>
      {entries.length === 0 ? <p className="subtext">{emptyLabel}</p> : null}
      <div className="dist-list">
        {entries.map(([label, value]) => {
          const width = Math.max(12, (value / max) * 100)
          return (
            <div key={label} className="dist-row">
              <div className="dist-meta">
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
              <div className="dist-track">
                <span className="dist-fill" style={{ width: `${width}%` }} />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function MemoryArchive({ history, filter, onFilterChange }) {
  const dateGroups = useMemo(() => groupHistoryByDate(history), [history])

  const filteredGroups = useMemo(() => {
    const term = filter.trim().toLowerCase()
    if (!term) return dateGroups
    return dateGroups
      .map((group) => ({
        ...group,
        items: group.items.filter((item) => {
          const t = String(item.transcript || '').toLowerCase()
          const a = String(item.assistant_text || '').toLowerCase()
          return t.includes(term) || a.includes(term)
        }),
      }))
      .filter((g) => g.items.length > 0)
  }, [dateGroups, filter])

  const totalCount = filteredGroups.reduce((sum, g) => sum + g.items.length, 0)

  return (
    <section className="panel memory-archive-panel">
      <div className="memory-archive-header">
        <div>
          <h2>Αρχείο Αναμνήσεων</h2>
          <p className="subtext" style={{ marginTop: '4px' }}>
            Διαβάστε τις συνομιλίες του αγαπημένου σας με τη Θάλπω.
          </p>
        </div>
        <div className="memory-search-wrap">
          <label>
            Αναζήτηση
            <input
              value={filter}
              onChange={(e) => onFilterChange(e.target.value)}
              placeholder="λέξη, θέμα, συναίσθημα…"
            />
          </label>
          <p className="subtext" style={{ fontSize: '12.5px', marginTop: '6px' }}>
            {totalCount} {totalCount === 1 ? 'καταγραφή' : 'καταγραφές'}
          </p>
        </div>
      </div>

      {filteredGroups.length === 0 ? (
        <p className="subtext" style={{ padding: '32px 0', textAlign: 'center' }}>
          Δεν υπάρχουν συνομιλίες ακόμη.
        </p>
      ) : (
        <div className="memory-date-groups">
          {filteredGroups.map((group) => (
            <div key={group.sort} className="memory-date-group">
              <div className="memory-date-header">
                <span className="memory-date-label">{group.label}</span>
                <span className="memory-date-count">{group.items.length} {group.items.length === 1 ? 'συνομιλία' : 'συνομιλίες'}</span>
              </div>
              <div className="memory-entries">
                {group.items.map((item, idx) => {
                  const tone = getHistoryTone(item)
                  const time = formatTimeGreek(item.analysis?.created_at)
                  return (
                    <div key={`${item.session_id}-${idx}`} className={`memory-entry ${tone}`}>
                      {time && <span className="memory-entry-time">{time}</span>}
                      {item.transcript && (
                        <blockquote className="memory-entry-elder">
                          «{item.transcript}»
                        </blockquote>
                      )}
                      {item.assistant_text && (
                        <div className="memory-entry-thalpo">
                          <span className="memory-thalpo-label">Θάλπω</span>
                          {item.assistant_text}
                        </div>
                      )}
                      {(item.analysis?.emotion_label || item.analysis?.risk_flags?.length > 0) && (
                        <p className="memory-entry-meta">
                          {item.analysis.emotion_label ? `διάθεση: ${item.analysis.emotion_label}` : ''}
                          {item.analysis.risk_flags?.length > 0 ? ` · σήματα: ${item.analysis.risk_flags.join(', ')}` : ''}
                        </p>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}

const FEATURE_CARD_ORDER = [
  ['voice_biomarkers_100', 'Βιοδείκτες φωνής'],
  ['cognitive_score_100', 'Γνωστικό σκορ'],
  ['cognitive_gym_100', 'Νοητική ενδυνάμωση'],
  ['meds_tracker', 'Φάρμακα'],
  ['sleep_quality', 'Ύπνος'],
  ['nutrition_status', 'Διατροφή'],
  ['hydration_status', 'Ενυδάτωση'],
  ['physio_engagement', 'Φυσιοθεραπεία'],
  ['social_connection', 'Κοινωνική επαφή'],
  ['active_risk_flags', 'Σήματα κινδύνου'],
]

function getHistoryTone(item) {
  const flags = item?.analysis?.risk_flags || []
  if (flags.length >= 3) return 'critical'
  if (flags.length >= 1) return 'warning'
  return 'stable'
}

export default function DashboardView({
  profile,
  elderName,
  elderlyId,
  setElderlyId,
  snapshot,
  history,
  insights,
  loading,
  error,
  onRefresh,
  onLogout,
  onBack,
}) {
  const [memoryFilter, setMemoryFilter] = useState('')

  const cards = snapshot?.cards || {}
  const latestBiomarkers = history?.[0]?.analysis?.biomarkers || {}
  const activeAlerts = snapshot?.active_alerts || []

  const emotionSeries = useMemo(
    () => [...(history || [])].slice(0, 14).reverse().map((item) => scoreTo100(item.analysis?.emotion_score)),
    [history]
  )

  const cognitiveSeries = useMemo(
    () => [...(history || [])].slice(0, 14).reverse().map((item) => scoreTo100(item.analysis?.cognitive_score)),
    [history]
  )

  const riskCounts = insights?.risk_flag_counts || {}
  const alertCounts = insights?.alert_counts || {}

  const riskIndex = useMemo(() => {
    const avgEmotion = scoreTo100(insights?.avg_emotion_score ?? snapshot?.emotion_score)
    const avgCognitive = scoreTo100(insights?.avg_cognitive_score ?? snapshot?.cognitive_score)
    const alertLoad = activeAlerts.reduce((score, alert) => {
      if (alert.severity === 'critical') return score + 35
      if (alert.severity === 'warning') return score + 18
      return score + 6
    }, 0)
    const derived = alertLoad + (100 - avgEmotion) * 0.25 + (100 - avgCognitive) * 0.3
    return clamp(Math.round(derived), 0, 100)
  }, [activeAlerts, insights, snapshot])

  const riskTone = activeAlerts.some((item) => item.severity === 'critical') || riskIndex >= 70
    ? 'critical'
    : activeAlerts.some((item) => item.severity === 'warning') || riskIndex >= 40
      ? 'warning'
      : 'stable'

  const wellnessLabel =
    riskTone === 'critical' ? 'Χρειάζεται προσοχή' :
    riskTone === 'warning'  ? 'Να παρακολουθείται' :
    'Σε καλή κατάσταση'

  return (
    <div className="prototype-shell">
      {/* ── Sidebar ─────────────────────────────── */}
      <aside className="panel side-rail">
        <div className="brand">
          <img src={logoImg} alt="Thalpo" className="brand-logo" />
          <span className="brand-name">Thalpo</span>
        </div>

        <div className="profile-chip">
          <strong>{elderName || profile.display_name}</strong>
          <span>{profile.display_name} · {profile.role}</span>
        </div>

        <nav className="rail-nav" aria-label="Πλοήγηση">
          <button type="button" className="rail-item active">Εικόνα Υγείας</button>
          <button type="button" className="rail-item">Ειδοποιήσεις</button>
          <button type="button" className="rail-item">Δείκτες Ευεξίας</button>
          <button type="button" className="rail-item">Ημερολόγιο</button>
        </nav>

        <div className="rail-stat-grid">
          <div>
            <small>Συνομιλίες</small>
            <strong>{formatValue(insights?.total_turns)}</strong>
          </div>
          <div>
            <small>Συνεδρίες</small>
            <strong>{formatValue(insights?.sessions_count)}</strong>
          </div>
        </div>

        {onBack && (
          <button className="secondary" onClick={onBack}>← Όλοι οι ηλικιωμένοι</button>
        )}
        <button className="secondary" onClick={onLogout}>Αποσύνδεση</button>
      </aside>

      {/* ── Main ────────────────────────────────── */}
      <main className="main-stage">

        {/* Header */}
        <header className="panel command-bar">
          <div>
            <p className="eyebrow">Thalpo</p>
            <h1>{elderName || 'Κέντρο Φροντίδας'}</h1>
            <p className="subtext">
              Παρακολουθείτε σε πραγματικό χρόνο την υγεία και την καθημερινότητα του αγαπημένου σας.
            </p>
          </div>

        </header>

        {error ? <p className="error">{error}</p> : null}

        {/* Primary grid: dial + trend + insights */}
        <section className="clinical-primary-grid">

          <article className={`panel risk-dial ${riskTone}`}>
            <p className="eyebrow">Κατάσταση Ευεξίας</p>
            <div className="dial-wrap" style={{ '--dial': `${riskIndex * 3.6}deg` }}>
              <div className="dial-inner">
                <strong>{riskIndex}</strong>
                <span>/100</span>
              </div>
            </div>
            <p className="subtext">{wellnessLabel}</p>
          </article>

          <article className="panel trend-panel">
            <div className="panel-title-row">
              <h2>Τάσεις Ευεξίας</h2>
              <p className="subtext">Τελευταίοι 14 γύροι</p>
            </div>
            <ClinicalTrendChart emotionSeries={emotionSeries} cognitiveSeries={cognitiveSeries} />
          </article>

          <article className="panel bento medical-visual-panel">
            <div className="panel-title-row">
              <h2>Σύνοψη Περιόδου</h2>
              <p className="subtext">Τελευταίες 30 μέρες</p>
            </div>
            <p className="subtext" style={{ lineHeight: 1.7 }}>
              {insights?.summary || 'Δεν υπάρχουν ακόμη αρκετά δεδομένα για σύνοψη.'}
            </p>
            <div style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              <div className="card-pill" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '2px' }}>
                <span style={{ fontSize: '11px' }}>Μέσο γνωστικό</span>
                <strong>{toPercent(insights?.avg_cognitive_score)}</strong>
              </div>
              <div className="card-pill" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '2px' }}>
                <span style={{ fontSize: '11px' }}>Μέσο συναίσθημα</span>
                <strong>{toPercent(insights?.avg_emotion_score)}</strong>
              </div>
            </div>
          </article>

        </section>

        {/* KPI grid */}
        <section className="glance-grid">
          <article className="panel metric">
            <h3>Γνωστικό</h3>
            <p className="kpi-value">{formatValue(snapshot?.cognitive_score)}</p>
            <span className="kpi-caption">Τρέχον σκορ</span>
          </article>
          <article className="panel metric">
            <h3>Συναίσθημα</h3>
            <p className="kpi-value">{formatValue(snapshot?.emotion_score)}</p>
            <span className="kpi-caption">Συναισθηματικό σήμα</span>
          </article>
          <article className="panel metric">
            <h3>Διάθεση</h3>
            <p className="kpi-value">{formatValue(snapshot?.emotion_label)}</p>
            <span className="kpi-caption">Κυρίαρχη κατάσταση</span>
          </article>
          <article className="panel metric">
            <h3>Ενημέρωση</h3>
            <p className="kpi-value" style={{ fontSize: '1.1rem' }}>
              {snapshot?.last_updated
                ? new Date(snapshot.last_updated).toLocaleString('el-GR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
                : 'Μ/Δ'}
            </p>
            <span className="kpi-caption">Τελευταίος συγχρονισμός</span>
          </article>
        </section>

        {/* Analytics grid */}
        <section className="analytics-grid">
          <article className="panel bento">
            <DistributionBars
              title="Συχνότητα Σημάτων"
              data={riskCounts}
              emptyLabel="Δεν έχουν καταγραφεί σήματα."
            />
          </article>

          <article className="panel bento">
            <DistributionBars
              title="Είδη Ειδοποιήσεων"
              data={alertCounts}
              emptyLabel="Δεν έχουν καταγραφεί ειδοποιήσεις."
            />
          </article>

          <article className="panel bento feature-panel">
            <h2>Δείκτες Ευεξίας</h2>
            <div className="cards-list">
              {FEATURE_CARD_ORDER.map(([key, label]) => (
                <div key={key} className="card-pill">
                  <span>{label}</span>
                  <strong>
                    {key.includes('_100') || key === 'meds_tracker' || key === 'physio_engagement' || key === 'social_connection'
                      ? toPercent(cards[key])
                      : key.endsWith('_status')
                        ? statusLabel(cards[key])
                        : formatValue(cards[key])}
                  </strong>
                </div>
              ))}
              <div className="card-pill"><span>Άρθρωση φωνής</span><strong>{formatValue(latestBiomarkers.voice_articulation_blur)}</strong></div>
              <div className="card-pill"><span>Εύρεση λέξεων</span><strong>{formatValue(latestBiomarkers.voice_word_finding)}</strong></div>
              <div className="card-pill"><span>Παύσεις αναπνοής</span><strong>{formatValue(latestBiomarkers.voice_breath_pauses)}</strong></div>
              <div className="card-pill"><span>Τόνος φωνής</span><strong>{formatValue(latestBiomarkers.prosody_stress)}</strong></div>
            </div>
          </article>
        </section>

        {/* Alerts */}
        <article className="panel panel-inner">
          <h2 style={{ marginBottom: '14px' }}>Ειδοποιήσεις</h2>
          {activeAlerts.length === 0 ? (
            <p className="subtext">Δεν υπάρχουν ενεργές ειδοποιήσεις. Όλα καλά! 🌿</p>
          ) : (
            <ul className="alert-list">
              {activeAlerts.map((alert, index) => (
                <li key={`${alert.created_at}-${index}`} className={`alert ${alert.severity}`}>
                  <p>
                    <strong>
                      {alert.severity === 'critical' ? 'Κρίσιμο' : alert.severity === 'warning' ? 'Προσοχή' : 'Ενημέρωση'}
                    </strong>
                    {' · '}{formatDateGreek(alert.created_at)} {formatTimeGreek(alert.created_at)}
                  </p>
                  <p>{alert.reasons.join(' · ')}</p>
                </li>
              ))}
            </ul>
          )}
        </article>

        {/* Digital Memory Archive */}
        <MemoryArchive history={history} filter={memoryFilter} onFilterChange={setMemoryFilter} />

      </main>
    </div>
  )
}
