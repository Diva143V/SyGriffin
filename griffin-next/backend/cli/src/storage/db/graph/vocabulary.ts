import { DatabaseClient } from "../client"
import { Log } from "../../../util/log"

export namespace Vocabulary {
  const log = Log.create({ service: "storage.db.graph.vocabulary" })

  export function normalize(subtype: string): string {
    let s = subtype.toLowerCase().trim().replace(/[\s_]+/g, "-")
    if (s.endsWith("s") && !s.endsWith("ss") && s.length > 3) {
      s = s.slice(0, -1)
    }
    return s
  }

  export function propose(
    handle: DatabaseClient.Handle,
    rawSubtype: string,
    kind: string,
    definition?: string,
    authority?: string,
    firstSeenNodeId?: string,
  ): { name: string; status: string; reused: boolean } {
    const name = normalize(rawSubtype)

    // Every lookup is scoped by kind: the table is keyed on (kind, name), and
    // 'dataset' legitimately exists under both 'entity' and 'artifact'.
    const existing = handle
      .stmt(`SELECT name, status, merged_into FROM vocabulary WHERE kind = ? AND name = ?`)
      .get(kind, name) as any

    if (existing) {
      const activeName = existing.merged_into ?? existing.name
      handle
        .stmt(`UPDATE vocabulary SET usage_count = usage_count + 1 WHERE kind = ? AND name = ?`)
        .run(kind, activeName)
      const status = existing.merged_into
        ? ((handle.stmt(`SELECT status FROM vocabulary WHERE kind = ? AND name = ?`).get(kind, activeName) as any)
            ?.status ?? existing.status)
        : existing.status
      checkAutoPromotion(handle, kind, activeName)
      return { name: activeName, status, reused: true }
    }

    handle
      .stmt(
        `INSERT INTO vocabulary (name, kind, status, definition, authority, first_seen_node, usage_count, created_at) ` +
          `VALUES (?, ?, 'proposed', ?, ?, ?, 1, ?)`,
      )
      .run(name, kind, definition ?? null, authority ?? null, firstSeenNodeId ?? null, Date.now())

    log.info("proposed new subtype", { name, kind })
    return { name, status: "proposed", reused: false }
  }

  /** Distinct nodes required before a proposed subtype is auto-accepted. */
  export const AUTO_PROMOTE_THRESHOLD = 10

  export function checkAutoPromotion(handle: DatabaseClient.Handle, kind: string, name: string): boolean {
    const row = handle
      .stmt(`SELECT status FROM vocabulary WHERE kind = ? AND name = ?`)
      .get(kind, name) as any
    if (!row || row.status !== "proposed") return false

    // Count nodes of this kind only — a subtype name shared across kinds must
    // not have one kind's usage promote another's.
    const distinctNodes =
      (
        handle
          .stmt(
            `SELECT count(DISTINCT id) AS n FROM node WHERE kind = ? AND subtype = ? AND review_state != 'rejected'`,
          )
          .get(kind, name) as any
      )?.n ?? 0

    if (distinctNodes < AUTO_PROMOTE_THRESHOLD) return false

    handle
      .stmt(
        `UPDATE vocabulary SET status = 'accepted', promoted_by = 'auto', promoted_at = ? WHERE kind = ? AND name = ?`,
      )
      .run(Date.now(), kind, name)
    log.info("auto-promoted vocabulary subtype", { kind, name, distinctNodes })
    return true
  }

  /** Maintainer promotion or rejection, recorded distinctly from the auto path. */
  export function setStatus(
    handle: DatabaseClient.Handle,
    kind: string,
    name: string,
    status: "accepted" | "rejected",
    by = "maintainer",
  ): void {
    handle
      .stmt(`UPDATE vocabulary SET status = ?, promoted_by = ?, promoted_at = ? WHERE kind = ? AND name = ?`)
      .run(status, by, Date.now(), kind, normalize(name))
  }

  /** Proposed subtypes by usage, surfaced in `griffin db status` so drift is visible. */
  export function proposed(handle: DatabaseClient.Handle): { kind: string; name: string; usage_count: number }[] {
    return handle
      .stmt(`SELECT kind, name, usage_count FROM vocabulary WHERE status = 'proposed' ORDER BY usage_count DESC, name`)
      .all() as any
  }

  export function merge(handle: DatabaseClient.Handle, kind: string, fromName: string, intoName: string): void {
    handle.tx(() => {
      const normFrom = normalize(fromName)
      const normInto = normalize(intoName)
      handle
        .stmt(`UPDATE vocabulary SET status = 'merged', merged_into = ? WHERE kind = ? AND name = ?`)
        .run(normInto, kind, normFrom)
      handle.stmt(`UPDATE node SET subtype = ? WHERE kind = ? AND subtype = ?`).run(normInto, kind, normFrom)
    })
  }
}
