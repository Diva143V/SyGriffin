import { test, expect, afterEach } from "bun:test"
import path from "path"
import fs from "fs/promises"
import { Global } from "../src/global"
import { Griffin } from "../src/griffin"

const file = path.join(Global.Path.data, "griffin-session.json")

afterEach(async () => {
  await fs.rm(file, { force: true }).catch(() => {})
})

test("getSession carries the sync bookkeeping fields", async () => {
  await fs.mkdir(Global.Path.data, { recursive: true })
  await Bun.write(
    file,
    JSON.stringify({
      api_key: "thk_test.secret",
      user_id: "user-1",
      device_name: "test-device",
      cached_v: 7,
      last_check_ts: 1751700000000,
    }),
  )

  const session = await Griffin.getSession()
  expect(session).not.toBeNull()
  expect(session!.cached_v).toBe(7)
  expect(session!.last_check_ts).toBe(1751700000000)
})
