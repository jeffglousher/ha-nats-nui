import { readFileSync } from 'node:fs'
import { describe, expect, test } from 'vitest'
import { CBOR } from '@cbortech/cbor'
import { bytesToBinaryString, compileCddl, decodeAndValidateCbor } from './index'

const schema = {
  id: 'bundled/agent-board', name: 'agent-board.cddl',
  content: readFileSync(new URL('../../../../agent-board.cddl', import.meta.url), 'utf8'),
}
describe('bundled authoritative agent-board contract', () => {
  test('compiles the complete contract without a separate UI schema', () => {
    expect(compileCddl(schema.content).error).toBeUndefined()
  })
  test('decodes and validates a native notice with integer SenML labels', () => {
    const notice = {
      specversion: '1.0', id: 'ab1942a3-6c22-48d9-8b05-386d4cc3cf0e',
      source: 'urn:uuid:11111111-1111-4111-8111-111111111111',
      subject: 'urn:uuid:22222222-2222-4222-8222-222222222222',
      time: '2026-10-11T01:37:37.527Z', datacontenttype: 'application/cbor',
      type: 'io.github.jeffglousher.agentboard.notice.v1',
      data: { actor: { agent: '33333333-3333-4333-8333-333333333333', session: '44444444-4444-4444-8444-444444444444' },
        to: { scope: 'all' }, topic: 'agent-board', intent: 'inform', attention: 'normal', summary: 'Contract fixture',
        facts: [new CBOR.MapEntries([0, 'online'], [4, true])] },
    }
    const result = decodeAndValidateCbor(bytesToBinaryString(CBOR.encode(notice)), schema, 'notice-event')
    expect(result.success).toBe(true)
    expect(result.valid, JSON.stringify(result)).toBe(true)
  })
  test('validates version one metadata and rejects unsupported versions', () => {
    for (const value of [
      { version: 1, data: { created: '2026-10-11T01:37:37.527Z' } },
    ]) {
      const result = decodeAndValidateCbor(bytesToBinaryString(CBOR.encode(value)), schema, 'agent-board')
      expect(result.success).toBe(true)
      expect(result.valid).toBe(true)
    }
    const future = decodeAndValidateCbor(bytesToBinaryString(CBOR.encode({version: 2, data: {created: 'future'}})), schema, 'remote-envelope')
    expect(future.valid).toBe(false)
  })
})
