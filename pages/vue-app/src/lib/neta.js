import { API, netaFetch } from './api.js'

export function shortUrlOf(text = '') {
  return (String(text).match(/https?:\/\/t\.nieta\.art\/[a-zA-Z0-9]+/) || [])[0] || ''
}
export function uuidOf(text = '') {
  return (String(text).match(/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/) || [])[0] || ''
}
export function creatorOf(text = '') {
  return (String(text).match(/[?&#](?:from_user|creator_uuid|owner_uuid|user_uuid)=([0-9a-fA-F-]{32,36})/) || [])[1] || ''
}
export async function resolveShareInput(raw) {
  let text = String(raw || '')
  const short = shortUrlOf(text)
  if (short) {
    const data = await fetch(`${API}/v1/util/original-url?short_url=${encodeURIComponent(short)}`).then(r => r.json())
    text = typeof data === 'string' ? data : JSON.stringify(data || {})
  }
  return { uuid: uuidOf(text), creator_uuid: creatorOf(text), url: text }
}
export async function fetchNetaProfile(token) {
  return netaFetch('/v1/user/', token)
}
export async function fetchCharacterProfile(uuid, token) {
  return netaFetch(`/v2/travel/parent/${uuid}/profile`, token)
}
