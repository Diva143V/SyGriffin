import os from "os"
import { expect, test, beforeEach, afterEach } from "bun:test"
import { DatabaseClient } from "../../../src/storage/db/client"
import { Schema } from "../../../src/storage/db/schema"
import { GraphStore } from "../../../src/storage/db/graph/store"
import path from "path"
import fs from "fs/promises"

// Databases go to os.tmpdir(), never into the repo: files written under test/
// are not gitignored and get committed by a directory-wide `git add`.
const tmpDir = path.join(os.tmpdir(), "griffin-test-rebuild-" + process.pid)
let handle: DatabaseClient.Handle | undefined

beforeEach(async () => {
  await fs.rm(tmpDir, { recursive: true, force: true }).catch(() => {})
  await fs.mkdir(tmpDir, { recursive: true }).catch(() => {})
})

afterEach(async () => {
  if (handle) {
    try { handle.db.close() } catch {}
  }
  await fs.rm(tmpDir, { recursive: true, force: true }).catch(() => {})
})

test("GraphStore rebuild preserves agent/user nodes while re-deriving system nodes", () => {
  handle = DatabaseClient.create(path.join(tmpDir, "rebuild.db"))
  Schema.migrate(handle)

  // System entities
  handle.stmt(`INSERT INTO project (id, vcs, worktree, json) VALUES ('p1', 'git', '/app', '{}')`).run()
  handle.stmt(`INSERT INTO session (id, project_id, json) VALUES ('s1', 'p1', '{}')`).run()
  handle.stmt(`INSERT INTO message (id, session_id, role, created_at, json) VALUES ('m1', 's1', 'assistant', 1000, '{}')`).run()

  // Agent node
  GraphStore.recordNode(handle, {
    id: "clm:agent_claim_1",
    kind: "claim",
    label: "Agent Claim",
    recorded_at: 1000,
    origin: "agent",
    review_state: "unreviewed",
  })

  // Perform rebuild
  const res = GraphStore.rebuild(handle)
  expect(res.systemNodes).toBeGreaterThan(0)

  // Verify agent node survived rebuild
  const agentNode = handle.stmt(`SELECT * FROM node WHERE id = 'clm:agent_claim_1'`).get() as any
  expect(agentNode).toBeDefined()
  expect(agentNode.origin).toBe("agent")
})
