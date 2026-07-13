;(function () {
  var themeId = localStorage.getItem("griffin-theme-id")
  if (!themeId) return

  var scheme = localStorage.getItem("griffin-color-scheme") || "system"
  var isDark = scheme === "dark" || (scheme === "system" && matchMedia("(prefers-color-scheme: dark)").matches)
  var mode = isDark ? "dark" : "light"

  document.documentElement.dataset.theme = themeId
  document.documentElement.dataset.colorScheme = mode

  if (themeId === "griffin-1") return

  var css = localStorage.getItem("griffin-theme-css-" + mode)
  if (css) {
    var style = document.createElement("style")
    style.id = "griffin-theme-preload"
    style.textContent =
      ":root{color-scheme:" +
      mode +
      ";--text-mix-blend-mode:" +
      (isDark ? "plus-lighter" : "multiply") +
      ";" +
      css +
      "}"
    document.head.appendChild(style)
  }
})()
