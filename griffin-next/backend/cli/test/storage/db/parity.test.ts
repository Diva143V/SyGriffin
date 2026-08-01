import os from "os"
import { expect, test, beforeEach, afterEach } from "bun:test"
import { Storage } from "../../../src/storage/storage"
import { DatabaseClient } from "../../../src/storage/db/client"
import { DatabaseMode } from "../../../src/storage/db/mode"
import { Projection } from "../../../src/storage/db/projection"
import path from "path"
import fs from "fs/promises"

// Databases go to os.tmpdir(), never into the repo: files written under test/
// are not gitignored and get committed by a directory-wide `git add`.
const tmpDir = path.join(os.tmpdir(), "griffin-test-parity-" + process.pid)

beforeEach(async () => {
  await fs.rm(tmpDir, { recursive: true, force: true }).catch(() => {})
  await fs.mkdir(tmpDir, { recursive: true }).catch(() => {})
  DatabaseClient.create(path.join(tmpDir, "parity.db"))
  Projection.reset()
})

afterEach(async () => {
  delete process.env.GRIFFIN_DB
  DatabaseMode.reset()
  Projection.reset()
  await fs.rm(tmpDir, { recursive: true, force: true }).catch(() => {})
})

test("Parity across off, shadow, and primary modes", async () => {
  for (const mode of ["off", "shadow", "primary"] as const) {
    process.env.GRIFFIN_DB = mode
    DatabaseMode.reset()

    const key = ["project", `prj_${mode}`]
    const content = { id: `prj_${mode}`, vcs: "git", worktree: `/app/${mode}` }

    await Storage.write(key, content)
    await Projection.flush()

    const list = await Storage.list(["project"])
    expect(list).toContainEqual(key)

    if (mode === "primary") {
      const val = await Storage.read<any>(key)
      expect(val.id).toBe(`prj_${mode}`)
    }
  }
})
