import path from "path"
import fs from "fs/promises"
import crypto from "crypto"
import Supermemory from "supermemory"
import z from "zod"
import { Global } from "../global"
import { Instance } from "../project/instance"
import { Log } from "../util/log"

// Supermemory is Griffin's durable context layer. Pinned notes are also kept
// locally so explicit user instructions remain available during an outage.
export namespace Memory {
  const log = Log.create({ service: "settings.memory" })

  export const Note = z.object({
    id: z.string(),
    text: z.string(),
    createdAt: z.number(),
  })
  export type Note = z.infer<typeof Note>

  export const Category = z.object({
    id: z.string(),
    name: z.string(),
    notes: z.array(Note),
  })
  export type Category = z.infer<typeof Category>

  export const Doc = z.object({
    enabled: z.boolean(),
    categories: z.array(Category),
  })
  export type Doc = z.infer<typeof Doc>

  export const Status = z.object({
    provider: z.literal("supermemory"),
    mode: z.enum(["local", "cloud"]),
    connected: z.boolean(),
    baseURL: z.string(),
  })
  export type Status = z.infer<typeof Status>

  export const State = Doc.extend({ status: Status })
  export type State = z.infer<typeof State>

  export const Scope = z.enum(["global", "project"])
  export type Scope = z.infer<typeof Scope>

  const root = path.join(Global.Path.data, "settings", "memory")
  const baseURL = process.env.SUPERMEMORY_BASE_URL ?? process.env.SUPERMEMORY_LOCAL_URL ?? "http://localhost:8787"
  const apiKey = process.env.SUPERMEMORY_API_KEY ?? "local"
  const mode: Status["mode"] = baseURL.includes("api.supermemory.ai") ? "cloud" : "local"
  const client = new Supermemory({ baseURL, apiKey, timeout: 4_000, maxRetries: 0 })
  let healthCache: { connected: boolean; checkedAt: number } | undefined

  function defaultDoc(): Doc {
    return {
      enabled: true,
      categories: [{ id: "about-you", name: "About you", notes: [] }],
    }
  }

  function projectKey(): string {
    return crypto.createHash("sha256").update(Instance.directory).digest("hex").slice(0, 16)
  }

  function containerTag(scope: Scope): string {
    return scope === "global" ? "griffin-global" : `griffin-project-${projectKey()}`
  }

  function fileFor(scope: Scope): string {
    if (scope === "global") return path.join(root, "global.json")
    return path.join(root, "projects", `${projectKey()}.json`)
  }

  async function read(scope: Scope): Promise<Doc> {
    const text = await Bun.file(fileFor(scope))
      .text()
      .catch(() => undefined)
    if (!text) return defaultDoc()
    try {
      const parsed = Doc.safeParse(JSON.parse(text))
      if (parsed.success) return parsed.data
    } catch (error) {
      log.error("failed to parse pinned memory", { scope, error })
    }
    return defaultDoc()
  }

  export async function status(force = false): Promise<Status> {
    if (!force && healthCache && Date.now() - healthCache.checkedAt < 30_000) {
      return { provider: "supermemory", mode, connected: healthCache.connected, baseURL }
    }
    let connected = false
    try {
      await fetch(baseURL, { signal: AbortSignal.timeout(700) })
      connected = true
    } catch {}
    healthCache = { connected, checkedAt: Date.now() }
    return { provider: "supermemory", mode, connected, baseURL }
  }

  export async function get(scope: Scope): Promise<State> {
    return { ...(await read(scope)), status: await status() }
  }

  export async function set(scope: Scope, doc: Doc): Promise<State> {
    const previous = await read(scope)
    const file = fileFor(scope)
    await fs.mkdir(path.dirname(file), { recursive: true })
    await Bun.write(file, JSON.stringify(doc, null, 2))

    const existing = new Set(previous.categories.flatMap((category) => category.notes.map((note) => note.id)))
    const additions = doc.categories.flatMap((category) =>
      category.notes
        .filter((note) => note.text.trim() && !existing.has(note.id))
        .map((note) => ({ category: category.name, note })),
    )
    if (doc.enabled && additions.length > 0) {
      void Promise.allSettled(
        additions.map(({ category, note }) =>
          client.add({
            content: note.text.trim(),
            containerTag: containerTag(scope),
            customId: `griffin-note-${scope}-${note.id}`.replace(/[^a-zA-Z0-9_.-]/g, "-").slice(0, 100),
            entityContext: "Pinned context for Griffin, a life-science research companion.",
            metadata: { source: "griffin-pinned-note", category, scope },
          }),
        ),
      ).then((results) => {
        if (results.some((result) => result.status === "rejected")) healthCache = undefined
      })
    }
    return { ...doc, status: await status() }
  }

  export async function remember(content: string, sessionID?: string): Promise<void> {
    const text = content.trim()
    if (!text) return
    const project = await read("project")
    if (!project.enabled || !(await status()).connected) return
    const digest = crypto.createHash("sha256").update(`${sessionID ?? "session"}\n${text}`).digest("hex").slice(0, 24)
    await client
      .add({
        content: text,
        containerTag: containerTag("project"),
        customId: `griffin-turn-${digest}`,
        entityContext: "Research context from a Griffin life-science workspace.",
        metadata: { source: "griffin-conversation", ...(sessionID ? { sessionID } : {}) },
      })
      .catch((error) => {
        healthCache = undefined
        log.warn("failed to store Supermemory context", { error })
      })
  }

  async function supermemoryBlock(scope: Scope, query?: string): Promise<string | undefined> {
    const profile = await client.profile({ containerTag: containerTag(scope), ...(query ? { q: query } : {}) })
    const memories = [...profile.profile.static, ...profile.profile.dynamic]
      .map((item) => item.trim())
      .filter(Boolean)
      .slice(0, 24)
    if (memories.length === 0) return
    return [
      `<supermemory scope="${scope}">`,
      "Relevant durable context recalled by Supermemory:",
      ...memories.map((item) => `- ${item}`),
      "</supermemory>",
    ].join("\n")
  }

  export async function recall(query?: string): Promise<string[]> {
    const blocks: string[] = []

    for (const scope of Scope.options) {
      const doc = await read(scope).catch(() => undefined)
      if (!doc?.enabled) continue
      const lines = doc.categories.flatMap((category) => {
        const notes = category.notes.map((note) => note.text.trim()).filter(Boolean)
        return notes.length > 0 ? [`## ${category.name}`, ...notes.map((note) => `- ${note}`)] : []
      })
      if (lines.length > 0) {
        blocks.push(
          [
            `<memory scope="${scope}">`,
            "Pinned context saved by the user:",
            ...lines,
            "</memory>",
          ].join("\n"),
        )
      }
    }

    if (!(await status()).connected) return blocks
    const recalled = await Promise.all(
      Scope.options.map((scope) => supermemoryBlock(scope, query).catch((error) => {
        healthCache = undefined
        log.warn("failed to recall Supermemory context", { scope, error })
        return undefined
      })),
    )
    return [...blocks, ...recalled.filter((block): block is string => !!block)]
  }
}
