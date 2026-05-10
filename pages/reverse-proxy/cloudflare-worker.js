const DEFAULT_ORIGIN = 'https://s-63a86395-de5c-46f9-a54d-0f7d02aa0671-3000.cohub.run'

export default {
  async fetch(request, env) {
    const origin = (env.COHUB_ORIGIN || DEFAULT_ORIGIN).replace(/\/$/, '')
    const incomingUrl = new URL(request.url)
    const upstreamUrl = new URL(incomingUrl.pathname + incomingUrl.search, origin)

    const headers = new Headers(request.headers)
    headers.set('Host', new URL(origin).host)
    headers.set('X-Forwarded-Host', incomingUrl.host)
    headers.set('X-Forwarded-Proto', incomingUrl.protocol.replace(':', ''))

    const upstreamRequest = new Request(upstreamUrl.toString(), {
      method: request.method,
      headers,
      body: ['GET', 'HEAD'].includes(request.method) ? undefined : request.body,
      redirect: 'manual'
    })

    const response = await fetch(upstreamRequest)
    const outHeaders = new Headers(response.headers)

    // Keep the custom domain as the public origin.
    outHeaders.delete('content-security-policy')
    outHeaders.delete('cross-origin-resource-policy')
    outHeaders.set('X-Content-Type-Options', 'nosniff')
    outHeaders.set('Referrer-Policy', 'strict-origin-when-cross-origin')

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: outHeaders
    })
  }
}
