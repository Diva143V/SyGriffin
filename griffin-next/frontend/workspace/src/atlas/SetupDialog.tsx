import { type JSX, For, Show, createSignal } from "solid-js"
import { Dialog } from "@griffin/ui/dialog"
import { useDialog } from "@griffin/ui/context/dialog"
import { Button } from "@griffin/ui/button"
import { TextField } from "@griffin/ui/text-field"
import { useGlobalSDK } from "@/context/global-sdk"
import { FONT_SANS } from "@/styles/tokens"

export const SETUP_DISMISS_KEY = "griffin.setup.dismissed"

export function readSetupDismissed(): boolean {
  try {
    return localStorage.getItem(SETUP_DISMISS_KEY) === "1"
  } catch {
    return false
  }
}

export function openSetupDialog(dialog: ReturnType<typeof useDialog>, onDismiss?: () => void) {
  dialog.show(() => <SetupDialog onDismiss={onDismiss} />)
}

const PROVIDERS = [
  { id: "anthropic", label: "Anthropic", placeholder: "sk-ant-..." },
  { id: "openai", label: "OpenAI", placeholder: "sk-..." },
  { id: "google", label: "Google", placeholder: "AIza..." },
  { id: "openrouter", label: "OpenRouter", placeholder: "sk-or-..." },
]

type View = "choose" | "key"

export function SetupDialog(props: { onDismiss?: () => void }): JSX.Element {
  const dialog = useDialog()
  const sdk = useGlobalSDK()
  const [view, setView] = createSignal<View>("choose")
  const [provider, setProvider] = createSignal(PROVIDERS[0].id)
  const [apiKey, setApiKey] = createSignal("")
  const [busy, setBusy] = createSignal(false)
  const [error, setError] = createSignal<string>()

  const dismiss = () => {
    try {
      localStorage.setItem(SETUP_DISMISS_KEY, "1")
    } catch {}
    props.onDismiss?.()
    dialog.close()
  }

  const save = async () => {
    const key = apiKey().trim()
    if (!key || busy()) return
    setBusy(true)
    setError(undefined)
    try {
      await sdk.client.auth.set({ providerID: provider(), auth: { type: "api", key } })
      await sdk.client.global.sync()
      dialog.close()
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause))
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog title="Set up a model provider">
      <div style={{ display: "flex", "flex-direction": "column", gap: "16px", "max-width": "460px" }}>
        <Show when={error()}>
          <div style={{ "font-family": FONT_SANS, "font-size": "12px", color: "var(--color-error)" }}>{error()}</div>
        </Show>

        <Show when={view() === "choose"}>
          <p style={intro()}>Connect a model provider to begin research. Credentials stay on this machine.</p>
          <ChoiceCard
            title="Connect your provider"
            body="Use an Anthropic, OpenAI, Google, or OpenRouter API key."
            onClick={() => setView("key")}
          />
          <ChoiceCard
            title="Not now"
            body="Open the workspace and connect a provider later in Settings."
            muted
            onClick={dismiss}
          />
        </Show>

        <Show when={view() === "key"}>
          <label style={{ display: "flex", "flex-direction": "column", gap: "6px" }}>
            <span style={{ "font-family": FONT_SANS, "font-size": "12px", color: "var(--color-text-muted)" }}>
              Provider
            </span>
            <select value={provider()} onChange={(event) => setProvider(event.currentTarget.value)} style={selectStyle()}>
              <For each={PROVIDERS}>{(item) => <option value={item.id}>{item.label}</option>}</For>
            </select>
          </label>
          <TextField
            type="password"
            hideLabel
            placeholder={PROVIDERS.find((item) => item.id === provider())?.placeholder ?? "API key"}
            value={apiKey()}
            disabled={busy()}
            onChange={setApiKey}
            onKeyDown={(event: KeyboardEvent) => {
              if (event.key === "Enter") void save()
            }}
          />
          <div style={{ display: "flex", gap: "8px", "justify-content": "space-between" }}>
            <Button variant="ghost" size="small" onClick={() => setView("choose")}>
              back
            </Button>
            <Button variant="primary" size="small" disabled={busy() || !apiKey().trim()} onClick={() => void save()}>
              {busy() ? "connecting..." : "connect"}
            </Button>
          </div>
        </Show>
      </div>
    </Dialog>
  )
}

function ChoiceCard(props: { title: string; body: string; muted?: boolean; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={props.onClick}
      style={{
        display: "flex",
        "flex-direction": "column",
        gap: "4px",
        padding: "12px",
        border: "1px solid var(--color-border)",
        "border-radius": "6px",
        background: "var(--color-bg-surface)",
        color: props.muted ? "var(--color-text-muted)" : "var(--color-text)",
        "text-align": "left",
        cursor: "pointer",
      }}
    >
      <strong style={{ "font-family": FONT_SANS, "font-size": "13px" }}>{props.title}</strong>
      <span style={{ "font-family": FONT_SANS, "font-size": "12px", "line-height": 1.5 }}>{props.body}</span>
    </button>
  )
}

const intro = (): JSX.CSSProperties => ({
  margin: 0,
  "font-family": FONT_SANS,
  "font-size": "13px",
  "line-height": 1.6,
  color: "var(--color-text-muted)",
})

const selectStyle = (): JSX.CSSProperties => ({
  height: "36px",
  padding: "0 10px",
  border: "1px solid var(--color-border)",
  "border-radius": "4px",
  background: "var(--color-bg-surface)",
  color: "var(--color-text)",
})
