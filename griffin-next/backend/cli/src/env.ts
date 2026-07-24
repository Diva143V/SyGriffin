export class Env {
  static get(key: string): string | undefined {
    return process.env[key]
  }

  static set(key: string, value: string): void {
    process.env[key] = value
  }

  static remove(key: string): void {
    delete process.env[key]
  }

  static all(): Record<string, string> {
    const result: Record<string, string> = {}
    for (const [k, v] of Object.entries(process.env)) {
      if (v !== undefined) {
        result[k] = v
      }
    }
    return result
  }
}
