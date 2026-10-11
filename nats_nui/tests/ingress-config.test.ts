import { afterEach, expect, test, vi } from 'vitest'

vi.mock('@priolo/jon', () => ({ createStore: (setup: any) => ({ state: setup.state }) }))
afterEach(() => { vi.unstubAllGlobals(); vi.resetModules() })

test('loads optional configuration relative to the ingress page', async () => {
  const fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ theme: 'boring' }) })
  vi.stubGlobal('fetch', fetch)
  vi.stubGlobal('localStorage', { getItem: () => null })
  const layout = await import('./index')
  await layout.loadConfig()
  expect(fetch).toHaveBeenCalledWith('./config.json')
  expect(layout.default.state.theme).toBe('boring')
})

test.each(['http', 'network', 'json'])('configuration %s failures preserve a saved theme', async mode => {
  vi.stubGlobal('fetch', vi.fn(async () => {
    if (mode === 'network') throw new Error('offline')
    return { ok: mode !== 'http', json: async () => { throw new Error('invalid JSON') } }
  }))
  vi.stubGlobal('localStorage', { getItem: () => 'boring' })
  const layout = await import('./index')
  await layout.loadConfig()
  expect(layout.default.state.theme).toBe('boring')
})
