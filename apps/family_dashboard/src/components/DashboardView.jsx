import { useMemo, useState } from 'react'
import logoImg from '../assets/logo.png'

/* ── inline SVG icon set ─────────────────────────── */
function Icon({ d, size = 18, color = 'currentColor', fill = 'none', strokeWidth = 1.8 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill={fill} stroke={color}
      strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ flexShrink: 0 }}>
      <path d={d} />
    </svg>
  )
}

const ICONS = {
  health:    'M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z',
  bell:      'M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 0 1-3.46 0',
  chart:     'M18 20V10M12 20V4M6 20v-6',
  archive:   'M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z',
  brain:     'M9.5 2a2.5 2.5 0 0 1 5 0c1.5.2 3.5 1.2 4 4 .6 3-.5 5.5-2 7-1 1-1.5 2.5-1.5 4H9c0-1.5-.5-3-1.5-4-1.5-1.5-2.6-4-2-7 .5-2.8 2.5-3.8 4-4z',
  emotion:   'M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z',
  smile:     'M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10zM8 13s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01',
  clock:     'M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10zm0-14v4l3 3',
  shield:    'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z',
  mic:       'M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3zm6 10c0 3.31-2.69 6-6 6s-6-2.69-6-6H4c0 3.85 2.77 7.08 6.5 7.73V22h3v-3.27C17.23 18.08 20 14.85 20 11h-2z',
  pill:      'M10.5 3.5a6 6 0 0 1 6 6v1.5a6 6 0 0 1-6 6h-1a6 6 0 0 1-6-6v-1.5a6 6 0 0 1 6-6h1zm-4 6.5h10M7 7l10 10',
  moon:      'M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z',
  droplet:   'M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z',
  activity:  'M22 12h-4l-3 9L9 3l-3 9H2',
  users:     'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z',
  alert:     'M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0zM12 9v4M12 17h.01',
  refresh:   'M23 4v6h-6M1 20v-6h6M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15',
  food:      'M18 8h1a4 4 0 0 1 0 8h-1M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8zm4-7v7M10 1v7M14 1v7',
  dumbbell:  'M6.5 6.5h11M6.5 17.5h11M3 3v4M3 17v4M21 3v4M21 17v4M3 5h2M19 5h2M3 19h2M19 19h2',
}

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
  ['voice_biomarkers_100', 'Βιοδείκτες φωνής',  'mic'],
  ['cognitive_score_100',  'Γνωστικό σκορ',      'brain'],
  ['cognitive_gym_100',    'Νοητική ενδυνάμωση', 'dumbbell'],
  ['meds_tracker',         'Φάρμακα',             'pill'],
  ['sleep_quality',        'Ύπνος',               'moon'],
  ['nutrition_status',     'Διατροφή',            'food'],
  ['hydration_status',     'Ενυδάτωση',           'droplet'],
  ['physio_engagement',    'Φυσιοθεραπεία',       'activity'],
  ['social_connection',    'Κοινωνική επαφή',     'users'],
  ['active_risk_flags',    'Σήματα κινδύνου',     'alert'],
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
          <button type="button" className="rail-item active"><Icon d={ICONS.health} size={16} />Εικόνα Υγείας</button>
          <button type="button" className="rail-item"><Icon d={ICONS.bell} size={16} />Ειδοποιήσεις</button>
          <button type="button" className="rail-item"><Icon d={ICONS.chart} size={16} />Δείκτες Ευεξίας</button>
          <button type="button" className="rail-item"><Icon d={ICONS.archive} size={16} />Αρχείο Συνομιλιών</button>
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
          <button className="secondary" onClick={onBack}><Icon d="M15 18l-6-6 6-6" size={15} />Όλοι οι ηλικιωμένοι</button>
        )}
        <button className="secondary" onClick={onLogout}><Icon d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9" size={15} />Αποσύνδεση</button>
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
          <div className="command-actions">
            <span className="role-chip">{profile.role}</span>
            <button type="button" className="secondary" onClick={onRefresh} disabled={loading}>
              {loading ? 'Ανανέωση...' : 'Ανανέωση Δεδομένων'}
            </button>
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
              <h2><Icon d={ICONS.activity} size={20} />Τάσεις Ευεξίας</h2>
              <p className="subtext">Τελευταίοι 14 γύροι</p>
            </div>
            <ClinicalTrendChart emotionSeries={emotionSeries} cognitiveSeries={cognitiveSeries} />
          </article>

          <article className="panel bento medical-visual-panel">
            <div className="panel-title-row">
              <h2><Icon d={ICONS.shield} size={20} />Σύνοψη Περιόδου</h2>
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
            <div className="kpi-icon-wrap"><Icon d={ICONS.brain} size={22} /></div>
            <h3>Γνωστικό</h3>
            <p className="kpi-value">{formatValue(snapshot?.cognitive_score)}</p>
            <span className="kpi-caption">Τρέχον σκορ</span>
          </article>
          <article className="panel metric">
            <div className="kpi-icon-wrap"><Icon d={ICONS.emotion} size={22} /></div>
            <h3>Συναίσθημα</h3>
            <p className="kpi-value">{formatValue(snapshot?.emotion_score)}</p>
            <span className="kpi-caption">Συναισθηματικό σήμα</span>
          </article>
          <article className="panel metric">
            <div className="kpi-icon-wrap"><Icon d={ICONS.smile} size={22} /></div>
            <h3>Διάθεση</h3>
            <p className="kpi-value">{formatValue(snapshot?.emotion_label)}</p>
            <span className="kpi-caption">Κυρίαρχη κατάσταση</span>
          </article>
          <article className="panel metric">
            <div className="kpi-icon-wrap"><Icon d={ICONS.clock} size={22} /></div>
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
            <h2><Icon d={ICONS.chart} size={20} />Δείκτες Ευεξίας</h2>
            <div className="cards-list">
              {FEATURE_CARD_ORDER.map(([key, label, iconKey]) => (
                <div key={key} className="card-pill">
                  {iconKey && ICONS[iconKey] && <Icon d={ICONS[iconKey]} size={14} />}
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
              <div className="card-pill"><Icon d={ICONS.mic} size={14} /><span>Άρθρωση φωνής</span><strong>{formatValue(latestBiomarkers.voice_articulation_blur)}</strong></div>
              <div className="card-pill"><Icon d={ICONS.brain} size={14} /><span>Εύρεση λέξεων</span><strong>{formatValue(latestBiomarkers.voice_word_finding)}</strong></div>
              <div className="card-pill"><Icon d={ICONS.activity} size={14} /><span>Παύσεις αναπνοής</span><strong>{formatValue(latestBiomarkers.voice_breath_pauses)}</strong></div>
              <div className="card-pill"><Icon d={ICONS.mic} size={14} /><span>Τόνος φωνής</span><strong>{formatValue(latestBiomarkers.prosody_stress)}</strong></div>
            </div>
          </article>
        </section>

        {/* Alerts */}
        <article className="panel panel-inner">
          <h2 style={{ marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}><Icon d={ICONS.bell} size={20} />Ειδοποιήσεις</h2>
          {activeAlerts.length === 0 ? (
            <p className="subtext">Δεν υπάρχουν ενεργές ειδοποιήσεις.</p>
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
