---
name: aur-pkg-analysis
description: "Analyze AUR packages one by one from a list (passed as parameters, read from a file, or fetched via pacman -Qm). For each package: check reverse dependencies, find flatpak/pip/official repo alternatives, provide sudo pacman removal command. Use when cleaning up AUR packages from your system."
recommended: true
deps-skills: []
disable-model-invocation: false
user-invocable: true
allowed-tools: ["bash", "glob", "view", "mcp_searxng_searxng_web_search", "agentic_fetch"]
---

```json
{
  "todos": [
    {"content": "Determine package list source (params, file, or pacman -Qm)", "status": "in_progress", "active_form": "Determining package list source"},
    {"content": "Parse and validate package list", "status": "pending", "active_form": "Parsing package list"},
    {"content": "Analyze each package one by one", "status": "pending", "active_form": "Analyzing packages one by one"},
    {"content": "Generate removal and alternative commands", "status": "pending", "active_form": "Generating commands"},
    {"content": "Complete aur-pkg-analysis operation", "status": "pending", "active_form": "Completing aur-pkg-analysis operation"}
  ]
}
```

# AUR Package Analysis

Analyze AUR packages one by one from a text file. For each package, provide analysis, alternatives, and removal commands.

## BEGIN EXECUTION IMMEDIATELY

Do not ask the user what they want to do. Start with step 1:

### Step 1 — Determine the package list source (in priority order)

1. **Package list passed as parameters**: If the user provided package names directly as parameters, use those directly.
2. **Package list file**: If the user provided a file path as a parameter, read the file and treat each non-empty, non-comment line as a package name.
3. **Auto-detect in project**: Search the project for an existing `aur-packages.md` file (use `glob` to find it). If found, read it and proceed as the package list source.
4. **Auto-generate**: If no file exists, try generating it yourself: `pacman -Qm > ./aur-packages.md`. If successful, read the file and proceed.
5. **Fallback (cannot generate)**: If you cannot run `pacman` (no shell access / permission denied), provide the command to the user for manual execution (raw text, no code block, no preamble — last line of response):

pacman -Qm > ./aur-packages.md

After the user runs it and confirms, read `./aur-packages.md` and proceed.

**Parsing rules** (applies to all input sources):
- Skip empty lines and lines starting with `#` (comments)
- Each valid line is treated as one package name
- For default (`pacman -Qm` → `./aur-packages.md`) output, parse each line as `<pkg> <version>` or just `<pkg>` (extract package name, skip blank lines)
- If multiple versioned packages from the same project appear (e.g., boost1.86, boost174, gcc13), batch them together in a single analysis

### Step 2 — Present and analyze packages

Present packages ONE at a time, then wait for user to proceed.

**Batching rule (evaluated at first occurrence)**:
Before analyzing the current package, scan the remaining (uncommented) package list for related packages that should be batched together. Batching criteria:
- **Versioned variants**: Same project with version suffixes (e.g., `boost1.86`, `boost174`, `gcc13`)
- **Library + libs pairs**: Base package + `-libs`/`-static`/`-dev` variants (e.g., `boost1.86` + `boost1.86-libs`)
- **Debug packages**: Base package + `-debug` variant (e.g., `obs-move-transition` + `obs-move-transition-debug`)
- **Overlapping functionality**: Packages that provide the same service from different sources (e.g., `aria2-systemd` + `aria2c-daemon`)
- **Ecosystem packages**: Same upstream project split into multiple AUR packages (e.g., `openvino` + `openvino-intel-gpu-plugin` + `python-openvino`)

When batching:
1. **Batch at the FIRST occurrence** — when you reach the first package of a group, include ALL related packages in that single analysis
2. **Mark the entire batch as done** (`#`) in the file immediately after presenting the analysis
3. **Skip batched packages** when the pointer reaches them later — they're already commented out
4. Do NOT analyze a package in isolation when a related sibling appeared earlier and was already handled — that means the batch was done correctly
5. Do NOT retroactively mention batching on the second/later element — the batch analysis must happen on the first element's turn

## Analysis Workflow

For each package, search the following in parallel:

1. AUR package info: Search `site:aur.archlinux.org <pkg-name>` for PKGBUILD, dependencies, and reverse dependencies
2. For each reverse dependency found, look up what that package is (search its AUR page or Arch package page), plus its upstream repo URL, last release date, and last commit date
3. Upstream source repo: Check the PKGBUILD `url=` or `source=` field for the upstream repository
4. Upstream repo activity: Check the upstream repo for last release date and last commit/merge date on master/main
5. Official Arch repos: Search `site:archlinux.org/packages <pkg-name>` to check if it exists in official repos
6. Flatpak alternative: Search `flathub.org` or `freedesktop.org` for a flatpak equivalent
7. pip alternative: Search for Python/pip equivalent if applicable
8. Upstream activity: Visit the repo's releases and commits pages to find last release and last commit dates
9. Official install methods: Check the project's README/homepage for officially supported install methods (flatpak, appimage, deb, snap, aur, etc.). For Java applications, specifically check for a standalone JAR file download (`java -jar App.jar` or `wget http://url/App.jar`) — this is a valid self-contained install method, no packaging needed. For Go projects, check if `go install <module>@latest` is a viable install method — if the upstream repo is a Go module with a public import path, list `go install` as an official alternative and show the `go install <module>@latest` command in the Commands section. For Rust/Cargo projects, ALWAYS check `https://crates.io/crates/<pkg-name>` — if the crate exists, list `cargo install <crate-name>` as an official alternative in the Commands section. If the exact AUR name doesn't match, try common variants (remove `-git`, `-bin` suffixes; check the PKGBUILD `source=` for the crate name).
10. Community-maintained distribution channels: Check for community-supported packages on established distribution channels (Flathub, Snapcraft). These are NOT officially supported by upstream but are real install alternatives — treat them as valid alternatives, distinct from AUR. **IMPORTANT: Verify Flathub official status** — when a flatpak is found, check `https://flathub.org/api/v2/appstream/<flatpak-id>?architecture=x86_64&branch=stable` for `flathub::verification::verified: true` in metadata. If verified=true, it's officially endorsed by upstream (NOT community). Also check for the disclaimer text "This wrapper is not verified by, affiliated with, or supported by" on the Flathub web page — its absence + verified=true = official. Its presence = community-maintained. Search `flathub.org/apps/search?q=<pkg>` and `snapcraft.io/<pkg>`. Note last update date and whether it's active or potentially abandoned.
11. Neovim/vim plugin manager alt: If the package is a neovim or vim plugin (check AUR description, PKGBUILD, or name pattern like `nvim-*`, `vim-*`, `*nvim*`, `*vim*`), check if it can be installed via neovim/vim plugin managers — lazy.nvim, Mason, packer.nvim, vim-plug, vim-packer, minpac, pckr.nvim, etc. Search for the plugin on the upstream repo README for supported install methods via these managers. If so, list the plugin manager(s) as alternatives — the AUR package is unnecessary.
12. Pre-built plugin binaries (MANDATORY for plugin packages): For ANY package that is a plugin for a host application (OBS Studio, Audacity, DaVinci Resolve, Reaper, Blender, Kdenlive, GIMP, Inkscape, etc.), ALWAYS check the upstream GitHub/GitLab releases page for pre-built binaries (`.so`, `.dll`, `.dylib`, `.dvcp.bundle`, `.zip`). If pre-built binaries exist, show the download link and install instructions (extract to host app's plugin folder, e.g., `~/.config/obs-studio/plugins/`). This is a MANDATORY alternative to AUR — the AUR package is unnecessary when pre-built binaries are available. Common host app plugin paths: OBS (`~/.config/obs-studio/plugins/`), Audacity (`~/.audacity-data/Plugins/`), DaVinci Resolve (`~/.local/share/DaVinciResolve/Support/IOPlugins/`), Reaper (`~/.vst/` or `~/.config/REAPER/Reaper-Packages/user/`), Blender (`~/.config/blender/<version>/scripts/addons/`), Kdenlive (`~/.local/share/kdenlive/plugins/` or `/usr/lib/kde/plugins/kdenlive/`).
13. Unofficial install methods: Other non-official methods. AUR is unofficial unless the project itself maintains the AUR package.
14. Re-implementations/alternatives: Search for modern re-implementations or alternatives (e.g., "apg-go" for "apg") — check if the project has active forks, rewrites in other languages, or maintained alternatives
15. Maintainer profile: Get maintainer reputation via AUR web search. (a) Package count: fetch `https://aur.archlinux.org/packages/?SeB=m&K=<maintainer-name>&PP=1` — parse "X packages found" from the HTML/text response for their total package count. (b) TU status: fetch `https://wiki.archlinux.org/title/Trusted_Users` or check the maintainer's AUR packages page for TU indicators. (c) Account age: query `https://aur.archlinux.org/rpc/?v=5&type=info&arg=<pkg-name>` — the `FirstSubmitted` field (Unix epoch) shows how long they've maintained that package. Include all found info in the output.
16. Maintainer repo / semi-official sources: Check if the AUR maintainer has their own package repository (e.g., personal Arch user repo on GitHub/GitLab/website with pre-built packages, or mirrors of their AUR packages like Chrysocome's repo). Search `<maintainer-name> archlinux packages repository` or check their AUR profile for links to external repos. This provides semi-official pre-built alternatives to building from AUR.

## Output Format Per Package

Present each package as raw Markdown (do NOT wrap in an outer code fence — inner ```bash``` blocks will break otherwise):

| <package> | <description> |
|---|---|
| What it is | <description> |
| Who uses it | <reverse dep names with brief descriptions, e.g. "kjots (KDE notes app)" or "standalone"> |
| Flatpak alt | <✓/✗ — official only; community-maintained flatpaks go under "Community Channels"> |
| pip alt | <✓/✗> |
| Official repo | <✓/✗ - if in [core], [extra], [community]> |

If the package is a neovim/vim plugin, add a plugin manager row:
| Plugin mgr alt | <✓/✗ — lazy.nvim, Mason, vim-plug, packer, etc.>

If the package is a plugin for a host application (OBS, Audacity, DaVinci Resolve, Reaper, Blender, etc.), add a pre-built plugin row:
| Pre-built plugin | <✓/✗ — link to upstream releases page with pre-built binaries; show target plugin folder path>

**Upstream**
- **Repo**: `<url>` or `N/A`
- **Last release**: `<date>` or `N/A`
- **Last commit (master/main)**: `<date>` or `N/A`
- **Install methods**: `<official methods from repo README/site only (not AUR unless the project itself lists it), e.g. "flatpak, appimage, deb, snap" or "none">`

**Reverse Dependencies**
- `dep-name` (<brief description>)
  - Repo: `<url>` or `N/A`
  - Last release: `<date>` or `N/A`
  - Last commit: `<date>` or `N/A`
  - Install methods: `<official methods from repo README/site, e.g. "aur, flatpak, appimage" or "none">`

**Unofficial Install Methods**
- <list methods not in official repo, e.g. "AUR" (only if not already listed as official)>
- Flatpak (community): `<flatpak-id>` on Flathub (last updated <date>, note if abandoned)
- Snap (community): `<snap-name>` on Snapcraft (last updated <date>, note if abandoned)

**Maintainer Reputation**
- **Name**: <maintainer-name> (AUR profile: `https://aur.archlinux.org/account/<maintainer-name>`)
- **Packages maintained**: `<count>`
- **Status**: `<TU (Trusted User) / regular user>`
- **Long-standing**: `<✓/✗ — account age / first submission date>`

**Maintainer Repo** (only if found)
- `<maintainer-name>`: `<repo-url>` (pre-built packages / PKGBUILDs mirror)

**Notes** (only if applicable)
- <relevant notes: e.g., "AUR package removed; use official `ambix` instead", "superseded by X", "requires manual config", "modern alternative: `apg-go` (https://github.com/...)", etc.>

**Alternatives** (only if applicable, before Commands)
- **<alt-name>**: <brief description>
  ```bash
  sudo pacman -S <pkg>
  ```
  Or:
  ```bash
  flatpak install <flatpak-id>
  ```
  Or (if no package manager): `go install <module>@latest` / `pip install <pkg>` / `cargo install <crate>` / "build from source at <upstream-repo-url>" / "download from <url>"
- **<alt-name>**: <brief description>
  ```bash
  <install-command>
  ```
  (If no install command exists, specify how to obtain it with a link: "build from source at <url>", "tarball at <url>", "Windows/macOS only — <url>", etc. Always include the source repo URL.)

**Commands**
```bash
sudo pacman -Rns <pkg-name>
```

If replaced by official package or newer version exists:
```bash
sudo pacman -Rns <old-pkg-name>
sudo pacman -S <newer-official-pkg-name>
```

If the AUR package has a newer version in official repos (e.g., KF5 → KF6 transition: `libkdcraw5` → `libkdcraw`), always show both the removal and the replacement install command.

If flatpak alternative exists (upstream-verified via Flathub API `verified: true`, OR no disclaimer on Flathub page):
```bash
flatpak install flathub <flatpak-id>
```

For community-maintained flatpaks (NOT upstream-verified, or disclaimer exists), do NOT show them under Commands. List them under "Unofficial Install Methods" instead: `- Flatpak (community): <flatpak-id> on Flathub (last updated <date>)`.

**Flatpak verification**:
- **MANDATORY**: Check `https://flathub.org/api/v2/appstream/<flatpak-id>?architecture=x86_64&branch=stable` for metadata
- **Official**: `flathub::verification::verified: true` → show "Flatpak alt: yes" + `flatpak install` command under Commands
- **Community**: `verified: false` / missing / or Flathub disclaimer "This wrapper is not verified by..." → show under "Unofficial Install Methods" only
- **Decision table**: verified=true → official. verified=false → community. No API data → fetch Flathub web page for disclaimer text.

If pip alternative exists:
```bash
pip install <pip-package-name>
```

If the project is a Go module and `go install` is available:
```bash
go install <module-path>@latest
```

If the project is a Rust crate on crates.io and `cargo install` is available:
```bash
cargo install <crate-name>
```

If the package is a neovim/vim plugin and a plugin manager alternative exists, add a **Plugin Manager Install** section here:

**Plugin Manager Install**
- <list supported managers, e.g. "lazy.nvim, Mason, vim-plug">
- <example config snippet from upstream README, e.g. `{'mfussenegger/nvim-jdtls'}>`

If AppImage is available (official install method or in release assets), show a **Download** section after Commands:

**Download**
- <download-url>
```bash
chmod +x <appimage-file>
./<appimage-file>
```

After each package's analysis, add a "next" prompt at the end of the response:
> Say "next" for **<next-pkg-name>**.

This gives the user a clear, one-word command to proceed to the next package.

## Tracking Progress

If the input source is a **file**, immediately after presenting each package's analysis (in the same response), mark it as done in the input file by prefixing with `#`:
- Done: `# accounts-qml-module`
- Pending: `accounts-qml-module`

This happens BEFORE waiting for the user to proceed. Do not wait for "next" to mark a package done.

When reading the package list, skip any line starting with `#`. This allows resuming analysis across sessions without re-processing done packages.

If the input source is **parameters** or **default** (no file), store the package list in `./aur-packages.md` (one package per line) and mark each as done after analysis by prefixing with `#`. This allows resuming across sessions.

## Rules

- ONLY use `sudo pacman` for Arch package management commands (removal, installation, replacement). Never use paru, yay, pamac, or any other AUR helper/package manager for pacman operations — even for AUR-only replacements. If a replacement package is AUR-only, show `sudo pacman -Rns <old-pkg>` and note the replacement "requires an AUR helper (e.g., paru, yay)" without providing the install command.
- **NEVER show non-Arch package manager commands** in the Commands section or as alternatives — no `apt`, `apt-get`, `dpkg`, `aptitude`, `yum`, `dnf`, `zypper`, `emerge`, `pacstall`, or any distro-specific installer. If an upstream offers a `.deb`/`.rpm`/APT repo, mention it in the "Install methods" list text only (e.g., "deb, rpm, APT repo") but never provide the install command. The user is on Arch Linux.
- Present packages ONE at a time, then ask for next.
- If an **official** flatpak alternative exists (upstream-verified, no disclaimer), always show the flatpak install command. Community-maintained flatpaks go under "Unofficial Install Methods" only — never show `flatpak install` commands for them.
- If a pip alternative exists, always show the pip install command.
- If a package is a neovim/vim plugin, check for plugin manager alternatives (lazy.nvim, Mason, vim-plug, packer, etc.). If it can be installed via a plugin manager, the AUR package is unnecessary — list the plugin manager install method and note the AUR package can be safely removed.
- If information cannot be found via web search, fall back to checking the PKGBUILD directly.
- Always include a "Notes" section before "Commands". Use it for migration notes (AUR superseded by official package), configuration warnings, or deprecation notices.
- Include an "Alternatives" section before "Commands" when alternatives exist. List each alternative with its install command in a code block. If no install command exists (e.g., source-only, tarball download), specify how to obtain it with a link to the source repo: "build from source at <upstream-repo-url>", "tarball at <url>", etc. Always include the source repo URL.
- When a package is replaced by an official alternative, include both the removal command and the official install command in the "Commands" section.
- When a newer replacement package exists (e.g., KF5 transitional `libkcddb5` superseded by official `libkcddb`, or `-git` superseded by stable release in [extra]), always show `sudo pacman -S <newer-pkg>` alongside the removal command.
- When a package is merged/absorbed into another package, list which AUR packages were absorbed by the new package in the Notes section (e.g., "ambix now includes: ambix-standalone, ambix-vst").
- When a modern re-implementation or alternative exists (e.g., `apg-go` for `apg`), mention it in the Notes section with a link.
- Install methods in the "Upstream" section come from the project's official README/site. If the project lists AUR as official (or maintains the AUR package themselves, e.g., Brave), include AUR in the official "Install methods" list and do NOT list it under "Unofficial Install Methods". If AUR is community-maintained, list it under "Unofficial Install Methods" instead.
- When finding the upstream repo, use the `url=` field from the PKGBUILD as the canonical source. If the project links to a non-GitHub repo (e.g., GitLab, SourceHut, invent.kde.org, Gitea), list that as the primary repo. GitHub is only the primary repo if the project's official URL points there directly — if a GitHub URL exists but the official site links elsewhere, treat GitHub as a mirror and list the actual upstream repo instead.
- Keep output concise — omit empty sections. Only include sections with actual findings. Skip steps that return no results rather than printing "(none)".
- Versioned packages (e.g., boost1.86, boost174, gcc13, python311, llvm19) are legacy builds kept for ABI compatibility. When multiple versioned packages from the same project appear in the list, batch them together in a single analysis with a shared upstream section and per-package reverse deps.
- When a maintainer has their own package repository with pre-built packages, include it in the "Maintainer Repo" section. This is a semi-official alternative to building from AUR.
- For Go projects, always check if `go install <module-path>@latest` is viable. If so, list it in the Commands section and note the AUR package is unnecessary.
- For Rust/Cargo projects, ALWAYS check crates.io (try the package name, minus `-git`/`-bin` suffixes). If a crate exists, show `cargo install <crate-name>` in the Commands section and note the AUR package is unnecessary. If crates.io fetch fails, check the upstream README for cargo install instructions.
- For plugin packages (OBS, Audacity, DaVinci Resolve, Reaper, Blender, Kdenlive, etc.), ALWAYS check upstream releases for pre-built binaries. When pre-built binaries exist, list the download link and install path as the primary alternative — the AUR package is unnecessary. Show the host app's plugin folder path and a brief install example (`wget` + `unzip`/`tar` + `mv` to plugin dir). This is MANDATORY for any plugin-type package.

## References

- Guide: `references/guide-pkg-analysis.md`
- Alternatives: `references/guide-alternatives.md`
```
