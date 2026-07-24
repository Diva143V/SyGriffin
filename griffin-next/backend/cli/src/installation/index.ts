import { BusEvent } from "@/bus/bus-event"
import path from "path"
import { $ } from "bun"
import z from "zod"
import { NamedError } from "@griffin/util/error"
import { Log } from "../util/log"
import { iife } from "@/util/iife"
import { Flag } from "../flag/flag"

declare global {
  const GRIFFIN_VERSION: string
  const GRIFFIN_CHANNEL: string
}

export namespace Installation {
  const log = Log.create({ service: "installation" })

  export type Method = Awaited<ReturnType<typeof method>>

  export const Event = {
    Updated: BusEvent.define(
      "installation.updated",
      z.object({
        version: z.string(),
      }),
    ),
    UpdateAvailable: BusEvent.define(
      "installation.update-available",
      z.object({
        version: z.string(),
      }),
    ),
  }

  export const Info = z
    .object({
      version: z.string(),
      latest: z.string(),
    })
    .meta({
      ref: "InstallationInfo",
    })
  export type Info = z.infer<typeof Info>

  export async function info() {
    return {
      version: VERSION,
      latest: await latest(),
    }
  }

  export function isPreview() {
    return CHANNEL !== "latest"
  }

  export function isLocal() {
    return CHANNEL === "local"
  }

  export async function method() {
    if (process.execPath.includes(path.join(".griffin", "bin"))) return "curl"
    // legacy pre-rename curl installs lived under ~/.synsc/bin
    if (process.execPath.includes(path.join(".synsc", "bin"))) return "curl"
    // ~/.local/bin is ALSO npm's target with `--prefix ~/.local`, pipx, and many
    // package managers — so it's ambiguous. Defer it: let the package-manager
    // probes below claim the install first, and only fall back to "curl" for
    // .local/bin when none of them do (see after the loop). Otherwise a
    // `npm i -g` into ~/.local was upgraded with the curl script.
    const inLocalBin = process.execPath.includes(path.join(".local", "bin"))
    const exec = process.execPath.toLowerCase()

    const checks = [
      {
        name: "npm" as const,
        command: () => $`npm list -g --depth=0`.throws(false).quiet().text(),
      },
      {
        name: "yarn" as const,
        command: () => $`yarn global list`.throws(false).quiet().text(),
      },
      {
        name: "pnpm" as const,
        command: () => $`pnpm list -g --depth=0`.throws(false).quiet().text(),
      },
      {
        name: "bun" as const,
        command: () => $`bun pm ls -g`.throws(false).quiet().text(),
      },
      {
        name: "brew" as const,
        command: () => $`brew list --formula griffin`.throws(false).quiet().text(),
      },
      {
        name: "scoop" as const,
        command: () => $`scoop list griffin`.throws(false).quiet().text(),
      },
      {
        name: "choco" as const,
        command: () => $`choco list --limit-output griffin`.throws(false).quiet().text(),
      },
    ]

    checks.sort((a, b) => {
      const aMatches = exec.includes(a.name)
      const bMatches = exec.includes(b.name)
      if (aMatches && !bMatches) return -1
      if (!aMatches && bMatches) return 1
      return 0
    })

    for (const check of checks) {
      const output = await check.command()
      const installedName =
        check.name === "brew" || check.name === "choco" || check.name === "scoop"
          ? "griffin"
          : "@griffin/griffin"
      if (output.includes(installedName)) {
        return check.name
      }
    }

    // No package manager claimed it — now honor the ambiguous ~/.local/bin as a
    // curl install (the curl installer's default target).
    if (inLocalBin) return "curl"

    return "unknown"
  }

  export const UpgradeFailedError = NamedError.create(
    "UpgradeFailedError",
    z.object({
      stderr: z.string(),
    }),
  )

  async function getBrewFormula() {
    const tapFormula = await $`brew list --formula griffin/tap/griffin`.throws(false).quiet().text()
    if (tapFormula.includes("griffin")) return "griffin/tap/griffin"
    const coreFormula = await $`brew list --formula griffin`.throws(false).quiet().text()
    if (coreFormula.includes("griffin")) return "griffin"
    return "griffin"
  }

  export async function upgrade(method: Method, target: string) {
    let cmd
    switch (method) {
      case "curl":
        // griffin.sh/install serves the repo install script. The app
        // subdomain serves the dashboard SPA, so piping it into bash fails.
        // Override via GRIFFIN_INSTALL_URL if hosting the script elsewhere.
        cmd = $`curl -fsSL ${process.env.GRIFFIN_INSTALL_URL || "https://griffin.sh/install"} | bash`.env({
          ...process.env,
          VERSION: target,
        })
        break
      case "npm":
        cmd = $`npm install -g @griffin/griffin@${target}`
        break
      case "pnpm":
        cmd = $`pnpm install -g @griffin/griffin@${target}`
        break
      case "bun":
        cmd = $`bun install -g @griffin/griffin@${target}`
        break
      case "brew": {
        const formula = await getBrewFormula()
        cmd = $`brew upgrade ${formula}`.env({
          HOMEBREW_NO_AUTO_UPDATE: "1",
          ...process.env,
        })
        break
      }
      case "choco":
        cmd = $`echo Y | choco upgrade griffin --version=${target}`
        break
      case "scoop":
        cmd = $`scoop install griffin@${target}`
        break
      default:
        throw new Error(`Unknown method: ${method}`)
    }
    const result = await cmd.quiet().throws(false)
    if (result.exitCode !== 0) {
      const stderr = method === "choco" ? "not running from an elevated command shell" : result.stderr.toString("utf8")
      throw new UpgradeFailedError({
        stderr: stderr,
      })
    }
    log.info("upgraded", {
      method,
      target,
      stdout: result.stdout.toString(),
      stderr: result.stderr.toString(),
    })
    await $`${process.execPath} --version`.nothrow().quiet().text()
  }

  export const VERSION = typeof GRIFFIN_VERSION === "string" ? GRIFFIN_VERSION : "local"
  export const CHANNEL = typeof GRIFFIN_CHANNEL === "string" ? GRIFFIN_CHANNEL : "local"
  export const USER_AGENT = `griffin/${CHANNEL}/${VERSION}/${Flag.GRIFFIN_CLIENT}`

  /** OData query for the latest published version of a Chocolatey package.
   *  The id must match what the CLI actually publishes to Chocolatey
   *  (`griffin`) — everywhere else in this file already uses it (`choco
   *  list --limit-output griffin`, `choco upgrade griffin`). A leftover
   *  pre-rename `synsc` id here queried a non-existent package, so choco users
   *  could never resolve an upgrade target (`data.d.results[0]` was undefined). */
  export function chocoLatestVersionUrl(pkg: string = "griffin"): string {
    const filter = encodeURIComponent(`Id eq '${pkg}' and IsLatestVersion`)
    return `https://community.chocolatey.org/api/v2/Packages?$filter=${filter}&$select=Version`
  }

  export async function latest(installMethod?: Method) {
    const detectedMethod = installMethod || (await method())

    if (detectedMethod === "brew") {
      const formula = await getBrewFormula()
      if (formula === "griffin") {
        return fetch("https://formulae.brew.sh/api/formula/griffin.json")
          .then((res) => {
            if (!res.ok) throw new Error(res.statusText)
            return res.json()
          })
          .then((data: any) => data.versions.stable)
      }
    }

    if (
      detectedMethod === "npm" ||
      detectedMethod === "bun" ||
      detectedMethod === "pnpm" ||
      detectedMethod === "unknown"
    ) {
      const registry = await iife(async () => {
        const r = (await $`npm config get registry`.quiet().nothrow().text()).trim()
        const reg = r || "https://registry.npmjs.org"
        return reg.endsWith("/") ? reg.slice(0, -1) : reg
      })
      const knownTags = new Set(["latest", "ci", "dev", "beta"])
      const channel = knownTags.has(CHANNEL) ? CHANNEL : "latest"
      return fetch(`${registry}/@griffin/griffin/${channel}`)
        .then((res) => {
          if (!res.ok) throw new Error(res.statusText)
          return res.json()
        })
        .then((data: any) => data.version)
    }

    if (detectedMethod === "choco") {
      return fetch(chocoLatestVersionUrl(), { headers: { Accept: "application/json;odata=verbose" } })
        .then((res) => {
          if (!res.ok) throw new Error(res.statusText)
          return res.json()
        })
        .then((data: any) => data.d.results[0].Version)
    }

    if (detectedMethod === "scoop") {
      return fetch("https://raw.githubusercontent.com/ScoopInstaller/Main/master/bucket/griffin.json", {
        headers: { Accept: "application/json" },
      })
        .then((res) => {
          if (!res.ok) throw new Error(res.statusText)
          return res.json()
        })
        .then((data: any) => data.version)
    }

    return fetch("https://api.github.com/repos/synthetic-sciences/Griffin/releases/latest")
      .then((res) => {
        if (!res.ok) throw new Error(res.statusText)
        return res.json()
      })
      .then((data: any) => data.tag_name.replace(/^v/, ""))
  }
}
