import { describe, expect, test } from "bun:test"
import { Griffin } from "../../src/griffin"

// Test env is XDG-isolated (see test/preload.ts), so the session file lives in a
// throwaway dir and starts absent.

describe("Griffin session file", () => {
  test("getSession returns null when no session file exists (real logout)", async () => {
    await Griffin.clearSession()
    expect(await Griffin.getSession()).toBeNull()
    expect(await Griffin.isAuthenticated()).toBe(false)
  })

  test("saveSession then getSession round-trips atomically", async () => {
    await Griffin.saveSession({ api_key: "thk_test.secret", user_id: "u1", device_name: "dev" })
    const s = await Griffin.getSession()
    expect(s?.api_key).toBe("thk_test.secret")
    expect(s?.user_id).toBe("u1")
    await Griffin.clearSession()
    expect(await Griffin.getSession()).toBeNull()
  })

  test("a session without an api_key is treated as no session", async () => {
    await Griffin.saveSession({ api_key: "", user_id: "u1" } as any)
    expect(await Griffin.getSession()).toBeNull()
    await Griffin.clearSession()
  })
})
