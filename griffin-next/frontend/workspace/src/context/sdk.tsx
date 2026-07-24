import { createGriffinClient, type Event } from "@griffin/sdk/v2/client"
import { createSimpleContext } from "@griffin/ui/context"
import { createGlobalEmitter } from "@solid-primitives/event-bus"
import { createEffect, createMemo, onCleanup } from "solid-js"
import { useGlobalSDK } from "./global-sdk"
import { usePlatform } from "./platform"

export const { use: useSDK, provider: SDKProvider } = createSimpleContext({
  name: "SDK",
  init: (props: { directory: string }) => {
    const platform = usePlatform()
    const globalSDK = useGlobalSDK()

    const directory = createMemo(() => props.directory)
    const normalizedDirectory = createMemo(() => directory().replaceAll("\\", "/").toLowerCase())
    const client = createMemo(() =>
      createGriffinClient({
        baseUrl: globalSDK.url,
        fetch: platform.fetch,
        directory: directory(),
        throwOnError: true,
      }),
    )

    const emitter = createGlobalEmitter<{
      [key in Event["type"]]: Extract<Event, { type: key }>
    }>()

    createEffect(() => {
      console.log("[SDK] Subscribing to directory:", normalizedDirectory())
      const unsub = globalSDK.event.on(normalizedDirectory(), (event) => {
        console.log("[SDK] Received event for directory:", normalizedDirectory(), "event type:", event.type, "event:", event)
        emitter.emit(event.type, event)
      })
      onCleanup(unsub)
    })

    return {
      get directory() {
        return directory()
      },
      get client() {
        return client()
      },
      event: emitter,
      get url() {
        return globalSDK.url
      },
    }
  },
})
