# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Two independently-packaged, independently-released add-ons for [Spec Kit](https://github.github.io/spec-kit/) (`specify` CLI). Both target DFT's internal spec-driven development workflow; content and user-facing prose are in Vietnamese.

- **`speckit-extension/`** — a multi-command **extension** (`extension.yml`, id `dft-speckit`). *Adds new* slash commands (namespaced `speckit.dft-speckit.<name>`) plus templates. Grows over time; new commands are added here, not in the preset.
- **`speckit-dft-preset/`** — a **preset** (`preset.yml`, id `dft-preset`). *Overrides existing* core commands (`speckit.constitution`, `speckit.specify`, `speckit.plan`, `speckit.checklist`) via `strategy: wrap`, plus a `ui-ux-checklist` template. Turns `/speckit.specify` into a sequential business-analyst interview (via AskUserQuestion) and `/speckit.constitution` into a codebase-scan + interview constitution generator (budget ≤7 principles, MUST/Rationale self-check gate).

The two are orthogonal: extension = new commands, preset = behavior overrides on core commands.

## Architecture

Both packages share the same shape, defined by their manifest:
- **`extension.yml` / `preset.yml`** is the source of truth. Every command and template must be declared under `provides` — a `commands/*.md` or `templates/*.md` file that isn't declared in the manifest does nothing.
- **`commands/*.md`** — one file per command. Frontmatter `description` + the process the AI agent follows. This is prompt/instruction content, not code.
- **`templates/*.md`** — fixed output scaffolds (constitution, checklists, roadmap). Preset templates use `strategy: replace` to swap core templates; the interview logic references these template contents, so the preset is self-contained (works on a fresh project with no existing constitution).
- **`scripts/`** — supporting scripts (e.g. `csv_to_xlsx.py`, self-bootstraps a `.venv` + `openpyxl` on first run). `scripts/.venv/` is committed-adjacent; ignore it when exploring.

Key constraints (verified against spec-kit 0.12.11 source — see `docs/research/speckit-addon-review-2026-07-11.md`):
- `preset add` does **not** write the live `.specify/memory/constitution.md`; the only way to create it is running the overridden `/speckit.constitution` (this is why the preset wraps that command). Without a constitution, `/speckit.specify` warns and skips its GĐ4 cross-check — every other stage still runs.
- Preset command overrides are **materialized snapshots** in the agent's command dir — spec-kit does not re-resolve the stack at runtime. Upgrading the `specify` CLI (or re-running `specify init`) can silently clobber them with fresh core versions. After every `specify` upgrade: `specify preset disable dft-preset && specify preset enable dft-preset`, then verify with `specify preset resolve speckit.specify`, and run `scripts/check-core-anchors.sh <project>` to confirm the core section names the preset anchors to ("Pre-Execution Checks", "Specification Quality Validation", …) still exist verbatim.
- Wrap commands declare `strategy: wrap` in **both** `preset.yml` and the file frontmatter (a legacy code path in spec-kit reads it from frontmatter).

## Common commands

Adding a new extension command:
1. Create `speckit-extension/commands/<name>.md` (frontmatter `description` + process).
2. Declare it in `extension.yml` under `provides.commands` as `speckit.dft-speckit.<name>`.
3. Scripts go in `scripts/`.

Local dev install:
```bash
# --dev: the extension ARGUMENT is the local path (not a flag value). Passing the
# path as a trailing arg after a name fails with "unexpected extra argument".
specify extension add /path/to/speckit-extension --dev --force
specify preset add --dev ./speckit-dft-preset
```
Dev install copies the **whole directory** (drags in `.omc/`, `dist/`, `release.sh`, `build-zip.sh`) — noise, but harmless. The release zip is clean (see below); use the zip path to verify what actually ships.

Testing the packaged install (verifies build-zip output, not just the source tree):
```bash
# 1. Build + eyeball the zip contents
speckit-extension/build-zip.sh && unzip -l speckit-extension/dist/dft-speckit-<ver>.zip
# 2. Serve locally (--from rejects file:// paths; needs HTTPS/localhost) and install
#    into a throwaway `specify init --here --integration claude` project.
(cd speckit-extension/dist && python3 -m http.server 8799 &)
yes y | specify extension add dft-speckit --from http://localhost:8799/dft-speckit-<ver>.zip --force
# --from prompts an "Untrusted Source" confirmation -> pipe `yes y`.
```
The installed tree lands at `<project>/.specify/extensions/dft-speckit/`. **Gotcha this caught:** commands reference bundled `references/*.md` and `scripts/*.py` by the path `.specify/extensions/dft-speckit/<...>`, so `build-zip.sh` must `cp -R` every such support dir. A support dir that exists in the source but isn't copied in `build-zip.sh` ships a broken command (the manifest's `provides` only lists commands/templates — it does **not** gate what gets bundled). After install, assert the referenced dirs are present, e.g. `ls .../references/` returns all 9 files.

Smoke-test `csv_to_xlsx.py` standalone (its `.venv` self-bootstrap needs network on first run only):
```bash
python3 speckit-extension/scripts/csv_to_xlsx.py cases.json out.xlsx   # or 16-col CSV
```

Release — **manual only, by design** (no GitHub Actions; the old release workflows were deliberately removed). Each package has its own `build-zip.sh` + `release.sh`, reading version from its manifest:
```bash
# Bump the version in the manifest first, then:
speckit-extension/release.sh              # or: release.sh 1.2.0 to force version
speckit-dft-preset/release.sh
# -> builds zip, creates/updates GitHub Release (tag <pkg>-v<version>), uploads asset,
#    rewrites the install URL in the package README.
```
Version policy: both packages were deliberately **reset to a 0.0.1 baseline** (all pre-reset tags/releases deleted); versions increase monotonically from there. Never resurrect the old 1.x/4.x tag series.

Install from a release: `specify extension add dft-speckit --from <https-url-to-zip>` / `specify preset add --from <url>`. `--from` accepts HTTPS/localhost only, not local file paths — the URL must point at the release zip asset.

## Conventions

- Bump the version in the manifest (`extension.yml` / `preset.yml`) **before** running `release.sh`; the tag, zip name and README install URL all derive from it.
- Command/template `.md` files are agent instructions — edit them as prompts (clear process, fixed output format), not as code.
- User-facing docs and command content are written in Vietnamese; match that when editing.
- The `.claude/skills/speckit-addon-reviewer` skill reviews these packages (deterministic lint + prompt-semantics critic). Its `references/speckit-mechanics.md` cheatsheet must be kept in sync with upstream findings — update it when new spec-kit mechanics are verified (see `docs/research/speckit-addon-review-2026-07-11.md` §2).
- Compat with upstream is anchored on verbatim core wording; `scripts/check-core-anchors.sh` (run against a specify project or a spec-kit clone) must pass before adopting a new spec-kit version. Last verified: spec-kit 0.12.4 (real install test) and 0.12.11 (source clone), 2026-07-11.
