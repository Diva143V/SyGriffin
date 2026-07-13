import solidPlugin from "vite-plugin-solid"
import tailwindcss from "@tailwindcss/vite"
import { fileURLToPath } from "url"
import folderResolve from "./vite-folder-resolve.js"
import repoBridge from "./vite-repo.js"

/**
 * @type {import("vite").PluginOption}
 */
export default [
  {
    name: "griffin-desktop:config",
    config() {
      return {
        resolve: {
          alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
          },
        },
        worker: {
          format: "es",
        },
      }
    },
  },
  tailwindcss(),
  solidPlugin(),
  folderResolve,
  repoBridge,
]
