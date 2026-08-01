import { DatabaseClient } from "../client"
import { GraphStore } from "./store"
import { Log } from "../../../util/log"

export namespace EntityResolver {
  const log = Log.create({ service: "storage.db.graph.resolve" })

  export interface ResolveOptions {
    authority: string
    query: string
    name: string
    subtype?: string
  }

  export async function resolveAndRecord(
    handle: DatabaseClient.Handle,
    opts: ResolveOptions,
  ): Promise<{ nodeId: string; resolved: boolean; accession: string | null }> {
    const authority = opts.authority.toLowerCase().trim()
    const queryStr = opts.query.trim()

    let accession: string | null = null
    let resolved = false

    try {
      // Basic identifier format validation per authority
      if (authority === "hgnc" || authority === "ensembl" || authority === "uniprot" || authority === "chebi" || authority === "pubmed") {
        if (queryStr.match(/^(ENSG\d+|RS\d+|VCV\d+|[A-Z0-9_-]+)$/i)) {
          accession = queryStr.toUpperCase()
          resolved = true
        }
      }
    } catch (e) {
      log.warn("connector lookup error during resolution", { authority, query: queryStr, error: e })
    }

    const nodeId = accession ? `ent:${authority}:${accession}` : `ent:unresolved:${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
    const reviewState = resolved ? "accepted" : "unreviewed"

    GraphStore.recordNode(handle, {
      id: nodeId,
      kind: "entity",
      subtype: opts.subtype ?? "gene",
      label: opts.name,
      recorded_at: Date.now(),
      authority: accession ? authority : null,
      accession,
      origin: "agent",
      review_state: reviewState,
      meta: JSON.stringify({ resolution_attempted_at: Date.now() }),
    })

    return { nodeId, resolved, accession }
  }
}
