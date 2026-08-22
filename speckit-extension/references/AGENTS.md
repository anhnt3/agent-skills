<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-07-14 | Updated: 2026-07-14 -->

# references

## Purpose
Nine supporting documents that define detailed workflows for each phase of the `qa-spec-cycle` command. These are required reading before executing their corresponding phases; the command prose contains only summaries. Each reference is bundled via `build-zip.sh` and accessed at runtime via `.specify/extensions/dft-speckit/references/<name>.md`. All content is in Vietnamese.

## Key Files
| File | Description |
|------|-------------|
| `qa-context-template.md` | Template and guide for `.agents/qa-context.md` (project-level configuration file). Defines the 4-block structure: test pyramid (frameworks per layer), test tools (runner, CI), env setup (commands for seed/migrate/serve), auth/selector strategy. Explains "scan before ask" principle: command scans codebase/qa-context to auto-fill missing fields, only interviewing user if scan is inconclusive. **Pha 1 of qa-spec-cycle requires this.** |
| `coverage-matrix.md` | Coverage matrix workflow: from each FR/AC, select test layer (unit/integration/E2E/manual-only) + rationale by risk level. Enforces pyramid integrity: push assertions to lowest layer that proves the requirement. Mandatory gate: matrix must cover all N requirements listed in Pha 0 (if a requirement has no test row, mark explicitly as GAP + reason; no blank cells). **Pha 3 of qa-spec-cycle requires this.** |
| `manual-xlsx-format.md` | Data contract for CSV/JSON → XLSX conversion (Pha 4 of qa-spec-cycle). Defines 17 columns (ID, Tiêu đề, Nhóm, Ưu tiên, Loại, Tiền điều kiện, Dữ liệu test, Các bước, Kết quả mong đợi, Truy vết, Test tự động, Kết quả tự động, Kết quả thực tế, Trạng thái, Bug ID, Ghi chú, Nguồn BRD). Columns 1–11 + 17 = command-authored (design phase); 12 = read-only auto-update (CI results); 13–16 = tester-authored (execution). §3.1 defines row ordering: group by screen (L1) → item within screen (L2) → cross-cutting groups last (L3); row order is the handover contract, ID is only a merge key. XLSX output has 2 sheets: Testcases + Ma trận truy vết. **Pha 4 requires this; invokes `scripts/csv_to_xlsx.py`.** |
| `test-generation.md` | Auto-test authoring from manual testcases: generate unit/integration/E2E tests matching pyramid (Pha 5). Map each manual case to one or more auto tests at appropriate layer. Enforce: no fake-green (empty asserts, non-existent selectors blocked before reporting). Bounded fix: auto-fix test infra issues, escalate product bugs. **Pha 5 requires this.** |
| `environment-bringup.md` | Environment setup and running tests (Pha 7): commands to seed DB, migrate schema, start services, run test suite. Reads commands from qa-context.md; detects missing DB, network issues, or seed failures and escalates. No-defer: command handles environment problems, not the tester. **Pha 7 requires this.** |
| `quality-gate.md` | Checkpoints before releasing results (Pha 6): verify coverage (N requirements → N test rows), verify no fake-green, verify results are real (re-run flaky tests). Gate keeper: stop and escalate if any check fails; do not present results to user if quality is suspect. **Pha 6 requires this.** |
| `blocker-playbook.md` | Triage and decision tree for test failures (Pha 7 + Pha 10): is it a product bug, test infra issue, or environmental flake? For each failure, classify, propose fix scope (product PR, test fix, env mitigation), and escalate if needed. **Pha 7 (readiness blockers) and Pha 10 (triage) require this.** |
| `failure-classification.md` | Classification taxonomy for failures: product defect (bug to file), test defect (test code to fix), environment/flake (transient, re-run), infrastructure issue (deploy/setup problem). Clarifies what gets escalated to dev team vs. handled by qa-spec-cycle. **Pha 10 uses this.** |
| `traceability.md` | Traceability ledger and resume mechanism (Pha 0, Pha 8, Pha 11): checkpoint format for `qa-run.md` to track completion and resume mid-flow. Defines ledger structure, how to extract requirement IDs from spec, how to anchor test rows to requirements, how to validate coverage at the end. **Pha 0 (intake) and Pha 11 (finalize) require this; all phases update ledger.** |

## Subdirectories
(none)

## For AI Agents

### Working In This Directory
- **Each reference is a detailed runbook**: Edit as markdown procedure. Contains background (why this phase exists), concrete steps (what to do), checkpoints (when to stop and escalate), and examples (Vietnamese context or real codebase scenarios).
- **Command must read before executing**: The `qa-spec-cycle` command prose says "→ chi tiết: <file>" for phases that need these docs. This is a **must-read gate**, not optional. If a phase executes without reading the corresponding reference, the workflow is incomplete.
- **Integration across phases**: References coordinate (e.g., `coverage-matrix.md` defines what a GAP is, `traceability.md` defines how to report GAPs, `blocker-playbook.md` references failure classes from `failure-classification.md`). Edits to one may cascade; verify cross-references.
- **Vietnamese operational procedures**: Content assumes Vietnamese naming conventions (tiếng Việt module names, status values, error codes). Adapt examples when needed but preserve the structure and logic.
- **Bundling requirement**: All 9 files MUST be copied by `build-zip.sh` with `cp -R references/`. If a file exists here but `build-zip.sh` doesn't copy it, the installed extension will be broken (command tries to read a non-existent file at runtime).

### Testing Requirements
- **Verify all 9 files are bundled**: After running `build-zip.sh`, unzip the output and confirm all 9 references/*.md files are present: `unzip -l dist/dft-speckit-<ver>.zip | grep 'references/'`.
- **Verify cross-references**: Each reference cites others (e.g., `failure-classification.md` cited by `blocker-playbook.md`). Use grep to find internal citations and spot-check that cited files exist.
- **Test readability at runtime**: In a test `specify init` project with the extension installed locally, verify that paths like `.specify/extensions/dft-speckit/references/coverage-matrix.md` are readable (use Bash file read).
- **Validate format examples**: If a reference includes CSV/JSON format examples, run them through the corresponding validator (e.g., `csv_to_xlsx.py` to check CSV format from `manual-xlsx-format.md`).

### Common Patterns
- **Checkpoint markers**: Use checkboxes (`- [ ]`) to denote phase steps. Gating: if a step has a stop condition, mark with ⛔ or `[GATE]` and explain when to escalate.
- **Conditional paths**: References often have decision trees (e.g., "Is it a product bug?" → escalate vs. auto-fix). Use nested bullets or explicit if/then language.
- **Traceability**: `traceability.md` enforces linking requirements to tests. Other references (coverage-matrix, manual-xlsx-format) must cite requirement IDs consistently (FR-01, AC-03, etc.) for this to work.
- **No-fake-green**: `test-generation.md` and `quality-gate.md` both call out "fake-green" (empty asserts, missing selectors). Reinforce this in both to avoid bugs where tests pass but don't verify anything.

## Dependencies

### Internal
- `../extension.yml` — manifest (for context; no direct dependency).
- `../commands/qa-spec-cycle.md` — **only consumer**: reads these docs at each corresponding phase.
- `../scripts/csv_to_xlsx.py` — used by Pha 4; format defined in `manual-xlsx-format.md`.

### External
- **Spec Kit** — provides the environment to execute `qa-spec-cycle` command.
- **`.agents/qa-context.md`** — project config read by Pha 1, referenced by `qa-context-template.md`. Tester/dev team maintains this, not authored by these references.
- **`qa-run.md`** — ledger file created by qa-spec-cycle in the spec directory; format defined in `traceability.md`. Persists across command reruns to enable resume.
- **Codebase being tested** — scanned by Pha 2 for test framework, file structure, existing tests, environment readiness.

<!-- MANUAL: Any manually added notes below this line are preserved on regeneration -->

### Critical Bundling Note
Commands reference these 9 files via `.specify/extensions/dft-speckit/references/<name>.md` at runtime. The extension manifest (`extension.yml`'s `provides` section) does NOT gate bundling — it only lists commands and templates. If `build-zip.sh` does not include `cp -R references/`, installed extensions will fail when `qa-spec-cycle` tries to read the reference files. Always verify: (1) `build-zip.sh` includes `cp -R references/`, (2) zip contains all 9 files, (3) test the command in a clean environment to confirm files are readable at the runtime path.
