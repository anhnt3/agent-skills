# Review toàn dự án đối chiếu source spec-kit v0.12.11

> Review ngày 2026-07-11. Phương pháp: clone `github/spec-kit` (0.12.11, commit `1be4299`), đọc sâu
> `src/specify_cli/` (extensions, presets, resolver, registrar, bundler) + toàn bộ file của repo này
> (2 package, skill reviewer, workflows, scripts, docs). Mọi kết luận chịu lực đều được xác minh
> trực tiếp trên source upstream, có dẫn file/dòng.
>
> Vai trò tài liệu: (1) biên bản review + trạng thái xử lý từng finding; (2) **bổ sung tri thức cơ chế
> upstream** mới phát hiện — dùng để cập nhật `speckit-mechanics.md` của skill reviewer và làm căn cứ
> cho các quyết định vận hành về sau.

## TL;DR

**Không có sai lầm kiến trúc.** Mọi cơ chế mà preset/extension dựa vào đều có thật và đúng trong
source 0.12.11 — kể cả các neo nguyên văn vào core template. Toàn bộ finding nằm ở tầng
**vận hành/đóng gói/tài liệu**, đã xử lý trong đợt fix cùng ngày (bảng §3). Hai quyết định chủ đích
của maintainer được ghi nhận làm chính sách: **(a)** version reset về `0.0.1`, tag/release cũ đã xoá;
**(b)** release **chỉ** bằng `release.sh` thủ công (zip lên GitHub Release) — không dùng workflow tự động.

---

## 1. Những giả định đã xác minh ĐÚNG với source upstream

| Giả định của repo này | Bằng chứng trong spec-kit 0.12.11 |
|---|---|
| `strategy: wrap` + `{CORE_TEMPLATE}` là cơ chế thật | `VALID_PRESET_STRATEGIES` (`presets/__init__.py:230-245`); thiếu placeholder → `PresetValidationError` (`:3256-3262`) |
| Neo "Pre-Execution Checks", "Specification Quality Validation", "For AI Generation", "LIMIT: Maximum 3 [NEEDS CLARIFICATION]", "Make informed guesses" trong preset specify | Khớp **nguyên văn** `templates/commands/specify.md` (dòng 21, 123-128, 144, 293) |
| Branch do hook `before_specify` (git extension) tạo; spec dir + `feature.json` do core tạo → vá hook của preset là đúng và đủ | `specify.md:76, 99-106, 278`: "Branch creation is handled by the `before_specify` hook (git extension). Spec directory and file creation are always handled by this core command." Core không còn gọi `create-new-feature.sh` |
| `specify preset resolve` resolve được cả template của preset lẫn **extension** (`ui-ux-checklist`, `domain-template`, `roadmap-template`) | `PresetResolver.resolve` tier 2 = preset dirs, tier 3 = extension dirs (`presets/__init__.py:2632-2762`); CLI subcommand `preset resolve` tại `presets/_commands.py:308` |
| `preset add` KHÔNG ghi `.specify/memory/constitution.md` → override command `speckit.constitution` là đường duy nhất ghi file sống | grep `constitution` trong `src/specify_cli/presets/` = rỗng; xác nhận lại kết luận `constitution-quality.md` §6 |
| `.extensionignore` là cơ chế thật | `_load_extensionignore` (`extensions/__init__.py:826-911`), gitignore-compatible qua `pathspec` |
| Layout zip: 1 thư mục gốc chứa manifest; `--from` chỉ HTTPS/localhost + trust prompt default-deny | `install_from_zip` (`extensions/__init__.py:1470-1533`); URL guard (`extensions/_commands.py:426-458`) |
| `analyze`/`converge` chỉ bốc tên nguyên tắc + câu `MUST`/`SHOULD`; MUST violation = CRITICAL | `analyze.md:113,157,249`; `converge.md:86` — nền của constitution override vững |
| Tên command extension `speckit.dft-speckit.<name>` đúng pattern bắt buộc | `EXTENSION_COMMAND_NAME_PATTERN` (`extensions/__init__.py:322`) |
| `requires.speckit_version` được cưỡng chế cứng lúc cài | `check_compatibility` qua `SpecifierSet` (`extensions/__init__.py:1283-1313`; preset tương đương) |

Điểm mạnh thiết kế được ghi nhận (giữ nguyên, không đụng): neo đếm từ nguồn ngoài; sổ theo dõi persist
ra file `.specify/interviews/`; bàn giao vật lý spec→plan qua section trong `spec.md`; phân tầng
trọng yếu/thứ yếu chống interview-fatigue; no-defer kèm gate an toàn DB dùng-một-lần; merge xlsx theo
`ID`; HALT non-interactive của `qa-spec-cycle`; ủy thác pha nặng cho subagent để giữ context.

## 2. Tri thức cơ chế upstream MỚI (bổ sung cho `speckit-mechanics.md`)

Các fact dưới đây lấy từ source 0.12.11, là phần cheatsheet cũ chưa có hoặc nói chưa chính xác:

1. **Preset override là snapshot đã materialize, không resolve lại lúc chạy.** `_register_commands` +
   `_reconcile_composed_commands` (`presets/__init__.py:589-865`) compose nội dung rồi **ghi hẳn** vào
   thư mục command của agent; chỉ reconcile lại khi có sự kiện lifecycle của preset
   (install/remove/enable/disable/set-priority). **Nâng cấp CLI spec-kit hoặc chạy lại `specify init`
   có thể ghi đè file đã compose bằng bản core mới → override lặng lẽ biến mất** cho tới khi cài lại
   preset. Docs upstream xác nhận: "Agents do not re-resolve the stack each time"
   (`docs/reference/presets.md:142`). → Runbook: sau mỗi lần nâng cấp `specify`, cài lại preset (hoặc
   `preset disable` → `enable`) rồi kiểm `specify preset resolve speckit.specify`.
2. **`{CORE_TEMPLATE}` được thay bằng `str.replace` — MỌI occurrence đều được expand**, không phải
   "đúng một lần" (`presets/__init__.py:3263`). Luật lint "đúng một token" vẫn là best-practice (tránh
   nhân đôi core body), nhưng bản chất kỹ thuật là ≥1, tất cả đều bị thay.
3. **Không tồn tại `.presetignore`.** Preset copy nguyên thư mục bằng `shutil.copytree` không ignore
   (`presets/__init__.py:1540`) — khác hẳn extension. Build-zip của preset phải tự lọc rác (repo này
   đã làm: prune `.omc/`, `.DS_Store`).
4. **Hook event name sai chính tả chết âm thầm.** Validator không có whitelist tên event; `after_speciy`
   pass validation và không bao giờ chạy — core template chỉ tra đúng chuỗi `before_/after_<phase>`.
5. **Claude integration hiện là skills-based**: command materialize thành
   `.claude/skills/<command-name>/SKILL.md` (`integrations/claude/__init__.py:38-58`), không phải
   `.claude/commands/*.md` (đường cũ chỉ còn là legacy fallback).
6. **Có một code path legacy đọc `strategy: wrap` từ frontmatter của FILE command**
   (`presets/__init__.py:1318`), song song đường chính đọc từ manifest. → File command wrap nên khai
   `strategy: wrap` ở cả frontmatter (đã áp dụng cho 4 command của dft-preset).
   **Bẫy đi kèm (thực nghiệm trên 0.12.4, phát hiện khi verify đợt fix này)**: `description`
   frontmatter dài quá ~1 dòng sẽ bị YAML emitter wrap đa dòng lúc materialize thành
   `.claude/skills/<cmd>/SKILL.md`, và `inject_argument_hint` chèn `argument-hint:` ngay sau dòng
   vật lý đầu tiên → **cắt đôi description, frontmatter gãy YAML**. → description phải ngắn
   (~≤60 ký tự); đã kiểm chứng cả 4 command sau fix: cài thật, parse YAML frontmatter đều pass,
   không còn literal `{CORE_TEMPLATE}` trong bản materialize.
7. **Đường phân phối chính thức của upstream**: GitHub tag archive
   (`.../archive/refs/tags/vX.Y.Z.zip` — installer chấp nhận layout nested 1 tầng) hoặc catalog entry
   kèm `sha256` (verify từ 0.11.7, `EXTENSION-PUBLISHING-GUIDE.md:95-124,323`). **Không có lệnh
   `specify extension bundle`** — `specify bundle build` là của hệ **bundle** (`bundle.yml`, schema
   riêng, `src/specify_cli/bundler/`), đừng nhầm với extension/preset. `--from` KHÔNG verify sha256
   (chỉ catalog mới có). → `build-zip.sh` + Release asset của repo này là hợp lệ; đây là lựa chọn
   chủ đích của maintainer.
8. **`replaces:` trong preset first-party (`presets/lean`) chỉ là metadata mô tả** — resolution key
   theo `name`; `strategy` mặc định `replace`.
9. **Manifest không phải closed schema**: field lạ/miệng vực (typo) được nuốt im lặng ở cả
   extension.yml lẫn preset.yml. `schema_version` là equality check cứng `== "1.0"`.
10. **CHANGELOG gần đây đáng chú ý với tác giả addon**: 0.12.0 — agent-context extension thành opt-in;
    0.11.7 — sha256 verify cho catalog install; 0.11.9 — core template chuyển sang "MUST actually
    invoke hook" (đã phản ánh đúng trong vá hook của preset); chuỗi 0.12.x — hardening bundler/catalog.

## 3. Findings & trạng thái xử lý (đợt fix 2026-07-11)

Severity: **MAJOR** = gãy/lệch âm thầm hoặc gây nhầm vận hành; **MINOR** = nhiễu/không nhất quán.

| # | Sev | Finding | Trạng thái |
|---|-----|---------|-----------|
| 1 | MAJOR | Version regression: manifest `0.0.1` trong khi tag/release cũ tới `dft-preset-v4.1.0`, `dft-speckit-v1.11.0` | **Chốt chính sách**: maintainer chủ ý reset baseline `0.0.1`. Đã xoá toàn bộ tag cũ (local + remote `dft-speckit-v1.11.0`); chỉ còn 2 tag `*-v0.0.1` khớp 2 release hiện hành. Từ nay version tăng đơn điệu từ 0.0.1 |
| 2 | MAJOR | Docs release sai thực tế: workflows đã tắt trigger push-tag nhưng CLAUDE.md + 2 README vẫn hướng dẫn "push tag → tự release" | **Đã sửa**: chốt chính sách chỉ release thủ công qua `release.sh`; xoá 2 workflow chết; viết lại section release trong CLAUDE.md + 2 README |
| 3 | MAJOR | Snapshot-clobber: override preset bị ghi đè khi nâng cấp spec-kit CLI / re-init (§2.1) mà không có runbook | **Đã sửa**: thêm mục "Sau khi nâng cấp spec-kit" vào README preset + CLAUDE.md |
| 4 | MAJOR | Coupling upstream không có cơ chế phát hiện gãy (neo nguyên văn vào section core, chỉ có floor `>=0.6.0`) | **Đã sửa**: thêm `scripts/check-core-anchors.sh` (2 chế độ: clone spec-kit / project đã cài — chế độ project kiểm ngay trên bản command đã materialize). Đã chạy pass 15/15 neo trên cả 0.12.11 (clone) lẫn **0.12.4 (bản CLI local, cài thật vào project tạm)** |
| 5 | MAJOR | 3/4 file command preset thiếu frontmatter (`description`, `strategy`) — đường legacy đọc strategy từ frontmatter (§2.6); description trống khi materialize skill | **Đã sửa**: thêm frontmatter `description` + `strategy: wrap` cho cả 4 command |
| 6 | MAJOR | Preset `speckit.specify` thiếu giao thức non-interactive (chạy trong autopilot/subagent không có người trả lời → không có đường dừng an toàn) | **Đã sửa**: thêm luật HALT (ghi trạng thái vào file sổ rồi dừng, cấm tự trả lời thay) |
| 7 | MINOR | Residue thời còn là Claude skill trong references của extension: "SKILL.md" (không tồn tại trong bản cài), `<đường-dẫn-skill>`, thuật ngữ "skill" chỉ `qa-spec-cycle`, ví dụ ghi "repo này (ABP + Angular)" gây hiểu nhầm project đích | **Đã sửa**: quét toàn bộ `references/*.md`, đổi về "command", đường dẫn cài thật, "ví dụ một repo ABP + Angular" |
| 8 | MINOR | `extension.yml` `requires.speckit_version: ">=0.1.0"` quá thấp (command dùng AskUserQuestion như preset) | **Đã sửa**: nâng `>=0.6.0` |
| 9 | MINOR | `extension.yml` `repository` ghi `github.com/dft/agent-skills` (sai remote thật `anhnt3/agent-skills`) | **Đã sửa** |
| 10 | MINOR | README extension: cây thư mục thiếu 2 template; README preset: link tương đối `../docs/research/...` gãy khi đóng zip | **Đã sửa**: bổ sung cây; link đổi sang URL GitHub tuyệt đối |
| 11 | MINOR | Manifest khai `license: MIT` nhưng không có file LICENSE; build-zip extension không copy LICENSE | **Đã sửa**: thêm LICENSE cho cả 2 package, build-zip extension copy kèm |
| 12 | MINOR | `release.sh` dùng `sed -i ''` (chỉ chạy macOS) | **Đã sửa**: chuyển sang `perl -pi -e` portable (cả 2 release.sh) |
| 13 | MINOR | `preset.yml` `description` dài như tài liệu (~90 từ) | **Đã sửa**: rút còn 2 câu; chi tiết để README |
| 14 | MINOR | Skill reviewer: cheatsheet cơ chế thiếu các fact §2 (snapshot-clobber, all-occurrences, `.presetignore` không tồn tại, dead-hook typo, skills layout, phân phối chính thức); chưa có bước verify neo với version spec-kit đang cài | **Đã sửa**: cập nhật `speckit-mechanics.md` + checklist; thêm bước verify anchors |

### Findings đã cân nhắc và KHÔNG xử lý (có chủ đích)

- **Không chuyển sang GitHub tag-archive / catalog + sha256**: maintainer chủ ý dùng `release.sh`
  thủ công đẩy zip lên Release. Hợp lệ với installer; ghi nhận trade-off: `--from` không verify sha256.
- **Không bật lại workflow tự động**: cùng lý do — 2 workflow đã xoá thay vì để chết gây nhầm.
- **Không đổi baseline version**: `0.0.1` là chủ đích, giữ.

## 4. Việc còn mở (tùy chọn, chưa làm)

1. **CI smoke test cài đặt** (giá trị cao nhất còn lại): job build zip → `specify init` project tạm →
   `extension add --from localhost` + `preset add --dev` → assert `references/` đủ 9 file,
   `preset resolve` trả đúng đường dẫn, command materialize có nội dung composed (không còn literal
   `{CORE_TEMPLATE}`). CLAUDE.md đã mô tả quy trình tay; tự động hóa là bước tiếp theo tự nhiên.
2. **Đo thực tế interview-fatigue**: `interview-notes.md` của các feature đã chạy trong dự án thật là
   dữ liệu sẵn có — đếm số lượt hỏi/feature để hiệu chỉnh sàn GĐ2/GĐ3 nếu vượt ~15-20 lượt.
3. **Theo dõi upstream theo nhịp release**: chạy `scripts/check-core-anchors.sh` sau mỗi lần nâng
   `specify`; nếu upstream đổi tên section thì sửa neo trong preset trước khi team nâng cấp.
