import z from "zod"

export const RnaSeqParameters = z.object({
  organism: z.string().min(1).default("Human"),
  reference: z.string().min(1).default("GRCh38"),
  sampleColumn: z.string().min(1).default("sample_id"),
  conditionColumn: z.string().min(1).default("condition"),
  control: z.string().min(1),
  treatment: z.string().min(1),
  batchColumn: z.string().optional(),
  adjustedPValue: z.number().min(0).max(1).default(0.05),
})

export type RnaSeqParameters = z.infer<typeof RnaSeqParameters>
export type ValidationCheck = {
  id: string
  label: string
  status: "pass" | "warning" | "fail"
  message: string
}

export const RNA_SEQ_WORKFLOW = {
  id: "rna-seq-differential-expression",
  version: "1.0.0",
  name: "RNA-seq differential expression",
  description: "Validate a count matrix and sample metadata before differential expression and pathway analysis.",
  inputs: [
    { key: "count_matrix", label: "Count matrix", type: "file", required: true },
    { key: "metadata", label: "Sample metadata", type: "file", required: true },
  ],
  steps: [
    "Inspect and validate inputs",
    "Normalize counts",
    "Run differential expression",
    "Generate PCA, volcano plot, and heatmap",
    "Run pathway enrichment",
    "Review evidence and warnings",
    "Package methods and provenance",
  ],
  outputs: ["deg_table", "pca_plot", "volcano_plot", "heatmap", "pathway_results", "methods", "provenance"],
} as const

export function parseDelimited(text: string): { headers: string[]; rows: Record<string, string>[] } {
  const first = text.split(/\r?\n/, 1)[0] ?? ""
  const delimiter = first.includes("\t") ? "\t" : ","
  const lines = text.split(/\r?\n/).filter((line) => line.trim().length > 0)
  if (lines.length === 0) return { headers: [], rows: [] }

  const split = (line: string) => {
    if (delimiter === "\t") return line.split("\t").map((value) => value.trim())
    const values: string[] = []
    let value = ""
    let quoted = false
    for (let i = 0; i < line.length; i++) {
      const char = line[i]
      if (char === '"') {
        if (quoted && line[i + 1] === '"') {
          value += '"'
          i++
        } else quoted = !quoted
      } else if (char === delimiter && !quoted) {
        values.push(value.trim())
        value = ""
      } else value += char
    }
    values.push(value.trim())
    return values
  }

  const headers = split(lines[0]).map((header) => header.replace(/^\uFEFF/, ""))
  const rows = lines.slice(1).map((line) => {
    const values = split(line)
    return Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""]))
  })
  return { headers, rows }
}

export function validateRnaSeqTables(input: {
  countText: string
  metadataText: string
  parameters: RnaSeqParameters
}): ValidationCheck[] {
  const checks: ValidationCheck[] = []
  const counts = parseDelimited(input.countText)
  const metadata = parseDelimited(input.metadataText)
  const params = input.parameters

  checks.push(
    counts.headers.length < 2
      ? { id: "count-shape", label: "Count matrix", status: "fail", message: "Expected a gene column and at least one sample column." }
      : { id: "count-shape", label: "Count matrix", status: "pass", message: `${counts.headers.length - 1} sample columns detected.` },
  )
  if (!metadata.headers.includes(params.sampleColumn))
    checks.push({ id: "sample-column", label: "Sample identifier", status: "fail", message: `Metadata column "${params.sampleColumn}" was not found.` })
  if (!metadata.headers.includes(params.conditionColumn))
    checks.push({ id: "condition-column", label: "Condition", status: "fail", message: `Metadata column "${params.conditionColumn}" was not found.` })
  if (checks.some((check) => check.status === "fail" && ["sample-column", "condition-column"].includes(check.id))) return checks

  const countSamples = new Set(counts.headers.slice(1).filter(Boolean))
  const metadataSamples = new Set(metadata.rows.map((row) => row[params.sampleColumn]).filter(Boolean))
  const missingMetadata = [...countSamples].filter((sample) => !metadataSamples.has(sample))
  const missingCounts = [...metadataSamples].filter((sample) => !countSamples.has(sample))
  checks.push(
    missingMetadata.length || missingCounts.length
      ? { id: "sample-ids", label: "Sample IDs", status: "fail", message: `${missingMetadata.length} count samples lack metadata; ${missingCounts.length} metadata samples lack counts.` }
      : { id: "sample-ids", label: "Sample IDs", status: "pass", message: `${countSamples.size} sample IDs match exactly.` },
  )

  const groups = new Map<string, number>()
  for (const row of metadata.rows) {
    const condition = row[params.conditionColumn]
    if (condition) groups.set(condition, (groups.get(condition) ?? 0) + 1)
  }
  const controlN = groups.get(params.control) ?? 0
  const treatmentN = groups.get(params.treatment) ?? 0
  if (!controlN || !treatmentN)
    checks.push({ id: "contrast", label: "Contrast", status: "fail", message: `Both "${params.control}" and "${params.treatment}" must occur in metadata.` })
  else if (controlN < 2 || treatmentN < 2)
    checks.push({ id: "replicates", label: "Replicates", status: "fail", message: `At least two replicates per group are required; found ${controlN} and ${treatmentN}.` })
  else if (controlN < 3 || treatmentN < 3)
    checks.push({ id: "replicates", label: "Replicates", status: "warning", message: `Only ${controlN} and ${treatmentN} replicates were found; three or more is preferable.` })
  else checks.push({ id: "replicates", label: "Replicates", status: "pass", message: `${controlN} control and ${treatmentN} treatment replicates found.` })

  if (!params.batchColumn) {
    checks.push({ id: "batch", label: "Batch design", status: "warning", message: "No batch column selected. Confirm that no known technical batch should be modeled." })
    return checks
  }
  if (!metadata.headers.includes(params.batchColumn)) {
    checks.push({ id: "batch", label: "Batch design", status: "fail", message: `Batch column "${params.batchColumn}" was not found.` })
    return checks
  }
  const byBatch = new Map<string, Set<string>>()
  for (const row of metadata.rows) {
    const batch = row[params.batchColumn]
    const condition = row[params.conditionColumn]
    if (!batch || !condition) continue
    const conditions = byBatch.get(batch) ?? new Set<string>()
    conditions.add(condition)
    byBatch.set(batch, conditions)
  }
  const confounded = byBatch.size > 1 && [...byBatch.values()].every((conditions) => conditions.size === 1)
  checks.push(
    confounded
      ? { id: "batch", label: "Batch design", status: "fail", message: "Batch is fully confounded with condition; the treatment effect cannot be separated from batch." }
      : { id: "batch", label: "Batch design", status: "pass", message: `${byBatch.size} batches can be included in the model.` },
  )
  return checks
}
