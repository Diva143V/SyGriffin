export * from "./client.js"
export * from "./server.js"

import { createGriffinClient } from "./client.js"
import { createGriffinServer } from "./server.js"
import type { ServerOptions } from "./server.js"

export async function createGriffin(options?: ServerOptions) {
  const server = await createGriffinServer({
    ...options,
  })

  const client = createGriffinClient({
    baseUrl: server.url,
  })

  return {
    client,
    server,
  }
}
