import { describe, it, expect, vi, beforeEach } from "vitest"
import ajax from "@/plugins/AjaxService"
import api from "./buckets"

vi.mock("@/plugins/AjaxService", () => ({ default: { get: vi.fn(), post: vi.fn() } }))
const wire = { bucket: "test", backing_store: "file", config: {
    bucket: "test", max_bytes: 65536, max_value_size: 1024, num_replicas: 1, history: 2,
} }
const model = { bucket: "test", maxBytes: 65536, maxValueSize: 1024, replicas: 1, history: 2 } as any
describe("HA bucket API contract with pinned nats.go", () => {
    beforeEach(() => { vi.clearAllMocks(); vi.mocked(ajax.post).mockResolvedValue(wire); vi.mocked(ajax.get).mockResolvedValue(wire) })
    for (const method of ["create", "update"] as const) {
        it(`${method} sends enforceable limits and decodes the response`, async () => {
            const result = await api[method]("connection", model)
            const sent = vi.mocked(ajax.post).mock.calls[0][1] as any
            expect(sent).toEqual({ bucket: "test", max_bytes: 65536, max_value_size: 1024, num_replicas: 1, history: 2 })
            expect(result.config).toMatchObject(model)
            expect(result.backingStore).toBe("file")
        })
    }
    it("loads limits back into editable UI fields", async () => {
        expect((await api.get("connection", "test")).config).toMatchObject(model)
    })
    it("normalizes bucket lists and empty responses", async () => {
        vi.mocked(ajax.get).mockResolvedValueOnce([wire]).mockResolvedValueOnce(null)
        expect((await api.index("connection"))[0].backingStore).toBe("file")
        expect(await api.index("connection")).toEqual([])
    })
})
