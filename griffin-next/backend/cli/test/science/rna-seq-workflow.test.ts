import { describe, expect, test } from "bun:test"
import { parseDelimited, validateRnaSeqTables } from "../../src/science/runs/workflows/rna-seq"

const parameters = {
  organism: "Human",
  reference: "GRCh38",
  sampleColumn: "sample_id",
  conditionColumn: "condition",
  control: "control",
  treatment: "treated",
  adjustedPValue: 0.05,
}

describe("RNA-seq workflow validation", () => {
  test("parses quoted CSV cells", () => {
    const parsed = parseDelimited('sample_id,condition,note\nS1,control,"one, two"')
    expect(parsed.rows[0].note).toBe("one, two")
  })

  test("accepts matching samples and warns when batch is not selected", () => {
    const checks = validateRnaSeqTables({
      countText: "gene,S1,S2,S3,S4,S5,S6\nTP53,1,2,3,4,5,6",
      metadataText: "sample_id,condition\nS1,control\nS2,control\nS3,control\nS4,treated\nS5,treated\nS6,treated",
      parameters,
    })
    expect(checks.some((check) => check.id === "sample-ids" && check.status === "pass")).toBe(true)
    expect(checks.some((check) => check.id === "batch" && check.status === "warning")).toBe(true)
    expect(checks.some((check) => check.status === "fail")).toBe(false)
  })

  test("blocks mismatched samples and confounded batches", () => {
    const checks = validateRnaSeqTables({
      countText: "gene,S1,S2,S3,S4\nTP53,1,2,3,4",
      metadataText: "sample_id,condition,batch\nS1,control,A\nS2,control,A\nS3,treated,B\nS5,treated,B",
      parameters: { ...parameters, batchColumn: "batch" },
    })
    expect(checks.some((check) => check.id === "sample-ids" && check.status === "fail")).toBe(true)
    expect(checks.some((check) => check.id === "batch" && check.status === "fail")).toBe(true)
  })
})
