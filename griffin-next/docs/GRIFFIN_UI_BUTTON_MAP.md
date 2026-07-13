# Griffin UI Button Map

This file documents the current Griffin UI controls as implemented in `frontend/workspace/src`.
It is meant to answer: where is each button/control placed, what does the user see, and what does it do.

## Source Scope

- Home screen: `frontend/workspace/src/pages/home.tsx`
- Session workspace: `frontend/workspace/src/pages/session.tsx`
- Composer: `frontend/workspace/src/atlas/Composer.tsx`
- Right panel: `frontend/workspace/src/atlas/RightPane.tsx`
- Files and previews: `frontend/workspace/src/atlas/FileExplorer.tsx`, file tree components, `frontend/workspace/src/atlas/FilePreview.tsx`
- Folder picker: `frontend/workspace/src/atlas/FolderPicker.tsx`
- Skills surfaces: `frontend/workspace/src/atlas/SkillsPage.tsx`, `frontend/workspace/src/atlas/SkillsBrowser.tsx`
- Settings dialog: `frontend/workspace/src/components/dialog-settings.tsx`
- Settings panels: `frontend/workspace/src/components/settings/*.tsx`
- Global overlays: `frontend/workspace/src/atlas/CommandPalette.tsx`, `frontend/workspace/src/atlas/HelpOverlay.tsx`, `frontend/workspace/src/atlas/FdaBanner.tsx`, `frontend/workspace/src/atlas/DisconnectedPanel.tsx`

## 1. Home Screen

Location: top app header.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Griffin wordmark | Far left of header | `Wordmark.tsx`, used by `home.tsx` | Click target when caller supplies `onClick`; on home it is visual branding only. |
| Search projects input | Header center/right | `home.tsx` | Filters the recent project grid/list by project path. |
| New project button | Header right, plus icon and `new project` label | `home.tsx` | Opens the folder selection flow. On desktop/local it can use the native directory picker; otherwise it opens Griffin's in-app `FolderPicker`. |
| Toggle theme button | Header right, sun/moon icon | `home.tsx` | Switches Griffin between light and dark color schemes. |
| Settings button | Header right, settings icon | `home.tsx` | Opens the Griffin settings dialog. |
| Server button | Header far right, status dot plus server name | `home.tsx` | Opens the server selection dialog. Dot color shows healthy, unhealthy, or unknown server status. |

Location: home project body.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Grid view button | Projects toolbar, right side | `home.tsx` | Switches project display to card grid and saves preference in local storage. |
| List view button | Projects toolbar, right side | `home.tsx` | Switches project display to compact list and saves preference in local storage. |
| Project card/row | Main project list/grid | `home.tsx` | Opens that folder as a Griffin project and navigates to its session workspace. |
| Favorite project button | Hover action on project card/row, star icon | `home.tsx` | Toggles the project as favorite; favorites sort above other projects. |
| Remove from list button | Hover action on project card/row, trash icon | `home.tsx` | Hides the project from the home list without deleting files. |
| New project card | End of project grid, plus icon | `home.tsx` | Opens the folder selection flow. |
| Clear search button | Empty search result state | `home.tsx` | Clears the project search filter. |
| Open folder button | Empty search result state or first-run empty hero | `home.tsx` | Opens folder picker to add/open a project. |

## 2. Session Workspace Header

Location: top app header inside a project.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Projects back button | Far left, chevron plus `projects` | `session.tsx` | Navigates back to the home/project list. |
| Command palette button | Header right, search icon | `session.tsx` | Opens the command palette. |
| Help button | Header right, book icon | `session.tsx` | Opens the help overlay. |
| Settings button | Header right, settings icon | `session.tsx` | Opens Griffin settings. |
| Toggle theme button | Header right, sun/moon icon | `session.tsx` | Switches light/dark scheme. |

## 3. Session Sidebar

Location: left session sidebar.

| Control | Placement | Source | What it does |
|---|---|---|---|
| New session button | Top of sidebar | `session.tsx` | Creates a new backend session for the current project and navigates to it. Shows `creating...` while busy. |
| Search sessions input | Under New session | `session.tsx` | Filters loaded sessions by title. Escape clears and blurs. |
| Clear search button | Inside session search field | `session.tsx` | Clears the search query. |
| Session row | Session list | `session.tsx` | Opens that session. Enter or Space also selects it. |
| Session title double-click | Session row title | `session.tsx` | Starts inline rename. Enter saves, Escape cancels, blur saves. |
| Delete session button | Hover action on session row, trash icon | `session.tsx` | Deletes the session through `sync.session.delete`; if active, navigates to next session or new session. |

## 4. Center Tabs

Location: top of the main center pane.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Chat tab | Center tab strip | `session.tsx` | Shows the active chat/session conversation. |
| Files tab | Center tab strip | `session.tsx` | Shows the project file explorer. Mounts lazily on first visit. |
| Skills tab | Center tab strip | `session.tsx` | Shows the full Skills catalog. Mounts lazily on first visit. |
| File document tab | Center tab strip, appears after opening a file | `session.tsx` | Shows a specific file in the center pane. |
| Close file tab button | Right side of each file tab, x icon | `session.tsx` | Closes that document tab and returns focus to another center tab. |
| Back to parent session | Chat header, when viewing child/subagent session | `session.tsx` | Navigates from a child session back to its parent session. |
| Jump to latest button | Floating near bottom of chat when user scrolled up | `session.tsx` | Forces chat scroll back to the newest message. |
| Restore reverted messages button | Revert banner in chat | `session.tsx` | Calls unrevert/redo for a reverted session. |
| Editable chat title | Sticky chat header title | `session.tsx` | Double-click starts rename. Enter or blur commits the new title; Escape cancels. |

## 5. Composer

Location: bottom of the chat surface.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Text area | Main composer input | `Composer.tsx` | Accepts the user prompt. Enter sends, Shift+Enter inserts newline. `/` opens slash skill suggestions. |
| Slash suggestion row | Popover above composer when typing `/query` | `Composer.tsx` | Inserts `/<skill-name> ` into the prompt. Keyboard arrows move selection; Enter picks. |
| Model selector button | Composer toolbar, model name button | `Composer.tsx` | Opens model picker popover. |
| Model search input | Inside model picker | `Composer.tsx` | Filters selectable models by model, provider, or name. |
| Model row | Inside model picker | `Composer.tsx` | Selects the provider/model for future sends. |
| Show older/show fewer button | Bottom of provider group in model picker | `Composer.tsx` | Expands or collapses older model family variants. |
| Effort segmented buttons | Model picker footer, when model exposes variants | `Composer.tsx` | Saves reasoning effort variant for the selected model. |
| Context segmented buttons | Model picker footer, when model has long-context tier | `Composer.tsx` | Toggles standard or over-200k context pricing intent. |
| Manage models link | Model picker footer | `Composer.tsx` | Opens external model management URL. |
| Agent mode button | Composer toolbar, current agent label | `Composer.tsx` | Opens the Griffin agent menu. |
| Research agent option | Agent menu | `Composer.tsx` | Selects default research companion mode for literature plus analysis. |
| Biology specialist option | Agent menu | `Composer.tsx` | Selects biology specialist mode for bioinformatics and life-science data. |
| Plan option | Agent menu | `Composer.tsx` | Selects planning mode, intended to think first without edits. |
| Attach file button | Composer toolbar, paperclip icon | `Composer.tsx` | Opens file picker input. Selected files are saved into `.context/` and attached to prompt. |
| Attachment remove button | On each attachment chip | `Composer.tsx` | Removes that pending attachment before sending. |
| Browse skills button | Composer toolbar, sparkles icon | `Composer.tsx` | Opens inline skills browser popover. |
| Send button | Composer toolbar, appears when prompt or attachment exists | `Composer.tsx` | Sends the prompt immediately if idle. |
| Queue button | Same location as Send while agent is busy | `Composer.tsx` | Queues the prompt and sends it after the current agent turn finishes. |
| Stop button | Composer toolbar while streaming | `Composer.tsx` | Stops the current streaming agent response. |

## 6. Right Panel

Location: right side workspace panel.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Resize handle | Left edge of right panel | `RightPane.tsx` | Drag to resize panel width between configured min and max; stores width in local storage. |
| Terminal tab button | Right panel tab bar | `RightPane.tsx` | Shows the terminal tab. Currently this is the only visible right-panel tab. |
| Skill library button | Right panel header, braces icon | `RightPane.tsx` | Opens centered Skill Library dialog. Picking a skill prefills `/<name> ` into composer. |
| Panel settings button | Right panel header, settings icon | `RightPane.tsx` | Opens panel menu for showing/hiding right-panel tabs. |
| Panel tab visibility row | Panel settings menu | `RightPane.tsx` | Toggles a right-panel tab on/off. |
| Hide panel menu row | Panel settings menu | `RightPane.tsx` | Collapses the right panel. |
| Hide panel button | Right panel header, chevron right icon | `RightPane.tsx` | Collapses the right panel into the rail. |
| Show panel button | Collapsed rail, chevron left icon | `RightPane.tsx` | Reopens the right panel. |
| Collapsed terminal rail button | Collapsed rail | `RightPane.tsx` | Reopens the panel and selects the terminal tab. |

Location: terminal tab inside right panel.

| Control | Placement | Source | What it does |
|---|---|---|---|
| New terminal button | Terminal tab header | `RightPane.tsx` | Opens a new terminal session when Griffin is connected to a loopback server. |
| Start terminal button | Empty terminal tab body | `RightPane.tsx` | Creates the first terminal session. |
| Terminal session tab | Terminal tab strip | `RightPane.tsx` | Switches active terminal session. |
| Close terminal x | Inside terminal session tab | `RightPane.tsx` | Closes that terminal session. |

## 7. File Explorer And File Preview

Location: Files tab and file tree.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Refresh file tree button | File tree header | File tree component | Refetches the current directory listing. |
| File/folder tree row | File tree body | `FileExplorer.tsx` and file tree component | Folders expand/collapse or navigate; files open in a file preview/document tab. |

Location: file preview/document header.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Reset button | File header, only when text is dirty | `FilePreview.tsx` | Discards unsaved draft changes and restores last saved text. |
| Save button | File header, only when text is dirty | `FilePreview.tsx` | Saves text changes through `PUT /file/content`. |
| Render/source toggle | File header, braces/book icon | `FilePreview.tsx` | Markdown: toggles rendered view and raw source. Code: toggles read-only highlighted view and editable source. |
| Copy contents button | File header, copy icon | `FilePreview.tsx` | Copies text file contents, or data URL for binary where supported. |
| Download button | File header, download icon for binary files | `FilePreview.tsx` | Downloads binary file data. |
| Refresh button | File header, refresh icon | `FilePreview.tsx` | Refetches the file from disk. |
| Close button | File header, x icon | `FilePreview.tsx` | Closes the preview or document tab when `onClose` exists. |
| Retry button | File error state | `FilePreview.tsx` | Refetches file after a failed read. |
| Backdrop click | Slide-in file preview backdrop | `FilePreview.tsx` | Closes the slide-in preview. Escape also closes it. |

## 8. Folder Picker

Location: modal opened by New project/Open folder.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Favorite sidebar row | Left sidebar: Home, Desktop, Documents, Downloads, Applications | `FolderPicker.tsx` | Navigates the picker to that shortcut path. |
| Recent sidebar row | Left sidebar recent section | `FolderPicker.tsx` | Single click navigates to recent path; double-click opens it as project. |
| Parent folder button | Breadcrumb row, left chevron | `FolderPicker.tsx` | Moves one directory up. Disabled at filesystem root. |
| Home button | Breadcrumb row, home icon | `FolderPicker.tsx` | Navigates to user's home folder. |
| Breadcrumb segment button | Breadcrumb row | `FolderPicker.tsx` | Navigates directly to that ancestor folder. |
| Refresh button | Breadcrumb row, refresh icon | `FolderPicker.tsx` | Refetches current folder listing. |
| Filter folders input | Under breadcrumbs | `FolderPicker.tsx` | Filters folder rows by name. |
| Go input | Dashed `go to` row | `FolderPicker.tsx` | Accepts absolute path, `~`, or relative path. Enter attempts to navigate there. |
| Go button | Dashed `go to` row | `FolderPicker.tsx` | Validates typed path and navigates to it. |
| Folder row | Folder list | `FolderPicker.tsx` | Single click drills into that folder. Enter also drills in. |
| Folder row open button | Hover action on folder row | `FolderPicker.tsx` | Opens that folder as the selected project. |
| Folder row double-click | Folder list row | `FolderPicker.tsx` | Opens that folder as the selected project. |
| Retry button | Folder list error state | `FolderPicker.tsx` | Refetches current folder after listing error. |
| Cancel button | Picker footer | `FolderPicker.tsx` | Closes picker and returns `null`. |
| Open this folder button | Picker footer, primary | `FolderPicker.tsx` | Validates and opens the current folder as a Griffin project. |

## 9. Skills Surfaces

Location: center-pane Skills tab.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Category filter menu | Skills toolbar | `SkillsPage.tsx`, `_shared.tsx` | Filters skills by category. |
| Search skills input | Skills toolbar | `SkillsPage.tsx`, `_shared.tsx` | Filters skills by name or description. |
| Clear skill search button | Inside search field | `_shared.tsx` | Clears skills search text. |
| Add skill menu | Skills toolbar | `SkillsPage.tsx`, `_shared.tsx` | Opens menu with ways to add a skill. |
| Write from scratch menu item | Add skill menu | `SkillsPage.tsx` | Switches page to scratch skill editor. |
| Upload a skill menu item | Add skill menu | `SkillsPage.tsx` | Opens file input to upload a `SKILL.md`. |
| Import from GitHub menu item | Add skill menu | `SkillsPage.tsx` | Switches page to GitHub import form. |
| Skill enable switch | Top-right of each skill card | `SkillsPage.tsx` | Writes permission config so agents can or cannot load that skill. |
| Create skill button | Scratch form | `SkillsPage.tsx` | Creates a new skill with frontmatter and Markdown instructions. |
| Cancel scratch button | Scratch form | `SkillsPage.tsx` | Returns to the skills list. |
| Install button | GitHub import form | `SkillsPage.tsx` | Calls `/settings/skills/install` for a public GitHub repo URL. |
| Cancel GitHub import button | GitHub import form | `SkillsPage.tsx` | Returns to the skills list. |

Location: composer inline skills browser.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Search skills input | Popover header | `SkillsBrowser.tsx` | Filters skills by name, description, or tags. |
| Close button | Popover header, x | `SkillsBrowser.tsx` | Closes inline skills browser. Escape and outside click also close it. |
| Skill row | Popover list | `SkillsBrowser.tsx` | Picks a skill and passes its name to caller, usually inserting `/<name> `. |

Location: centered Skill Library dialog.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Search skills input | Dialog top | `SkillsBrowser.tsx` | Filters library skills. |
| Skill row | Dialog body | `SkillsBrowser.tsx` | Picks a skill, calls `onPick(name)`, and closes dialog. |

## 10. Settings Dialog Shell

Location: settings modal.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Settings sidebar panel row | Left sidebar | `dialog-settings.tsx` | Navigates to selected settings panel. |
| Back button | Settings top bar | `dialog-settings.tsx` | Moves backward through internal settings navigation history. |
| Forward button | Settings top bar | `dialog-settings.tsx` | Moves forward through internal settings navigation history. |
| Expand/collapse button | Settings top bar | `dialog-settings.tsx` | Toggles expanded settings dialog width/layout. |
| Close button | Settings top bar | `dialog-settings.tsx` | Closes settings dialog. |

## 11. General Settings

Location: Settings > General.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Manage billing button | Account section, Billing row | `General.tsx` | Opens configured billing/dashboard URL in browser. |
| Sign out button | Account section, Session row | `General.tsx` | Confirms and logs out this local Griffin server. |
| Default model select | Model section | `General.tsx` | Updates global config `model`. |
| Subagent model select | Model section | `General.tsx` | Updates global config `small_model`. |
| Reasoning effort select | Model section | `General.tsx` | Saves default reasoning effort in preferences. |
| Non-commercial card | Licensing section | `General.tsx` | Saves output-use intent as non-commercial. |
| Commercial card | Licensing section | `General.tsx` | Saves output-use intent as commercial. |
| Appearance controls | Appearance sections | `settings-general.tsx` | Controls theme, language, update, sound, and related app preferences. |

## 12. Memory Settings

Location: Settings > Memory.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Global scope button | Scope segmented control | `Memory.tsx` | Loads and edits global Supermemory-backed notes. |
| This project scope button | Scope segmented control | `Memory.tsx` | Loads and edits project-specific Supermemory-backed notes. |
| Clear all button | Memory enabled card | `Memory.tsx` | Confirms and removes all categories/notes for current scope. |
| Memory enabled switch | Memory enabled card | `Memory.tsx` | Enables or pauses memory recall while keeping notes saved. |
| Remove category button | Category header, trash icon | `Memory.tsx` | Removes the category and its notes. |
| Remove note button | Hover action on note row, x icon | `Memory.tsx` | Removes one pinned note. |
| Add note button | Category note composer | `Memory.tsx` | Adds text from note input to that category. Enter also adds. |
| Add category button | Bottom category composer | `Memory.tsx` | Creates a new memory category. Enter also adds. |

## 13. Credentials Settings

Location: Settings > Credentials.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Disconnect provider button | Provider row when connected | `Credentials.tsx` | Removes saved credential/session for that provider. |
| Connect/configure provider button | Provider row | `Credentials.tsx` | Opens inline form for provider key/OAuth setup. |
| Save provider key button | Inline provider form | `Credentials.tsx` | Saves provider credential. |
| Cancel provider form button | Inline provider form | `Credentials.tsx` | Closes inline edit form. |
| Add custom provider row | Custom provider area | `Credentials.tsx` | Opens custom provider form. |
| Save custom provider button | Custom provider form | `Credentials.tsx` | Saves custom provider config. |
| Cancel custom provider button | Custom provider form | `Credentials.tsx` | Closes custom provider form. |
| Remove OpenAI Codex key button | Codex account area | `Credentials.tsx` | Removes stored OpenAI Codex key/session. |
| Connect Codex button | Codex account area | `Credentials.tsx` | Starts Codex authentication flow. |
| Save API key button | API key form | `Credentials.tsx` | Saves key for chosen provider. |
| Remove API key button | Saved key row | `Credentials.tsx` | Deletes stored API key. |
| Config-file provider disabled button | Saved key/provider row | `Credentials.tsx` | Shows provider is defined in `griffin.json` and must be edited there. |

## 14. Compute Settings

Location: Settings > Compute.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Add SSH host button | SSH hosts section header | `Compute.tsx` | Opens/closes SSH host creation form. |
| Remove SSH host button | SSH host row | `Compute.tsx` | Removes saved host from compute settings. |
| Add endpoint button | Model endpoints section header | `Compute.tsx` | Opens/closes model endpoint creation form. |
| Remove endpoint button | Endpoint row | `Compute.tsx` | Removes saved endpoint. |
| Provider open button | GPU provider row | `Compute.tsx` | Opens provider dashboard or setup URL. |
| Provider connect button | GPU provider row | `Compute.tsx` | Starts connection/configuration for provider. |
| Provider remove button | GPU provider row | `Compute.tsx` | Removes saved provider connection. |
| Save form button | Host/endpoint form footer | `Compute.tsx` | Saves the host or endpoint. |
| Cancel form button | Host/endpoint form footer | `Compute.tsx` | Closes the active form. |
| Remove field button | Form field row, x/trash style | `Compute.tsx` | Removes an item from a dynamic form list. |

## 15. Local Models Settings

Location: Settings > Local Models.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Install runtime button | Runtime card | `LocalModels.tsx` | Opens external install page for the runtime. |
| Start runtime button | Runtime card | `LocalModels.tsx` | Starts the local model runtime from Griffin. |
| Add running runtime button | Runtime card | `LocalModels.tsx` | Adds an already-running runtime endpoint. |
| Pull model button | Ollama/model pull row | `LocalModels.tsx` | Pulls the named model. |
| Run Ollama serve button | Ollama helper row | `LocalModels.tsx` | Opens right-panel terminal and runs `ollama serve`. |
| Refresh button | Local model providers area | `LocalModels.tsx` | Refetches runtime/provider status. |
| Add runtime model button | Discovered model row | `LocalModels.tsx` | Adds discovered model/provider entry. |
| List custom endpoint button | Custom endpoint area | `LocalModels.tsx` | Lists models from a custom endpoint URL. |
| Add custom models button | Custom endpoint area | `LocalModels.tsx` | Adds selected models from custom endpoint. |
| Remove local provider button | Provider row | `LocalModels.tsx` | Removes saved local provider entry. |

## 16. Connectors Settings

Location: Settings > Connectors.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Search connectors input | Toolbar | `Connectors.tsx`, `_shared.tsx` | Filters connector list. |
| Add connector menu | Toolbar | `Connectors.tsx`, `_shared.tsx` | Opens menu/form to create a connector. |
| Authenticate button | Connector row | `Connectors.tsx` | Starts authentication for that connector. |
| Edit button | Connector row | `Connectors.tsx` | Opens connector edit form. |
| Remove button | Connector row | `Connectors.tsx` | Deletes connector config. |
| Refresh button | Connector empty/error area | `Connectors.tsx` | Refetches connector list/status. |
| Save connector button | Connector form | `Connectors.tsx` | Saves connector config. |
| Cancel connector button | Connector form | `Connectors.tsx` | Closes form without saving. |

## 17. Specialists Settings

Location: Settings > Specialists.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Search specialists input | Toolbar | `Specialists.tsx`, `_shared.tsx` | Filters specialists list. |
| Add specialist menu/button | Toolbar/form entry | `Specialists.tsx`, `_shared.tsx` | Opens specialist creation form. |
| Delete specialist button | Specialist row, trash icon | `Specialists.tsx` | Removes custom specialist. |
| Create specialist button | Specialist form | `Specialists.tsx` | Creates specialist with name, description, prompt, and mode. |
| Cancel specialist button | Specialist form | `Specialists.tsx` | Closes creation form. |

## 18. Network, Sandbox, Permissions, Storage

Location: Settings > Network.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Expand/collapse domain group | Network group header | `Network.tsx` | Expands or collapses that domain permission group. |
| Clear custom domains button | Custom domains area | `Network.tsx` | Clears all custom network allowlist entries. |
| Remove custom domain button | Custom domain row, x icon | `Network.tsx` | Removes one custom domain. |
| Add custom domain button | Custom domain input row | `Network.tsx` | Adds typed custom domain. |

Location: Settings > Sandbox.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Remove writable path button | Writable paths row | `Sandbox.tsx` | Removes one path from sandbox write access. |
| Add writable path button | Writable paths input row | `Sandbox.tsx` | Adds typed path to sandbox write access. |
| Run sandbox test button | Test area | `Sandbox.tsx` | Runs sandbox capability test. |

Location: Settings > Permissions.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Revoke all button | Permissions panel | `Permissions.tsx` | Revokes stored permissions/approvals. |

Location: Settings > Storage.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Reset data location button | Data location row | `Storage.tsx` | Resets Griffin data directory to default. |
| Relocate data button | Data location row | `Storage.tsx` | Opens directory picker and moves/sets data location. |
| Go to credentials button | Storage warning/helper row | `Storage.tsx` | Navigates settings dialog to Credentials panel. |

## 19. Server And Model Dialogs

Location: Select server dialog.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Server row | Server list | `dialog-select-server.tsx` | Selects/activates a configured Griffin server. |
| Server URL/input controls | Server dialog form | `dialog-select-server.tsx` | Edits or adds server connection values. |
| Save/connect button | Dialog footer | `dialog-select-server.tsx` | Saves the server selection/config and closes or reconnects. |

Location: Select model dialog.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Manage models icon button | Model select dialog header/list | `dialog-select-model.tsx` | Opens manage models dialog. |
| Manage models button | Select model dialog footer | `dialog-select-model.tsx` | Opens manage models dialog. |
| Model row | Select model dialog body | `dialog-select-model.tsx` | Selects model for the caller. |

## 20. Global Overlays And Banners

Location: command palette.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Overlay backdrop | Full-screen behind palette | `CommandPalette.tsx` | Closes command palette. |
| Command row | Palette result list | `CommandPalette.tsx` | Runs selected command and closes palette. |

Location: help overlay.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Overlay backdrop | Full-screen behind help modal | `HelpOverlay.tsx` | Closes help overlay. |
| Close button | Help modal header, x icon | `HelpOverlay.tsx` | Closes help overlay. |

Location: disconnected server banner.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Switch server button | Disconnected panel | `DisconnectedPanel.tsx` | Opens server selection dialog. |

Location: filesystem access banner/dialog.

| Control | Placement | Source | What it does |
|---|---|---|---|
| Grant filesystem access button | FDA banner | `FdaBanner.tsx` | Opens OS-specific Full Disk Access instructions. |
| Recheck button | FDA instructions dialog | `FdaBanner.tsx` | Rechecks whether filesystem access is now available. |
| Dismiss button | FDA instructions dialog | `FdaBanner.tsx` | Dismisses/hides the access prompt. |

## Notes For Future UI Work

- Buttons with icon-only labels rely on `title` or `aria-label`; keep those updated when icons change.
- Project/session rows use `role="button"` and keyboard handlers even when they are `div`s.
- Some controls are imported UI primitives (`Button`, `IconButton`, `Select`, `Switch`, `DropdownMenu`) rather than raw `<button>` elements.
- Griffin-specific primary user paths are: open project, create/select session, choose agent/model, send/queue/stop prompt, browse/install skills, open files, manage memory.
- The center workspace also includes a Runs tab for structured scientific workflows and persisted research-run records.

## Scientific Runs

Location: center workspace, Runs tab.

| Control | Placement | Source | What it does |
| --- | --- | --- | --- |
| Runs tab | Center tab strip | `session.tsx`, `RunsPage.tsx` | Opens the project-scoped scientific runs workspace. |
| Refresh runs button | Runs header, top-right | `RunsPage.tsx` | Reloads persisted runs from the Griffin server. |
| New run button | Runs header, top-right | `RunsPage.tsx` | Opens the structured RNA-seq workflow launcher. |
| Run row | Left run list | `RunsPage.tsx` | Selects a run and opens its validation, plan, progress, inputs, parameters, and logs. |
| Close launcher button | Workflow launcher, top-right | `RunsPage.tsx` | Returns to the run list without creating a record. |
| Validate inputs button | Workflow launcher footer | `RunsPage.tsx` | Checks files, SHA-256 hashes, sample IDs, groups, replicates, and batch design. |
| Create tracked run button | Workflow launcher footer | `RunsPage.tsx` | Persists the validated workflow record. Failed checks create a blocked run. |
| Approve plan button | Run detail footer | `RunsPage.tsx` | Records researcher approval and marks a valid run ready for an execution worker. |
| Cancel button | Run detail footer | `RunsPage.tsx` | Cancels an awaiting, ready, or running run. |
| Retry button | Run detail footer | `RunsPage.tsx` | Resets a failed or cancelled run for validation and approval. |
- The old graph/canvas controls are intentionally absent from the current Griffin UI.
