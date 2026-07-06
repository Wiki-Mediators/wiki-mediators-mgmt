---
status: "research-input"
note: "Reference material for designing the dependency-catalog system; not roadmap truth and not a strategy spec."
---

# Building a Maintainable Dependency Wiki and Windows Bootstrap Installer for a Multi-Agent Markdown Vault

## TL;DR
- **Build a two-layer system: a single machine-readable manifest (`dependencies.yaml`) as the source of truth, rendered to human/agent-readable markdown, plus per-platform recipe files — and treat your existing git vault as the historical action log.** This cleanly separates the portable "what + why" (principle) from the OS-specific "how" (Windows now, Ubuntu later).
- **For the Windows bootstrap, use winget's declarative DSC configuration (`winget configure`, a YAML file) as the spine, wrapped in an idempotent PowerShell script that picks a working folder, inits/copies the repo, verifies deps, and starts git commits — and keep your already-downloaded installers in an offline bundle for the proprietary tools (NinjaTrader) and exact-version pins winget cannot reliably reproduce.**
- **Pin Python with `pyproject.toml` + `uv.lock` (uv is the 2026 default) and vendor a wheelhouse via `pip download` for offline rebuilds; pin a specific Python runtime; and add lightweight drift detection (`winget configure test`) so the catalog can be checked against reality.**

## Key Findings

1. **A personal toolchain SBOM is achievable with off-the-shelf concepts.** NTIA's "The Minimum Elements For a Software Bill of Materials (SBOM)," published July 12, 2021 pursuant to Executive Order 14028, defines exactly seven data fields — **Supplier Name, Component Name, Version of the Component, Other Unique Identifiers, Dependency Relationship, Author of SBOM Data, and Timestamp** (CISA's August 2025 update renamed "Supplier Name" to "Software Producer"). These map directly onto the fields you want to record. CycloneDX (OWASP) is the security-focused, compact, frequently-updated standard; SPDX (Linux Foundation) is compliance/license-focused. For a solo dev, you don't need a full CycloneDX document — but its field model (component name, version, `purl`, supplier, hashes, dependency graph) is the right schema to imitate in your own YAML manifest.

2. **winget is the right Windows spine, but it cannot reliably reproduce arbitrary old versions, and proprietary tools aren't in it.** winget is available on Windows 11, modern versions of Windows 10, and Windows Server 2025 as part of the App Installer; it supports `winget export`/`import` of a JSON app list (default source holds more than four thousand unique packages), and supports declarative `winget configure` (PowerShell DSC) for one-command, idempotent, drift-checkable setup. BUT: the community repo (winget-pkgs) only stores manifests pointing at publisher URLs, verified by SHA256; old versions get purged when download links die, and NinjaTrader is not in the repo at all. This is the decisive reason to keep your Downloads-folder installers as an offline bundle.

3. **uv has become the 2026 default for Python reproducibility.** `pyproject.toml` declares constraints; `uv.lock` pins exact versions with hashes across platforms; uv supports reading and exporting PEP 751 lockfiles via `uv export --format pylock.toml` while keeping its own cross-platform `uv.lock` as the primary format, and `uv export --format requirements-txt` regenerates a pip-compatible `requirements.txt` on demand. For offline rebuilds, `pip download -r requirements.txt -d wheelhouse` (run on a matching Python version/platform) plus `pip install --no-index --find-links` is the standard air-gapped pattern.

4. **The "principle vs. action log" split is a solved problem in two communities at once.** Docs-as-code teams keep a single structured source (YAML/JSON) and *generate* the human-readable markdown (tools like yaml-docs, or hand-rendered). Infrastructure-as-code teams (Ansible, Nix, devcontainers) separate an abstract declaration of intent from platform-specific execution. Your portability requirement is exactly the "same intent, different OS" problem those tools solve.

## Details

### 1. Dependency inventory & cataloging

**Discover what's installed.** Start by harvesting reality, then curate:
- `winget export -o installed.json --include-versions` produces a JSON list of everything winget can match against its sources. It will warn for apps it can't match (which is most proprietary tools) — those warnings are your "scattered installer" list.
- Cross-check `winget list` (shows all Add/Remove Programs entries, even unmanaged ones) and your `Downloads` folder. The unmatched entries plus loose installers in Downloads are precisely the manually-acquired tools (NinjaTrader, viewers, one-off utilities) that need manual cataloging.
- For your own Python tools, derive library deps from imports / `pyproject.toml`; since they're stdlib-only "dumb tools," many will have zero third-party deps — record that explicitly (it's a feature, not an omission).

**What to record per dependency** (modeled on NTIA's seven minimum elements + CycloneDX component fields, plus your operational needs):
- `name` — tool/component name
- `version` — exact pinned version (and version *string* as the tool reports it)
- `kind` — `os-tool` | `runtime` | `python-lib` | `proprietary-app`
- `supplier` / `source_url` — download URL or package source
- `purl` or package id — e.g. `pkg:pypi/...`, or `winget:Git.Git`
- `install_location` — where it lands on disk
- `depends_on` — what requires it (dependency relationship)
- `install_cmd` — exact command (winget/scoop/manual installer + silent switches)
- `verify_cmd` — how to check it's present and correct (e.g. `git --version`, `python --version`)
- `sha256` — hash of the archived installer (critical for proprietary tools you store yourself)
- `notes` — license, why it's needed, gotchas

**Principle/truth vs. historical action log.** Keep two distinct artifacts:
- **Truth layer** (`dependencies.yaml` + generated `catalog.md`): the *current desired state* — what must exist and why. This is declarative and overwritten as truth changes.
- **Action log** (git history + a human `CHANGELOG.md` / dated `actions/` notes): the *append-only record of what was done* — "2026-06-14: downloaded NinjaTrader 8.1.x installer, archived to bundle, recorded sha256." Your existing git-based change logger and "vault is a git repo + gitk" Layer-1 recovery *is* this action log; lean into it rather than duplicating it.

### 2. Version pinning & reproducibility

**Python (language level).** The 2026 consensus tooling is uv (Astral):
- Declare direct deps in `pyproject.toml`; run `uv lock` to produce `uv.lock`, a cross-platform lockfile capturing exact versions + hashes. `uv sync --locked` reproduces the environment exactly.
- `uv.lock` is universal (all platforms/markers) where pip-tools' `requirements.txt` is single-platform — relevant to your Windows-now/Ubuntu-later goal.
- For pip-only environments, pip-tools (`pip-compile`/`pip-sync`) remains valid. pip added an experimental `pip lock` command in 25.1 (released April 26, 2025) writing PEP 751 `pylock.toml`, and added experimental `pip install -r pylock.toml` in 26.1 (April 2026); PEP 751 itself was accepted in April 2025. Note `pip lock` locks only the current platform/Python version. Until pip 26.1, only uv could install from a `pylock.toml`.
- Generate a `requirements.txt` artifact on demand with `uv export --format requirements-txt` for any tooling that needs it.
- **Vendoring / offline:** `pip download -r requirements.txt -d wheelhouse` (or a `uv`-built wheelhouse) on a machine matching the *exact* target Python version and platform, then `pip install --no-index --find-links=wheelhouse -r requirements.txt`. Use `--generate-hashes` for hash-pinned, reproducible installs. Since your tools are stdlib-only, this mostly matters for any future libraries.

**Pin the Python runtime itself.** Don't assume "whatever Python is on the box." Options, lowest-friction first:
- Pin via the manifest + winget/scoop to a specific minor (e.g. `Python.Python.3.12`) and verify with `python --version`.
- For maximum determinism, ship the **Windows embeddable package** (a ~10 MB zip of a specific Python build) in your offline bundle and point your tools at it; it's portable, requires no admin, and doesn't touch the registry or system PATH (it needs a couple of tweaks — uncomment `import site` in the `._pth`, add `get-pip.py` — to support pip).
- The new Python install manager (`py install`, `pymanager`) supports offline installs via `--download=<PATH>` to build an offline index and `py install --source=<PATH>\index.json`.

**Windows external tools (OS level).** This is where reproducibility is hardest and the research is decisive:
- Install an exact version: `winget install --id <Publisher.App> --version <x.y.z> -e`. List what versions are still available with `winget show <id> --versions`.
- Prevent drift-by-upgrade with `winget pin add --id <id> --version <x.y.*>` (gating), `winget pin add <id> --blocking` (hard block), `winget pin list/remove/reset`. The pin subcommand reached general release in mid-2024.
- **Critical limitation:** exact-version installs only succeed if *both* the manifest still exists in winget-pkgs *and* the publisher's URL still serves that exact hash-matching binary. Old manifests are routinely removed by policy when download links die (e.g. winget-cli Issue #2602, where a maintainer confirmed Mailbird's download URL "always points to the latest version which prevents historical versions from being in the repository"). And `winget pin` has open, unresolved bug reports where pins were ignored — e.g. microsoft/winget-cli Issue #5244 ("winget pin is ignored and package is upgraded anyway"), filed against winget v1.9.25200, where a `--blocking` pin on mRemoteNG still showed "1 upgrade available." **Treat pinning as best-effort, not a guarantee.**
- **Therefore: for any tool whose exact version you must reproduce, archive the installer binary yourself** (store the EXE/MSI), record its version + SHA256 in the manifest, and install from your stored copy. Microsoft's sanctioned mechanisms are a private/REST source or installing from a local manifest (`winget install -m <manifest>`). For a solo dev, a plain `installers/` folder in the offline bundle is simpler and sufficient.

### 3. Windows provisioning / bootstrap patterns

**Option comparison for a low-maintenance solo dev:**

| Approach | Strengths | Weaknesses | Fit |
|---|---|---|---|
| **winget** | Built into Win11; `export`/`import`; declarative `configure` (DSC); idempotent; drift test | Can't reliably pin/re-acquire old versions; not all tools present; App Installer can go stale on servers | **Primary spine** |
| **Scoop** | No admin/UAC; user-dir installs; clean PATH via shims; JSON manifests; you can host a *local bucket* (git repo) with your own pinned manifests | Smallest catalog; dev-tool focused; some versioned-install bugs | **Great for your own/CLI tools + local pinned manifests** |
| **Chocolatey** | Largest catalog (over 10,000 pre-made packages on the Community Repository); many installer formats; strong automation/Ansible | Advanced features paywalled; community package lag | Optional |
| **Plain PowerShell** | Total control; no dependency on a package manager; can drive the whole flow | You write all idempotency/error handling yourself | **The wrapper/orchestrator** |
| **Manifest-driven (winget configure YAML)** | Declarative desired-state; reorder-independent; `test` for drift; can be hosted remotely | DSC resource ecosystem still maturing; some resources need elevation | **Recommended config format** |

**Offline capability is the deciding factor for you.** Because all installers are already in Downloads, your bootstrap should prefer local artifacts: Scoop can install from a local bucket + locally-stored archives; winget can install from a local manifest; and proprietary tools install from your archived EXEs directly. A pure "script that downloads from the internet" is the *least* aligned with your situation.

**"User picks a working folder → repo → commits" flow.** PowerShell can present a native folder picker via `System.Windows.Forms.FolderBrowserDialog` (with a cancel-handling loop so it doesn't crash). After selecting the path, the script inits or clones/copies the vault repo there, verifies deps, and starts the change logger.

**Making the PowerShell script idempotent and safe to re-run** (the research is unanimous on the pattern):
- Always **check current state before acting** — `if (-not (Test-Path $path)) { New-Item ... }`; query "is this version installed?" before installing.
- Prefer idempotent cmdlets (`Set-*` over `Add-*`); add `-Force` only where the cmdlet isn't naturally idempotent.
- Use `$ErrorActionPreference = "Stop"` and wrap risky steps in try/catch.
- Make every step re-entrant: re-running the script on an already-provisioned machine should report "already in desired state" and change nothing. `winget configure` gives you this for free (it only applies what differs).

### 4. Golden-image vs bootstrap-script vs manifest

- **Golden image / offline bundle (bundle a pinned runtime + tools):** Maximum reproducibility and offline capability; "replace, don't repair." For you this means a folder/zip containing the embeddable Python, the archived installers, the wheelhouse, and the manifests. Downside: larger to store, must be refreshed for security updates.
- **Script-that-downloads:** Smallest to store, always-latest — but fragile (dead URLs, version drift) and useless offline. Worst fit given dead-link risk for old versions.
- **Document-and-reacquire:** Lowest storage, but depends on the tool still being downloadable at the right version — which the research shows is *not* guaranteed for winget-pkgs old versions or proprietary tools.

**Verdict for you:** A **hybrid offline bundle is the right primary strategy** precisely because you already have the installers. Bundle the proprietary/hard-to-pin pieces (NinjaTrader, specific installer versions, embeddable Python, wheelhouse) offline; use winget/scoop live-download only for ubiquitous, always-current tools where latest is fine (Git, viewers). Document-and-reacquire is the fallback tier for anything trivial to replace.

### 5. Cross-platform principle portability

Structure the catalog so **the abstract manifest is platform-neutral and the recipes are platform-specific** — the pattern Ansible (intent in playbooks, modules per-OS), Nix (one package set across OSes), and devcontainers all use to solve "same intent, different OS":
- `dependencies.yaml` — the portable truth: each dependency's name, purpose, role, verify command *concept*. No `winget`/`apt` commands here.
- `recipes/windows.yaml` (or the winget DSC file) — concrete `winget`/`scoop`/installer commands.
- `recipes/ubuntu.yaml` — future `apt`/`snap`/Nix commands for the same logical dependencies.
- A small renderer maps manifest → `catalog.md` so humans and agents read one coherent doc.

This means when you move to Ubuntu, you keep `dependencies.yaml` unchanged and write only a new recipe file — the "why we need Git" principle is portable; only "how to install Git" changes. Note: the *running installer script stays Windows-only for now*; only the documentation/manifest layer is portable in principle. (One developer's widely-cited experience report found that maintaining cross-OS install *logic* in Ansible became "a maintenance nightmare," and that pushing package selection down to a single Nix package set eliminated the per-OS branching — a useful signal if your recipe files ever proliferate.)

### 6. Maintainability & multi-agent use

- **Single source of truth, dual format.** Keep one machine-readable manifest (YAML or JSON) and *generate* the markdown. This is the docs-as-code pattern (Talos/Sidero's docgen, yaml-docs, Mintlify's YAML-frontmatter approach): humans and AI agents read the rendered markdown; agents and scripts parse the manifest. Avoid hand-maintained markdown tables (they rot and are painful to edit).
- **AI-agent-friendly structure.** The 2026 trend (AGENTS.md, SKILL.md, Google Labs' DESIGN.md, machine-readable manifests as "OpenAPI for the CLI") confirms the right move: give agents an authoritative, structured, machine-readable contract so they don't improvise. Your YAML manifest *is* that contract. Add YAML frontmatter and clean headings to the rendered markdown for retrieval.
- **Prevent rot with conventions:** one manifest owns the truth; markdown is generated, never hand-edited; every dependency change is a git commit (your action log); the manifest lives in the vault so the same agents that read the vault can read and update it.
- **Drift detection (catalog vs. reality).** `winget configure test -f baseline.dsc.yaml` reports whether the machine still matches the declared state — "If a technician manually uninstalled a tool or changed a version, this test will flag the machine as non-compliant." Note DSC v3 dropped automatic enforcement/background drift correction — you trigger checks yourself via a scheduled task or a "dumb tool." Complement with a tiny stdlib-Python checker that runs each `verify_cmd` and diffs against the manifest — squarely in the spirit of your existing deterministic tools.

### 7. Concrete structure recommendation

**Dependency-wiki file/folder structure (inside the vault):**

```
/deps/
  dependencies.yaml         # SOURCE OF TRUTH (portable: what + why + verify concept)
  catalog.md                # GENERATED from dependencies.yaml (human/agent readable)
  recipes/
    windows.dsc.yaml        # winget configure DSC file (install how, Windows)
    windows-manual.md       # proprietary/manual steps (NinjaTrader, archived installers)
    ubuntu.yaml             # FUTURE: same deps, apt/nix recipes
  bundle/                   # offline bundle (gitignored or git-LFS / external)
    installers/             # archived EXE/MSI + .sha256 sidecars
    python-embed/           # pinned embeddable Python zip
    wheelhouse/             # pip download output for offline pip install
  CHANGELOG.md              # human action log (append-only)
  tools/
    render_catalog.py       # manifest -> catalog.md (stdlib)
    check_drift.py          # run verify_cmds, diff vs manifest (stdlib)
/bootstrap/
  bootstrap.ps1             # the Windows installer/orchestrator
```

**`dependencies.yaml` sketch:**

```yaml
meta:
  generated_by: render_catalog.py
  schema: personal-sbom-v1
dependencies:
  - name: Git
    kind: os-tool
    purpose: version control + Layer-1 recovery (vault is a git repo)
    version: "2.45.x"
    source_url: https://git-scm.com
    package_id: winget:Git.Git
    verify_cmd: "git --version"
    depends_for: [change-logger, vault-recovery]
  - name: Python runtime
    kind: runtime
    version: "3.12.x"
    package_id: winget:Python.Python.3.12
    bundle: python-embed/python-3.12-embed-amd64.zip
    verify_cmd: "python --version"
  - name: NinjaTrader 8
    kind: proprietary-app
    version: "8.1.x"            # record exact build at archive time
    source_url: https://ninjatrader.com (login-gated, latest only)
    bundle: installers/NinjaTrader.exe
    sha256: "<hash>"
    verify_cmd: "<path-exists check>"
    notes: NOT in winget; must install from archived installer
```

**Windows bootstrap script — step-by-step spec for Codex to build:**

1. **Preflight.** `$ErrorActionPreference="Stop"`. Detect/relaunch elevated only if needed. Confirm winget present; if missing/stale, register App Installer (`Add-AppxPackage -RegisterByFamilyName -MainPackage Microsoft.DesktopAppInstaller_8wekyb3d8bbwe`). Confirm Git present (or install from bundle/winget).
2. **Select working folder.** Show `FolderBrowserDialog` in a cancel-handling loop; store `$WorkRoot`. Idempotent: if a vault already exists there, offer to reuse.
3. **Place the vault.** If `$WorkRoot\vault\.git` doesn't exist: clone the repo (or copy from bundle), else `git -C $WorkRoot\vault pull`/leave as-is. Init if brand-new (`git init`, first commit).
4. **Reconstitute the toolchain (idempotent).** For each manifest dependency: check `verify_cmd`; if absent, install via its recipe — `winget configure -f recipes\windows.dsc.yaml --accept-configuration-agreements` for catalog tools; for proprietary/pinned tools, run the archived installer from `bundle\installers` with silent switches; deploy embeddable Python from `bundle\python-embed`; `pip install --no-index --find-links bundle\wheelhouse -r requirements.txt` for libraries.
5. **Verify.** Re-run every `verify_cmd` (and/or `winget configure test`); run `tools\check_drift.py`; write a provisioning report into the vault.
6. **Start logging/commits.** Register the change-logger as a startup item / scheduled task pointed at `$WorkRoot\vault`; make an initial "bootstrap complete on <machine> <date>" commit so the action log captures the event. (Reference pattern: gitwatch-style "watch a folder, commit on change" daemons — on Windows you can replicate this with a `FileSystemWatcher`-driven PowerShell loop or a scheduled task that runs `git add -A && git commit`.)
7. **Idempotency guarantee.** Re-running the whole script on a provisioned machine reports "already in desired state" and changes nothing.

## Recommendations

**Stage 1 — Establish the truth layer (do first, low effort).**
- Create `dependencies.yaml` and write `render_catalog.py` (stdlib) to generate `catalog.md`. This is another "dumb tool" and fits your toolkit philosophy.
- Harvest current state: `winget export`, `winget list`, and inventory the Downloads folder. Populate the manifest. Record SHA256 for every proprietary/archived installer.
- Commit everything; the git history becomes your action log. *Benchmark to proceed:* manifest covers every tool you can name and every loose installer in Downloads.

**Stage 2 — Build the offline bundle + Python pinning.**
- Move the relevant installers from Downloads into `bundle/installers/` with `.sha256` sidecars. Add the embeddable Python zip. Build a wheelhouse (`pip download`) for any non-stdlib libs.
- Add `pyproject.toml` + `uv.lock` for your tools (even if deps are empty today — it future-proofs).
- *Benchmark:* you can reconstruct the Python environment on an offline machine.

**Stage 3 — Write the bootstrap script.**
- Implement `bootstrap.ps1` per the 7-step spec, idempotent throughout. Author `recipes/windows.dsc.yaml` for the winget-installable tools.
- Test on a fresh Windows VM (or Windows Sandbox) end-to-end, then re-run to prove idempotency.
- *Benchmark:* a clean VM goes from zero to a committing vault in one run, and a second run is a no-op.

**Stage 4 — Maintainability & portability.**
- Add `check_drift.py` and schedule it (weekly) or run on demand; wire `winget configure test` for OS-tool drift.
- Stub `recipes/ubuntu.yaml` now (even incomplete) to keep the principle/recipe split honest.

**Thresholds that change the plan:**
- *If you ever add many third-party Python libs or distribute tools to others* → adopt a real CycloneDX SBOM (generate with `cyclonedx-py`) and Renovate/Dependabot for CVE alerts. (Note: Dependabot's pip ecosystem doesn't parse `uv.lock`; either keep an exported `requirements.txt` or use Renovate, which has native uv-lockfile support.)
- *If you outgrow a single machine or want true determinism across OSes* → evaluate Nix/Home Manager (one package set, Windows via WSL) rather than maintaining parallel recipe files.
- *If winget pin proves unreliable for a critical tool* (the open bugs suggest it might) → rely solely on the archived installer + exact-version install, and drop the pin.

## Caveats

- **winget version pinning is best-effort, not a guarantee.** There are open, unresolved GitHub issues where pins were ignored during `winget upgrade --all` (e.g. #5244, #3484, #4333), and old manifests are routinely purged from the community repo when publisher download links die (#2602, Discussion #98586). Do not depend on winget to reproduce a specific old version — archive the binary.
- **NinjaTrader is not in winget** and its download is login-gated to the latest release with no public per-version permalink; it *must* be archived locally and cataloged manually. (This was inferred from a winget catalog search returning only the unrelated `Ninja-build.Ninja` build system, plus NinjaTrader's manual-download-only install guide; I found no official NinjaTrader manifest in microsoft/winget-pkgs.)
- **DSC v3 removed automatic drift correction** (no background Local Configuration Manager); `winget configure test` detects drift but you must trigger remediation yourself. Plan for a scheduled task or manual run.
- **Offline bundles need periodic refresh** for security updates; an unmaintained golden image accumulates vulnerability debt. Put a calendar reminder to refresh pinned versions.
- **`pip download` wheels are platform/Python-version specific** — build the wheelhouse on a machine matching your exact target, or pass `--platform`/`--python-version`/`--abi`. This is the most common offline-install failure mode.
- **Some security-sensitive cautions surfaced in sources** (e.g. DSC-via-COM can evade EDR) are about *abuse* of these tools and aren't directly relevant to a solo dev's setup, but they confirm `winget configure` runs real PowerShell — only apply configuration files you trust/author.
- **The "YAML/Markdown as AI contract" framing** (AGENTS.md, DESIGN.md, "specification-driven development") is an emerging 2026 trend, not a settled standard; adopt the *practice* (machine-readable single source of truth) rather than betting on any one file-name convention.