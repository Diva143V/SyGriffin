import { createHash, randomUUID } from "crypto"
import { createReadStream } from "fs"
import path from "path"
import z from "zod"
import { Instance } from "@/project/instance"
import { Storage } from "@/storage/storage"
import { RNA_SEQ_WORKFLOW, RnaSeqParameters, validateRnaSeqTables } from "./workflows/rna-seq"

export namespace ResearchRun {
  export const Status = z.enum(["blocked", "awaiting_approval", "ready", "running", "completed", "failed", "cancelled"])
  export const InputFile = z.object({ key: z.string(), path: z.string(), checksum: z.string(), size: z.number() })
  export const Check = z.object({
    id: z.string(),
    label: z.string(),
    status: z.enum(["pass", "warning", "fail"]),
    message: z.string(),
  })
  export const Info = z.object({
    id: z.string().startsWith("run_"),
    projectID: z.string(),
    sessionID: z.string().optional(),
    workflow: z.object({ id: z.string(), version: z.string(), name: z.string() }),
    status: Status,
    progress: z.object({ current: z.number(), total: z.number(), step: z.string() }),
    inputs: InputFile.array(),
    parameters: z.record(z.string(), z.unknown()),
    plan: z.string().array(),
    checks: Check.array(),
    logs: z.object({ time: z.number(), level: z.enum(["info", "warning", "error"]), message: z.string() }).array(),
    outputs: z.object({ key: z.string(), path: z.string(), kind: z.string() }).array(),
    warnings: z.string().array(),
    approvals: z.object({ time: z.number(), decision: z.enum(["approved", "rejected"]), note: z.string().optional() }).array(),
    time: z.object({ created: z.number(), updated: z.number(), started: z.number().optional(), completed: z.number().optional() }),
  })
  export type Info = z.infer<typeof Info>

  export const Launch = z.object({
    workflowID: z.literal(RNA_SEQ_WORKFLOW.id),
    sessionID: z.string().optional(),
    inputs: z.object({ count_matrix: z.string().min(1), metadata: z.string().min(1) }),
    parameters: RnaSeqParameters,
  })
  export type Launch = z.infer<typeof Launch>
  export const Decision = z.object({ note: z.string().max(1000).optional() })

  export function workflows() {
    return [RNA_SEQ_WORKFLOW]
  }

  async function checksum(file: string) {
    const hash = createHash("sha256")
    await new Promise<void>((resolve, reject) => {
      const stream = createReadStream(file)
      stream.on("data", (chunk) => hash.update(chunk))
      stream.on("error", reject)
      stream.on("end", resolve)
    })
    return hash.digest("hex")
  }

  async function inspect(key: string, candidate: string) {
    const absolute = path.resolve(Instance.directory, candidate)
    if (!Instance.containsPath(absolute)) throw new Error(`Input file must be inside this project: ${candidate}`)
    const file = Bun.file(absolute)
    if (!(await file.exists())) throw new Error(`Input file does not exist: ${candidate}`)
    return {
      key,
      path: path.relative(Instance.directory, absolute).replaceAll("\\", "/"),
      checksum: await checksum(absolute),
      size: file.size,
      absolute,
    }
  }

  export async function validate(input: Launch) {
    const parsed = Launch.parse(input)
    const count = await inspect("count_matrix", parsed.inputs.count_matrix)
    const metadata = await inspect("metadata", parsed.inputs.metadata)
    if (metadata.size > 8 * 1024 * 1024) throw new Error("Metadata exceeds the 8 MB validation limit.")
    const [countText, metadataText] = await Promise.all([
      Bun.file(count.absolute).slice(0, 256 * 1024).text(),
      Bun.file(metadata.absolute).text(),
    ])
    const checks = validateRnaSeqTables({ countText, metadataText, parameters: parsed.parameters })
    return {
      workflow: { id: RNA_SEQ_WORKFLOW.id, version: RNA_SEQ_WORKFLOW.version, name: RNA_SEQ_WORKFLOW.name },
      inputs: [count, metadata].map(({ absolute: _absolute, ...file }) => file),
      parameters: parsed.parameters,
      plan: [...RNA_SEQ_WORKFLOW.steps],
      checks,
      valid: !checks.some((check) => check.status === "fail"),
    }
  }

  export async function create(input: Launch) {
    const preview = await validate(input)
    const now = Date.now()
    const run: Info = {
      id: `run_${now.toString(36)}_${randomUUID().replaceAll("-", "").slice(0, 12)}`,
      projectID: Instance.project.id,
      sessionID: input.sessionID,
      workflow: preview.workflow,
      status: preview.valid ? "awaiting_approval" : "blocked",
      progress: { current: 0, total: preview.plan.length, step: preview.valid ? "Awaiting plan approval" : "Input validation failed" },
      inputs: preview.inputs,
      parameters: preview.parameters,
      plan: preview.plan,
      checks: preview.checks,
      logs: [{ time: now, level: "info", message: "Run record created after input validation." }],
      outputs: [],
      warnings: preview.checks.filter((check) => check.status === "warning").map((check) => check.message),
      approvals: [],
      time: { created: now, updated: now },
    }
    await Storage.write(["research_run", Instance.project.id, run.id], run)
    return run
  }

  export async function list() {
    const keys = await Storage.list(["research_run", Instance.project.id])
    const runs = await Promise.all(keys.map((key) => Storage.read<Info>(key)))
    return runs.sort((a, b) => b.time.updated - a.time.updated)
  }

  export async function get(id: string) {
    return Storage.read<Info>(["research_run", Instance.project.id, id])
  }

  async function update(id: string, fn: (run: Info) => void) {
    return Storage.update<Info>(["research_run", Instance.project.id, id], (run) => {
      fn(run)
      run.time.updated = Date.now()
    })
  }

  export async function approve(id: string, note?: string) {
    return update(id, (run) => {
      if (run.status !== "awaiting_approval") throw new Error("Only a validated run awaiting approval can be approved.")
      run.status = "ready"
      run.progress.step = "Ready for execution"
      run.approvals.push({ time: Date.now(), decision: "approved", note })
      run.logs.push({ time: Date.now(), level: "info", message: "Analysis plan approved. Run is ready for an execution worker." })
    })
  }

  export async function cancel(id: string) {
    return update(id, (run) => {
      if (["completed", "cancelled"].includes(run.status)) throw new Error(`Cannot cancel a ${run.status} run.`)
      run.status = "cancelled"
      run.progress.step = "Cancelled"
      run.logs.push({ time: Date.now(), level: "warning", message: "Run cancelled by the researcher." })
    })
  }

  export async function retry(id: string) {
    return update(id, (run) => {
      if (!["failed", "cancelled"].includes(run.status)) throw new Error("Only failed or cancelled runs can be retried.")
      const failed = run.checks.some((check) => check.status === "fail")
      run.status = failed ? "blocked" : "awaiting_approval"
      run.progress = { current: 0, total: run.plan.length, step: failed ? "Input validation failed" : "Awaiting plan approval" }
      run.logs.push({ time: Date.now(), level: "info", message: "Run reset for review and retry." })
    })
  }
}
