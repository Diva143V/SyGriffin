interface ImportMetaEnv {
  readonly VITE_GRIFFIN_SERVER_HOST: string
  readonly VITE_GRIFFIN_SERVER_PORT: string
  readonly VITE_GRIFFIN_SERVER?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

interface Window {
  __GRIFFIN_BASE_URL__?: string
}
