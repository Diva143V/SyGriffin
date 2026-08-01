import { DatabaseClient } from "../client"
import { Hash } from "../hash"
import { Log } from "../../../util/log"

export namespace Derive {
  const log = Log.create({ service: "storage.db.graph.derive" })

  const TOOL_INPUT_PATH_KEYS = new Set([
    "filePath",
    "path",
    "file",
    "targetPath",
    "sourcePath",
    "destPath",
    "filename",
  ])

  export function artifactId(path: string): string {
    const norm = path.replace(/\\/g, "/").toLowerCase().trim()
    return "art:" + Hash.sha256Hex(norm).slice(0, 16)
  }

  export function deriveFromMessage(handle: DatabaseClient.Handle, messageId: string): void {
    const msgRow = handle
      .stmt(`SELECT id, session_id, role, agent, model, created_at, json FROM message WHERE id = ?`)
      .get(messageId) as any
    if (!msgRow) return

    const sesRow = handle
      .stmt(`SELECT id, project_id, created_at FROM session WHERE id = ?`)
      .get(msgRow.session_id) as any
    if (!sesRow) return

    const projectId = sesRow.project_id
    const prjNodeId = `prj:${projectId}`
    const sesNodeId = `ses:${sesRow.id}`
    const msgNodeId = `msg:${msgRow.id}`
    const recordedAt = msgRow.created_at ?? Date.now()

    handle.tx(() => {
      // 1. Ensure project node
      handle
        .stmt(
          `INSERT INTO node (id, kind, label, recorded_at, entity_type, entity_id, origin, review_state) ` +
            `VALUES (?, 'project', ?, ?, 'project', ?, 'system', 'accepted') ON CONFLICT(id) DO NOTHING`,
        )
        .run(prjNodeId, `Project ${projectId}`, recordedAt, projectId)

      // 2. Ensure session node + edge
      handle
        .stmt(
          `INSERT INTO node (id, kind, label, recorded_at, entity_type, entity_id, origin, review_state) ` +
            `VALUES (?, 'session', ?, ?, 'session', ?, 'system', 'accepted') ON CONFLICT(id) DO NOTHING`,
        )
        .run(sesNodeId, `Session ${sesRow.id}`, recordedAt, sesRow.id)

      handle
        .stmt(
          `INSERT INTO edge (from_id, to_id, relation, origin, created_at) ` +
            `VALUES (?, ?, 'part-of', 'system', ?) ON CONFLICT(from_id, to_id, relation) WHERE revoked_at IS NULL DO NOTHING`,
        )
        .run(sesNodeId, prjNodeId, recordedAt)

      // 3. Message node + edge
      handle
        .stmt(
          `INSERT INTO node (id, kind, label, recorded_at, entity_type, entity_id, origin, review_state, derived_at) ` +
            `VALUES (?, 'message', ?, ?, 'message', ?, 'system', 'accepted', ?) ` +
            `ON CONFLICT(id) DO UPDATE SET derived_at = excluded.derived_at`,
        )
        .run(msgNodeId, `${msgRow.role ?? "message"} ${msgRow.id}`, recordedAt, msgRow.id, Date.now())

      handle
        .stmt(
          `INSERT INTO edge (from_id, to_id, relation, origin, created_at) ` +
            `VALUES (?, ?, 'part-of', 'system', ?) ON CONFLICT(from_id, to_id, relation) WHERE revoked_at IS NULL DO NOTHING`,
        )
        .run(msgNodeId, sesNodeId, recordedAt)

      // 4. Parts processing
      const parts = handle
        .stmt(`SELECT id, type, tool, path, created_at, json FROM part WHERE message_id = ?`)
        .all(messageId) as any[]

      for (const p of parts) {
        const partVal = JSON.parse(p.json ?? "{}")
        const partTime = p.created_at ?? recordedAt

        if (p.type === "tool") {
          const runNodeId = `run:${p.id}`
          const toolName = p.tool ?? partVal.tool ?? "tool"
          handle
            .stmt(
              `INSERT INTO node (id, kind, subtype, label, recorded_at, entity_type, entity_id, origin, review_state) ` +
                `VALUES (?, 'run', ?, ?, ?, 'part', ?, 'system', 'accepted') ON CONFLICT(id) DO NOTHING`,
            )
            .run(runNodeId, toolName, `Run ${toolName}`, partTime, p.id)

          handle
            .stmt(
              `INSERT INTO edge (from_id, to_id, relation, origin, created_at) ` +
                `VALUES (?, ?, 'part-of', 'system', ?) ON CONFLICT(from_id, to_id, relation) WHERE revoked_at IS NULL DO NOTHING`,
            )
            .run(runNodeId, msgNodeId, partTime)

          // Tool input paths allowlist
          if (partVal.state?.input && typeof partVal.state.input === "object") {
            for (const [k, v] of Object.entries(partVal.state.input)) {
              if (TOOL_INPUT_PATH_KEYS.has(k) && typeof v === "string" && v.trim()) {
                const artId = artifactId(v)
                handle
                  .stmt(
                    `INSERT INTO node (id, kind, label, recorded_at, origin, review_state) ` +
                      `VALUES (?, 'artifact', ?, ?, 'system', 'accepted') ON CONFLICT(id) DO NOTHING`,
                  )
                  .run(artId, v, partTime)

                handle
                  .stmt(
                    `INSERT INTO edge (from_id, to_id, relation, origin, created_at) ` +
                      `VALUES (?, ?, 'consumed', 'system', ?) ON CONFLICT(from_id, to_id, relation) WHERE revoked_at IS NULL DO NOTHING`,
                  )
                  .run(runNodeId, artId, partTime)
              }
            }
          }
        } else if (p.type === "patch") {
          const runNodeId = `run:${p.id}`
          handle
            .stmt(
              `INSERT INTO node (id, kind, subtype, label, recorded_at, entity_type, entity_id, origin, review_state) ` +
                `VALUES (?, 'run', 'patch', 'Patch', ?, 'part', ?, 'system', 'accepted') ON CONFLICT(id) DO NOTHING`,
            )
            .run(runNodeId, partTime, p.id)

          handle
            .stmt(
              `INSERT INTO edge (from_id, to_id, relation, origin, created_at) ` +
                `VALUES (?, ?, 'part-of', 'system', ?) ON CONFLICT(from_id, to_id, relation) WHERE revoked_at IS NULL DO NOTHING`,
            )
            .run(runNodeId, msgNodeId, partTime)

          if (Array.isArray(partVal.files)) {
            for (const filePath of partVal.files) {
              if (typeof filePath === "string" && filePath.trim()) {
                const artId = artifactId(filePath)
                handle
                  .stmt(
                    `INSERT INTO node (id, kind, label, recorded_at, origin, review_state) ` +
                      `VALUES (?, 'artifact', ?, ?, 'system', 'accepted') ON CONFLICT(id) DO NOTHING`,
                  )
                  .run(artId, filePath, partTime)

                const patchMeta = partVal.hash ? JSON.stringify({ patch_hash: partVal.hash }) : null
                handle
                  .stmt(
                    `INSERT INTO edge (from_id, to_id, relation, origin, created_at, meta) ` +
                      `VALUES (?, ?, 'produced', 'system', ?, ?) ON CONFLICT(from_id, to_id, relation) WHERE revoked_at IS NULL DO NOTHING`,
                  )
                  .run(runNodeId, artId, partTime, patchMeta)
              }
            }
          }
        } else if (p.type === "file") {
          const source = partVal.source
          if (source?.type === "file" || source?.type === "symbol") {
            const filePath = source.path
            if (typeof filePath === "string" && filePath.trim()) {
              const artId = artifactId(filePath)
              handle
                .stmt(
                  `INSERT INTO node (id, kind, label, recorded_at, origin, review_state) ` +
                    `VALUES (?, 'artifact', ?, ?, 'system', 'accepted') ON CONFLICT(id) DO NOTHING`,
                )
                .run(artId, filePath, partTime)
            }
          } else if (source?.type === "resource" && source.uri) {
            const entNodeId = `ent:mcp:${source.uri}`
            handle
              .stmt(
                `INSERT INTO node (id, kind, label, recorded_at, authority, accession, origin, review_state) ` +
                  `VALUES (?, 'entity', ?, ?, 'mcp', ?, 'system', 'accepted') ON CONFLICT(id) DO NOTHING`,
              )
              .run(entNodeId, source.uri, partTime, source.uri)
          }
        }
      }
    })
  }

  export function deriveAll(handle: DatabaseClient.Handle): void {
    const messages = handle.stmt(`SELECT id FROM message`).all() as { id: string }[]
    for (const msg of messages) {
      deriveFromMessage(handle, msg.id)
    }
  }
}
