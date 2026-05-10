export const API = 'https://api.talesofai.cn'
export const TOKEN_KEY = 'NIETA_ACCESS_TOKEN'
export const REFRESH_KEY = 'NIETA_REFRESH_TOKEN'
export const SITE_SESSION_KEY = 'WEIREN_SITE_SESSION'
export const USER_CACHE_KEY = 'WEIREN_USER'

export async function siteApi(path, options = {}) {
  const res = await fetch(path, options)
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.error || data.detail || '请求失败')
  return data
}

export function sessionHeaders(session) {
  return { 'Content-Type': 'application/json', 'x-session': session }
}

export async function netaFetch(path, token, options = {}) {
  const headers = { ...(options.headers || {}), 'x-token': token, Authorization: `Bearer ${token}` }
  const res = await fetch(path.startsWith('http') ? path : `${API}${path}`, { ...options, headers })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.error || data.detail || '捏Ta请求失败')
  return data
}
