const API_URL = import.meta.env.VITE_FAMILY_API_URL || 'http://localhost:8003'

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  })

  if (!response.ok) {
    let message = `Request failed (${response.status})`
    try {
      const data = await response.json()
      message = data.detail || message
    } catch {
      // noop
    }
    throw new Error(message)
  }

  return response.json()
}

export async function login(username, password) {
  return request('/v1/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  })
}

export async function me(token) {
  return request('/v1/auth/me', {
    headers: { Authorization: `Bearer ${token}` }
  })
}

export async function getDashboard(userId, token) {
  return request(`/v1/dashboard/${userId}`, {
    headers: { Authorization: `Bearer ${token}` }
  })
}

export async function getHistory(userId, token, limit = 20) {
  return request(`/v1/dashboard/${userId}/history?limit=${limit}`, {
    headers: { Authorization: `Bearer ${token}` }
  })
}

export async function getInsights(userId, token, days = 30) {
  return request(`/v1/dashboard/${userId}/insights?days=${days}`, {
    headers: { Authorization: `Bearer ${token}` }
  })
}
