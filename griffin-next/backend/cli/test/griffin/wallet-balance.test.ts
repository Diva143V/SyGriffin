import { test, expect, describe } from "bun:test"
import { Griffin } from "../../src/griffin"

// Wallet balance bug: the panel showed Atlas's unified balance (CLI wallet +
// Atlas-web wallet + subscription + gifted, e.g. $160) but Griffin managed
// mode can only spend the CLI wallet. cliSpendableCents must report the CLI
// wallet, so the number reflects what the CLI can actually spend.

describe("cliSpendableCents", () => {
  test("prefers the CLI wallet over the unified pool", () => {
    // Unified $160 (mostly Atlas-web + gifted), CLI wallet $2.50 — show $2.50.
    expect(Griffin.cliSpendableCents({ cli_balance_cents: 250, unified_balance_cents: 16000 })).toBe(250)
  })

  test("shows an empty CLI wallet as 0, not the unified pool", () => {
    expect(Griffin.cliSpendableCents({ cli_balance_cents: 0, unified_balance_cents: 16000 })).toBe(0)
  })

  test("falls back to unified, then aggregate, when the CLI field is absent", () => {
    expect(Griffin.cliSpendableCents({ unified_balance_cents: 500 })).toBe(500)
    expect(Griffin.cliSpendableCents({ balance_cents: 300 })).toBe(300)
    expect(Griffin.cliSpendableCents({})).toBe(0)
  })
})
