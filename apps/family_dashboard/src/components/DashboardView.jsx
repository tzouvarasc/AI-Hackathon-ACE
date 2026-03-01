function formatValue(value) {
  if (value === null || value === undefined) {
    return 'N/A'
  }
  if (typeof value === 'number') {
    return Number.isInteger(value) ? `${value}` : value.toFixed(2)
  }
  return `${value}`
}

export default function DashboardView({
  profile,
  elderlyId,
  setElderlyId,
  snapshot,
  history,
  insights,
  loading,
  error,
  onRefresh,
  onLogout
}) {
  const cards = Object.entries(snapshot?.cards || {})

  return (
    <div className="dashboard-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">THALPO FAMILY</p>
          <h1>Care Dashboard</h1>
          <p className="subtext">
            {profile.display_name} · {profile.role}
          </p>
        </div>
        <button className="secondary" onClick={onLogout}>Logout</button>
      </header>

      <section className="panel controls">
        <label>
          Elderly User ID
          <input value={elderlyId} onChange={(e) => setElderlyId(e.target.value)} />
        </label>
        <button onClick={onRefresh} disabled={loading}>
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </section>

      {error ? <p className="error">{error}</p> : null}

      <section className="grid">
        <article className="panel metric">
          <h3>Cognitive Score</h3>
          <p>{formatValue(snapshot?.cognitive_score)}</p>
        </article>
        <article className="panel metric">
          <h3>Emotion Score</h3>
          <p>{formatValue(snapshot?.emotion_score)}</p>
        </article>
        <article className="panel metric">
          <h3>Emotion Label</h3>
          <p>{formatValue(snapshot?.emotion_label)}</p>
        </article>
        <article className="panel metric">
          <h3>Last Updated</h3>
          <p>{formatValue(snapshot?.last_updated)}</p>
        </article>
      </section>

      <section className="panel">
        <h2>Conversation Insights (30 days)</h2>
        {!insights ? (
          <p className="subtext">No insights yet.</p>
        ) : (
          <div className="insights-grid">
            <div className="card-pill">
              <span>Total turns</span>
              <strong>{formatValue(insights.total_turns)}</strong>
            </div>
            <div className="card-pill">
              <span>Sessions</span>
              <strong>{formatValue(insights.sessions_count)}</strong>
            </div>
            <div className="card-pill">
              <span>Avg emotion</span>
              <strong>{formatValue(insights.avg_emotion_score)}</strong>
            </div>
            <div className="card-pill">
              <span>Avg cognitive</span>
              <strong>{formatValue(insights.avg_cognitive_score)}</strong>
            </div>
            <div className="insights-block">
              <h3>Summary</h3>
              <p>{insights.summary || 'N/A'}</p>
            </div>
            <div className="insights-block">
              <h3>Suggested actions</h3>
              {(insights.suggested_actions || []).length === 0 ? (
                <p className="subtext">No actions.</p>
              ) : (
                <ul className="plain-list">
                  {(insights.suggested_actions || []).map((action, index) => (
                    <li key={`${action}-${index}`}>{action}</li>
                  ))}
                </ul>
              )}
            </div>
            <div className="insights-block">
              <h3>Top keywords</h3>
              <p>{(insights.top_keywords || []).join(', ') || 'N/A'}</p>
            </div>
          </div>
        )}
      </section>

      <section className="grid two-col">
        <article className="panel">
          <h2>Cards</h2>
          {cards.length === 0 ? <p className="subtext">No cards yet.</p> : null}
          <div className="cards-list">
            {cards.map(([key, value]) => (
              <div key={key} className="card-pill">
                <span>{key}</span>
                <strong>{formatValue(value)}</strong>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <h2>Active Alerts</h2>
          {(snapshot?.active_alerts || []).length === 0 ? (
            <p className="subtext">No active alerts.</p>
          ) : (
            <ul className="alert-list">
              {snapshot.active_alerts.map((alert, index) => (
                <li key={`${alert.created_at}-${index}`} className={`alert ${alert.severity}`}>
                  <p>
                    <strong>{alert.severity.toUpperCase()}</strong> · {alert.created_at}
                  </p>
                  <p>{alert.reasons.join(' | ')}</p>
                </li>
              ))}
            </ul>
          )}
        </article>
      </section>

      <section className="panel">
        <h2>Recent History</h2>
        {history.length === 0 ? <p className="subtext">No history yet.</p> : null}
        <div className="history-list">
          {history.map((item, index) => (
            <div className="history-item" key={`${item.session_id}-${index}`}>
              <p>
                <strong>{item.analysis.created_at}</strong> · session {item.session_id}
              </p>
              <p><strong>User:</strong> {item.transcript}</p>
              {item.assistant_text ? <p><strong>Thalpo:</strong> {item.assistant_text}</p> : null}
              <p className="subtext">
                emotion={item.analysis.emotion_label} ({formatValue(item.analysis.emotion_score)}) ·
                cognitive={formatValue(item.analysis.cognitive_score)} ·
                flags={item.analysis.risk_flags.join(', ') || 'none'}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
