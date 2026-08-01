import z from "zod"
import { Tool } from "./tool"
import { DatabaseClient } from "../storage/db/client"
import { GraphStore } from "../storage/db/graph/store"
import { Vocabulary } from "../storage/db/graph/vocabulary"
import { EntityResolver } from "../storage/db/graph/resolve"
import { Hash } from "../storage/db/hash"

export const KbAssertTool = Tool.define("kb_assert", {
  description: [
    "Assert a claim node in the knowledge base.",
    "Requires a source_node_id (e.g. paper or document read) and a confidence score.",
    "Claims land with review_state='unreviewed' until audited.",
  ].join("\n"),
  parameters: z.object({
    claim: z.string().describe("The assertion text"),
    source_node_id: z.string().describe("The ID of the source node read to assert this claim"),
    confidence: z.number().min(0).max(1).describe("Confidence score between 0.0 and 1.0"),
    subtype: z.string().optional().default("assertion").describe("Subtype e.g. 'assertion' | 'hypothesis'"),
    meta: z.record(z.string(), z.any()).optional().describe("Additional structured metadata"),
  }),
  async execute(params, ctx) {
    const handle = DatabaseClient.writer()
    const payload = { claim: params.claim, source_node_id: params.source_node_id, sessionID: ctx.sessionID }
    const { hash } = Hash.contentIdV2(payload)
    const nodeId = `clm:${hash}`

    GraphStore.recordNode(handle, {
      id: nodeId,
      kind: "claim",
      subtype: params.subtype,
      label: params.claim,
      recorded_at: Date.now(),
      content_hash: hash,
      hash_algo: "sha256-16-json-v2",
      origin: "agent",
      confidence: params.confidence,
      source_node_id: params.source_node_id,
      review_state: "unreviewed",
      meta: params.meta ? JSON.stringify(params.meta) : null,
    })

    // Link claim to source node via derived-from or supports
    GraphStore.linkEdge(handle, {
      from_id: nodeId,
      to_id: params.source_node_id,
      relation: "derived-from",
      origin: "agent",
      confidence: params.confidence,
      created_at: Date.now(),
    })

    return {
      title: `Asserted claim: ${nodeId}`,
      output: `Asserted claim node ${nodeId} with confidence ${params.confidence}.`,
      metadata: { id: nodeId, confidence: params.confidence },
    }
  },
})

export const KbEntityTool = Tool.define("kb_entity", {
  description: [
    "Resolve a biological entity to a canonical identity and record it in the knowledge base.",
    "The accession is VERIFIED against the source database (Ensembl, UniProt, ChEBI, PubMed, ...) before",
    "the entity is trusted. Give the accession if you know it, otherwise give the name and let it resolve.",
    "An entity that cannot be verified is still recorded, but stays unreviewed and out of default scope.",
  ].join("\n"),
  parameters: z.object({
    name: z.string().describe("Name or symbol of the entity, e.g. 'TP53'"),
    authority: z
      .string()
      .describe(`Accession namespace. One of: ${EntityResolver.authorities().join(", ")}`),
    accession: z
      .string()
      .optional()
      .describe("Accession in that namespace if known, e.g. 'ENSG00000141510'. Omit to resolve by name."),
    subtype: z.string().optional().describe("Entity subtype; inferred from the authority when omitted"),
  }),
  async execute(params, ctx) {
    const handle = DatabaseClient.writer()

    // Resolve rather than trust. Recording an unverified accession as
    // `accepted` puts it in default query scope looking authoritative, which
    // is the exact failure the trust columns exist to prevent — a wrong
    // identity silently merges two different things for every later query.
    const res = await EntityResolver.resolveAndRecord(handle, {
      authority: params.authority,
      query: params.accession ?? params.name,
      name: params.name,
      subtype: params.subtype,
      signal: ctx.abort,
    })

    const explain: Record<EntityResolver.Status, string> = {
      resolved: `Verified against ${params.authority} and accepted.`,
      "no-match": `${params.authority} returned no exact match. Recorded as unreviewed — check the spelling or the namespace.`,
      unavailable: `Could not reach ${params.authority}. Recorded as unreviewed and queued for retry; absence is NOT confirmed.`,
      "unknown-authority": `Unknown authority "${params.authority}". Recorded as unreviewed. Known authorities: ${EntityResolver.authorities().join(", ")}.`,
    }

    return {
      title: `Entity ${res.nodeId}`,
      output: [
        `**${params.name}** → \`${res.nodeId}\``,
        res.accession ? `accession: ${params.authority}:${res.accession}` : "accession: none",
        explain[res.status],
      ].join("\n"),
      metadata: { id: res.nodeId, status: res.status, accession: res.accession },
    }
  },
})

export const KbVocabularyProposeTool = Tool.define("kb_vocabulary_propose", {
  description: "Propose a new subtype classification in the knowledge base vocabulary.",
  parameters: z.object({
    subtype: z.string().describe("Proposed subtype token (e.g. 'tcr-clonotype')"),
    kind: z.enum(["entity", "source", "artifact", "claim"]).describe("Node kind this subtype applies to"),
    definition: z.string().optional().describe("Definition of the proposed subtype"),
    example_node_id: z.string().optional().describe("Optional example node id using this subtype"),
  }),
  async execute(params) {
    const handle = DatabaseClient.writer()
    const res = Vocabulary.propose(
      handle,
      params.subtype,
      params.kind,
      params.definition,
      undefined,
      params.example_node_id,
    )

    return {
      title: `Vocabulary Subtype: ${res.name}`,
      output: res.reused
        ? `Subtype "${params.subtype}" normalized and reused existing term "${res.name}" (status: ${res.status}).`
        : `Proposed new subtype "${res.name}" under kind "${params.kind}" (status: proposed).`,
      metadata: { name: res.name, status: res.status, reused: res.reused },
    }
  },
})

export const KbTools = [KbAssertTool, KbEntityTool, KbVocabularyProposeTool]
