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
      source: 'urn:uuid:7d4d54df-5cb0-4ef8-a339-97bb08056485',
      subject: 'urn:uuid:882a4bf5-46f4-4212-bca8-17d398e265a4',
      time: '2026-10-11T01:37:37.527Z', datacontenttype: 'application/cbor',
      type: 'io.github.jeffglousher.agentboard.notice.v1',
      data: { actor: { agent: 'add1f8e9-090d-4728-a613-1e1368665b71', session: '199db73d-6ef4-4048-82df-3b76661a83c0' },
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
