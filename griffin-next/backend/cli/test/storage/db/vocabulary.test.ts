import { afterEach, describe, expect, test } from "bun:test"
import os from "os"
import path from "path"
import fs from "fs/promises"
import { DatabaseClient } from "../../../src/storage/db/client"
import { Schema } from "../../../src/storage/db/schema"
import { Vocabulary } from "../../../src/storage/db/graph/vocabulary"

// Databases go to os.tmpdir(), never into the repo — test artifacts written
// under test/ are not gitignored and get committed by a directory-wide add.
const dirs: string[] = []

async function db() {
  const dir = await fs.mkdtemp(path.join(os.tmpdir(), "griffin-vocab-"))
  dirs.push(dir)
  const handle = DatabaseClient.create(path.join(dir, "vocab.db"))
  Schema.migrate(handle)
  return handle
}

afterEach(async () => {
  await Promise.all(dirs.splice(0).map((d) => fs.rm(d, { recursive: true, force: true }).catch(() => {})))
})

describe("normalize", () => {
  test("lowercases, hyphenates, and singularizes", () => {
    expect(Vocabulary.normalize("Gene Expression")).toBe("gene-expression")
    expect(Vocabulary.normalize("gene-expressions")).toBe("gene-expression")
    expect(Vocabulary.normalize("gene_expression")).toBe("gene-expression")
    expect(Vocabulary.normalize("  Gene Expression  ")).toBe("gene-expression")
  })

  test("does not strip a trailing s from short or double-s words", () => {
    expect(Vocabulary.normalize("mass")).toBe("mass")
    expect(Vocabulary.normalize("gas")).toBe("gas")
  })
})

describe("core seed", () => {
  test("ships with the schema so common subtypes are never 'proposed'", async () => {
    const h = await db()
    const rows = h.db.query("SELECT kind, name, status FROM vocabulary ORDER BY kind, name").all() as any[]

    expect(rows.length).toBeGreaterThan(0)
    expect(rows.every((r) => r.status === "core")).toBeTrue()
    expect(rows.some((r) => r.kind === "entity" && r.name === "gene")).toBeTrue()
    expect(rows.some((r) => r.kind === "claim" && r.name === "review")).toBeTrue()
  })

  test("created_at is fixed at 0 so a rebuild stays byte-identical", async () => {
    const h = await db()
    const distinct = h.db.query("SELECT DISTINCT created_at AS t FROM vocabulary").all() as any[]
    expect(distinct).toEqual([{ t: 0 }])
  })

  test("proposing a core subtype reuses it rather than creating a duplicate", async () => {
    const h = await db()
    const res = Vocabulary.propose(h, "Genes", "entity")

    expect(res.name).toBe("gene")
    expect(res.reused).toBeTrue()
    expect(res.status).toBe("core")
  })
})

describe("propose", () => {
  test("near-miss spellings collapse to one row (acceptance criterion 8)", async () => {
    const h = await db()

    expect(Vocabulary.propose(h, "Gene Expression", "entity").reused).toBeFalse()
    expect(Vocabulary.propose(h, "gene-expressions", "entity").reused).toBeTrue()
    expect(Vocabulary.propose(h, "gene_expression ", "entity").reused).toBeTrue()

    const rows = h.db
      .query("SELECT name, usage_count FROM vocabulary WHERE kind = 'entity' AND status = 'proposed'")
      .all() as any[]
    expect(rows).toEqual([{ name: "gene-expression", usage_count: 3 }])
  })

  test("a genuinely different term does NOT merge", async () => {
    const h = await db()
    Vocabulary.propose(h, "gene expression", "entity")
    const other = Vocabulary.propose(h, "gene regulation", "entity")

    expect(other.name).toBe("gene-regulation")
    expect(other.reused).toBeFalse()
  })

  test("new subtypes land as 'proposed', excluded from default scope", async () => {
    const h = await db()
    expect(Vocabulary.propose(h, "epitope", "entity").status).toBe("proposed")
  })

  test("the same name under two kinds are two independent rows", async () => {
    // 'dataset' is a core subtype of BOTH entity (a GEO accession) and artifact
    // (a materialized local file). With name as the sole primary key these
    // collide and one silently wins.
    const h = await db()
    const rows = h.db.query("SELECT kind, definition FROM vocabulary WHERE name = 'dataset' ORDER BY kind").all() as any[]

    expect(rows.map((r) => r.kind)).toEqual(["artifact", "entity"])
    expect(rows[0].definition).not.toBe(rows[1].definition)
  })

  test("usage of one kind does not increment another kind's count", async () => {
    const h = await db()
    Vocabulary.propose(h, "dataset", "entity")

    const counts = Object.fromEntries(
      (h.db.query("SELECT kind, usage_count FROM vocabulary WHERE name = 'dataset'").all() as any[]).map((r) => [
        r.kind,
        r.usage_count,
      ]),
    )
    expect(counts.entity).toBe(1)
    expect(counts.artifact).toBe(0)
  })
})

describe("auto-promotion", () => {
  function addNodes(h: DatabaseClient.Handle, kind: string, subtype: string, n: number) {
    for (let i = 0; i < n; i++) {
      h.db
        .query(
          `INSERT INTO node (id, kind, subtype, label, recorded_at, origin, review_state)
           VALUES (?, ?, ?, ?, 0, 'agent', 'unreviewed')`,
        )
        .run(`${subtype}-${i}`, kind, subtype, `n${i}`)
    }
  }

  test("promotes at the threshold and records that it was automatic", async () => {
    const h = await db()
    Vocabulary.propose(h, "epitope", "entity")

    addNodes(h, "entity", "epitope", Vocabulary.AUTO_PROMOTE_THRESHOLD - 1)
    expect(Vocabulary.checkAutoPromotion(h, "entity", "epitope")).toBeFalse()

    h.db
      .query(
        `INSERT INTO node (id, kind, subtype, label, recorded_at, origin, review_state)
         VALUES ('epitope-last', 'entity', 'epitope', 'n', 0, 'agent', 'unreviewed')`,
      )
      .run()

    expect(Vocabulary.checkAutoPromotion(h, "entity", "epitope")).toBeTrue()

    const row = h.db
      .query("SELECT status, promoted_by, promoted_at FROM vocabulary WHERE kind = 'entity' AND name = 'epitope'")
      .get() as any
    expect(row.status).toBe("accepted")
    // Auditable: a resolver promoted by sheer repetition stays traceable.
    expect(row.promoted_by).toBe("auto")
    expect(row.promoted_at).toBeGreaterThan(0)
  })

  test("rejected nodes do not count toward the threshold", async () => {
    const h = await db()
    Vocabulary.propose(h, "epitope", "entity")
    for (let i = 0; i < Vocabulary.AUTO_PROMOTE_THRESHOLD + 5; i++) {
      h.db
        .query(
          `INSERT INTO node (id, kind, subtype, label, recorded_at, origin, review_state)
           VALUES (?, 'entity', 'epitope', 'n', 0, 'agent', 'rejected')`,
        )
        .run(`r-${i}`)
    }
    expect(Vocabulary.checkAutoPromotion(h, "entity", "epitope")).toBeFalse()
  })

  test("a maintainer can promote or reject at any time, distinctly attributed", async () => {
    const h = await db()
    Vocabulary.propose(h, "epitope", "entity")
    Vocabulary.setStatus(h, "entity", "epitope", "accepted")

    const row = h.db
      .query("SELECT status, promoted_by FROM vocabulary WHERE kind = 'entity' AND name = 'epitope'")
      .get() as any
    expect(row.status).toBe("accepted")
    expect(row.promoted_by).toBe("maintainer")
  })
})

describe("merge", () => {
  test("is non-destructive and retargets nodes of that kind only", async () => {
    const h = await db()
    Vocabulary.propose(h, "gene-symbol", "entity")
    h.db
      .query(
        `INSERT INTO node (id, kind, subtype, label, recorded_at, origin, review_state)
         VALUES ('n1', 'entity', 'gene-symbol', 'TP53', 0, 'agent', 'unreviewed')`,
      )
      .run()

    Vocabulary.merge(h, "entity", "gene-symbol", "gene")

    const merged = h.db
      .query("SELECT status, merged_into FROM vocabulary WHERE kind = 'entity' AND name = 'gene-symbol'")
      .get() as any
    // Never DELETE — the audit trail survives its own revisions.
    expect(merged.status).toBe("merged")
    expect(merged.merged_into).toBe("gene")
    expect((h.db.query("SELECT subtype FROM node WHERE id = 'n1'").get() as any).subtype).toBe("gene")
  })

  test("proposing a merged subtype resolves to its target", async () => {
    const h = await db()
    Vocabulary.propose(h, "gene-symbol", "entity")
    Vocabulary.merge(h, "entity", "gene-symbol", "gene")

    const res = Vocabulary.propose(h, "gene symbol", "entity")
    expect(res.name).toBe("gene")
    expect(res.reused).toBeTrue()
  })
})

describe("proposed()", () => {
  test("lists proposed subtypes by usage so drift is visible in db status", async () => {
    const h = await db()
    Vocabulary.propose(h, "epitope", "entity")
    Vocabulary.propose(h, "hla-allele", "entity")
    Vocabulary.propose(h, "hla-alleles", "entity")

    expect(Vocabulary.proposed(h)).toEqual([
      { kind: "entity", name: "hla-allele", usage_count: 2 },
      { kind: "entity", name: "epitope", usage_count: 1 },
    ])
  })
})
