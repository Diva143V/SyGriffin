// Opens provider setup once for a new Griffin installation.
import { createEffect, createSignal } from "solid-js"
import { useDialog } from "@synsci/ui/context/dialog"
import { useServer } from "@/context/server"
import { useGlobalSync } from "@/context/global-sync"
import { useProviders } from "@/hooks/use-providers"
import { openSetupDialog, readSetupDismissed } from "@/atlas/SetupDialog"

export function SetupGate() {
  const dialog = useDialog()
  const server = useServer()
  const providers = useProviders()
  const globalSync = useGlobalSync()
  const [dismissed, setDismissed] = createSignal(readSetupDismissed())
  let decided = false

  const configured = () =>
    providers.connected().some((provider) => provider.id !== "synsci") || !!globalSync.data.config?.model

  createEffect(() => {
    if (decided || dismissed()) return
    if (server.healthy() !== true || !globalSync.data.ready) return
    decided = true
    if (!configured()) openSetupDialog(dialog, () => setDismissed(true))
  })

  return null
}
