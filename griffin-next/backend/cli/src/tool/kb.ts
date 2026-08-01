import z from "zod"
import { Tool } from "./tool"
import { DatabaseClient } from "../storage/db/client"
import { GraphStore } from "../storage/db/graph/store"
import { Vocabulary } from "../storage/db/graph/vocabulary"
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
  description: "Create or resolve a biological entity node in the KB against an accession and authority.",
  parameters: z.object({
    name: z.string().describe("Canonical name of the entity"),
    authority: z.string().describe("Accession namespace e.g. 'hgnc' | 'uniprot' | 'chebi' | 'ensembl'"),
    accession: z.string().describe("Accession ID in authority namespace e.g. 'ENSG00000141510'"),
    subtype: z.string().optional().default("gene").describe("Entity subtype e.g. 'gene' | 'protein' | 'compound'"),
  }),
  async execute(params) {
    const handle = DatabaseClient.writer()
    const nodeId = `ent:${params.authority.toLowerCase()}:${params.accession}`

    GraphStore.recordNode(handle, {
      id: nodeId,
      kind: "entity",
      subtype: params.subtype,
      label: params.name,
      recorded_at: Date.now(),
      authority: params.authority.toLowerCase(),
      accession: params.accession,
      origin: "agent",
      review_state: "accepted",
    })

    return {
      title: `Entity ${nodeId}`,
      output: `Resolved entity node ${nodeId} (${params.name}) under ${params.authority}:${params.accession}.`,
      metadata: { id: nodeId, authority: params.authority, accession: params.accession },
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
