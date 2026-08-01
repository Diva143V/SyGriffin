import { FTS } from "../fts"
import { DatabaseClient } from "../client"

export namespace GraphQuery {
  export interface LineageOptions {
    nodeId: string
    direction?: "ancestors" | "descendants" | "both"
    maxDepth?: number
    limit?: number
  }

  export interface LineageResult {
    nodes: any[]
    edges: any[]
  }

  export function lineage(handle: DatabaseClient.Handle, opts: LineageOptions): LineageResult {
    const direction = opts.direction ?? "ancestors"
    const maxDepth = opts.maxDepth ?? 6
    const limit = opts.limit ?? 500

    let nodeSql = ""
    if (direction === "ancestors") {
      nodeSql = /* sql */ `
        WITH RECURSIVE anc(id, depth) AS (
          SELECT ?, 0
          UNION ALL
          SELECT e.to_id, a.depth + 1
          FROM edge e
          JOIN anc a ON e.from_id = a.id
          WHERE a.depth < ? AND e.revoked_at IS NULL
        )
        SELECT DISTINCT n.* FROM node n JOIN anc a ON n.id = a.id LIMIT ?
      `
    } else if (direction === "descendants") {
      nodeSql = /* sql */ `
        WITH RECURSIVE desc(id, depth) AS (
          SELECT ?, 0
          UNION ALL
          SELECT e.from_id, d.depth + 1
          FROM edge e
          JOIN desc d ON e.to_id = d.id
          WHERE d.depth < ? AND e.revoked_at IS NULL
        )
        SELECT DISTINCT n.* FROM node n JOIN desc d ON n.id = d.id LIMIT ?
      `
    } else {
      nodeSql = /* sql */ `
        WITH RECURSIVE comp(id, depth) AS (
          SELECT ?, 0
          UNION ALL
          SELECT CASE WHEN e.from_id = c.id THEN e.to_id ELSE e.from_id END, c.depth + 1
          FROM edge e
          JOIN comp c ON (e.from_id = c.id OR e.to_id = c.id)
          WHERE c.depth < ? AND e.revoked_at IS NULL
        )
        SELECT DISTINCT n.* FROM node n JOIN comp c ON n.id = c.id LIMIT ?
      `
    }

    const nodes = handle.stmt(nodeSql).all(opts.nodeId, maxDepth, limit) as any[]
    if (nodes.length === 0) return { nodes: [], edges: [] }

    const nodeIds = new Set(nodes.map((n) => n.id))
    const placeholders = Array.from(nodeIds).map(() => "?").join(",")
    const edgesSql = `SELECT * FROM edge WHERE from_id IN (${placeholders}) AND to_id IN (${placeholders}) AND revoked_at IS NULL`
    const edges = handle.stmt(edgesSql).all(...Array.from(nodeIds), ...Array.from(nodeIds)) as any[]

    return { nodes, edges }
  }

  export function neighbors(
    handle: DatabaseClient.Handle,
    nodeId: string,
    relation?: string,
    kind?: string,
    limit = 100,
  ): LineageResult {
    let edgeSql = `SELECT * FROM edge WHERE (from_id = ? OR to_id = ?) AND revoked_at IS NULL`
    const params: any[] = [nodeId, nodeId]
    if (relation) {
      edgeSql += ` AND relation = ?`
      params.push(relation)
    }
    edgeSql += ` LIMIT ?`
    params.push(limit)

    const edges = handle.stmt(edgeSql).all(...params) as any[]
    const nodeIds = new Set<string>([nodeId])
    for (const e of edges) {
      nodeIds.add(e.from_id)
      nodeIds.add(e.to_id)
    }

    const placeholders = Array.from(nodeIds).map(() => "?").join(",")
    let nodeSql = `SELECT * FROM node WHERE id IN (${placeholders})`
    if (kind) {
      nodeSql += ` AND kind = '${kind}'`
    }

    const nodes = handle.stmt(nodeSql).all(...Array.from(nodeIds)) as any[]
    return { nodes, edges }
  }

  export function search(handle: DatabaseClient.Handle, queryStr: string, limit = 50): any[] {
    const q = `%${queryStr.trim()}%`
    const sql = `
      SELECT DISTINCT n.* FROM node n
      LEFT JOIN alias a ON n.id = a.node_id
      WHERE n.label LIKE ? OR n.accession LIKE ? OR a.normalized LIKE ? OR a.alias LIKE ?
      LIMIT ?
    `
    return handle.stmt(sql).all(q, q, q.toLowerCase(), q, limit) as any[]
  }

  export interface ContentHit {
    part_id: string
    session_id: string | null
    message_id: string
    type: string | null
    tool: string | null
    snippet: string
  }

  /**
   * Full-text search over message content.
   *
   * Complements `search()`, which matches node labels, accessions and aliases —
   * i.e. things already promoted into the graph. This reaches the prose the
   * workspace actually produced, which is where most "where did I see that"
   * questions live.
   */
  export function searchContent(handle: DatabaseClient.Handle, queryStr: string, limit = 25): ContentHit[] {
    const hits = FTS.search(handle, queryStr, limit)
    if (hits.length === 0) return []

    const byId = new Map(hits.map((h) => [h.id, h.snippet]))
    const placeholders = hits.map(() => "?").join(", ")
    const rows = handle
      .stmt(`SELECT id, session_id, message_id, type, tool FROM part WHERE id IN (${placeholders})`)
      .all(...hits.map((h) => h.id)) as any[]

    // Preserve FTS rank order; the IN-clause lookup does not guarantee it.
    const order = new Map(hits.map((h, i) => [h.id, i]))
    return rows
      .sort((a, b) => (order.get(a.id) ?? 0) - (order.get(b.id) ?? 0))
      .map((r) => ({
        part_id: r.id,
        session_id: r.session_id,
        message_id: r.message_id,
        type: r.type,
        tool: r.tool,
        snippet: byId.get(r.id) ?? "",
      }))
  }
}
