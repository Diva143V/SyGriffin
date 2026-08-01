import { DatabaseClient } from "../client"
import { Derive } from "./derive"
import { Log } from "../../../util/log"

export namespace GraphStore {
  const log = Log.create({ service: "storage.db.graph.store" })

  export interface NodeRow {
    id: string
    kind: string
    subtype?: string | null
    label: string
    recorded_at: number
    entity_type?: string | null
    entity_id?: string | null
    content_hash?: string | null
    hash_algo?: string | null
    accession?: string | null
    authority?: string | null
    origin: "system" | "agent" | "user"
    confidence?: number | null
    source_node_id?: string | null
    review_state?: "unreviewed" | "accepted" | "rejected"
    merged_into?: string | null
    derived_at?: number | null
    meta?: string | null
  }

  export interface EdgeRow {
    from_id: string
    to_id: string
    relation: string
    origin: "system" | "agent" | "user"
    confidence?: number | null
    created_at: number
    revoked_at?: number | null
    meta?: string | null
  }

  export function recordNode(handle: DatabaseClient.Handle, node: NodeRow): void {
    handle
      .stmt(
        `INSERT INTO node (id, kind, subtype, label, recorded_at, entity_type, entity_id, content_hash, hash_algo, accession, authority, origin, confidence, source_node_id, review_state, merged_into, derived_at, meta) ` +
          `VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ` +
          `ON CONFLICT(id) DO UPDATE SET ` +
          `kind=excluded.kind, subtype=excluded.subtype, label=excluded.label, recorded_at=excluded.recorded_at, ` +
          `entity_type=excluded.entity_type, entity_id=excluded.entity_id, content_hash=excluded.content_hash, hash_algo=excluded.hash_algo, ` +
          `accession=excluded.accession, authority=excluded.authority, origin=excluded.origin, confidence=excluded.confidence, ` +
          `source_node_id=excluded.source_node_id, review_state=excluded.review_state, merged_into=excluded.merged_into, ` +
          `derived_at=excluded.derived_at, meta=excluded.meta`,
      )
      .run(
        node.id,
        node.kind,
        node.subtype ?? null,
        node.label,
        node.recorded_at,
        node.entity_type ?? null,
        node.entity_id ?? null,
        node.content_hash ?? null,
        node.hash_algo ?? null,
        node.accession ?? null,
        node.authority ?? null,
        node.origin,
        node.confidence ?? null,
        node.source_node_id ?? null,
        node.review_state ?? "unreviewed",
        node.merged_into ?? null,
        node.derived_at ?? null,
        node.meta ?? null,
      )
  }

  export function linkEdge(handle: DatabaseClient.Handle, edge: EdgeRow): void {
    handle
      .stmt(
        `INSERT INTO edge (from_id, to_id, relation, origin, confidence, created_at, revoked_at, meta) ` +
          `VALUES (?, ?, ?, ?, ?, ?, ?, ?) ` +
          `ON CONFLICT(from_id, to_id, relation) WHERE revoked_at IS NULL DO NOTHING`,
      )
      .run(
        edge.from_id,
        edge.to_id,
        edge.relation,
        edge.origin,
        edge.confidence ?? null,
        edge.created_at,
        edge.revoked_at ?? null,
        edge.meta ?? null,
      )
  }

  export function rebuild(handle: DatabaseClient.Handle): { systemNodes: number; systemEdges: number } {
    let systemNodes = 0
    let systemEdges = 0

    handle.tx(() => {
      // Delete system edges and system nodes
      handle.stmt(`DELETE FROM edge WHERE origin = 'system'`).run()
      handle.stmt(`DELETE FROM node WHERE origin = 'system'`).run()

      // Re-derive workspace system events
      Derive.deriveAll(handle)

      systemNodes = (handle.stmt(`SELECT count(*) as n FROM node WHERE origin = 'system'`).get() as any)?.n ?? 0
      systemEdges = (handle.stmt(`SELECT count(*) as n FROM edge WHERE origin = 'system'`).get() as any)?.n ?? 0
    })

    log.info("rebuild completed", { systemNodes, systemEdges })
    return { systemNodes, systemEdges }
  }
}
