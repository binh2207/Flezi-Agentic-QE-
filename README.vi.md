# AIQE — Playwright Harness Engineering

Framework AI hỗ trợ tự động hoá Playwright, **không phụ thuộc vào ứng dụng cụ thể**. QA cung cấp flow thủ công; harness sinh ra POM automation từ bằng chứng DOM thực tế — không bao giờ tự bịa selector.

Tài liệu tiếng Anh: [README.md](README.md)

---

## Kiến trúc tổng quan

```
Coding assistant (Cursor / Claude Code / Copilot)
        │
        ▼
    skills/           ← workflows của agent
        │
        ▼
inputs/               ← flow thủ công & test case do QA viết
        │
        ▼
live-execution        ← mở trình duyệt thật, capture screen map
        │
        ▼
automation-framework  ← sinh POM từ screen map (pages, flows, specs)
        │
        ▼
playwright test       ← chạy kiểm thử
        │  (nếu fail)
        ▼
self-healing          ← AI tự vá locator/wait, tối đa 3 lần
        │  (tuỳ chọn)
        ▼
test-jira-reporter    ← post kết quả lên JIRA
```

| Thư mục | Vai trò |
|---------|---------|
| `skills/` | Workflow canonical cho từng agent |
| `inputs/` | Flow thủ công và test case của bạn |
| `playwright-automation-framework/` | POM, config, tests, screen maps, reports |
| `knowledge_base/` + `kb_server/` | RAG tuỳ chọn — không dùng cho selector |

### Cấu trúc thư mục

```
AIQE Agenting Harness Engineering/
│
├── 📁 inputs/                               ← QA đặt flows & test cases vào đây
│   ├── manual-flows/
│   │   └── example-flow.template.md         ← Template mẫu viết manual flow
│   └── test-cases/                          ← Test cases (rỗng khi mới setup)
│
├── 📁 playwright-automation-framework/      ← Framework Playwright (TypeScript)
│   ├── pages/
│   │   └── base.page.ts                     ← Base Page Object Model
│   ├── tests/
│   │   ├── e2e/
│   │   │   └── harness-placeholder.spec.ts  ← Placeholder (chờ test thật)
│   │   └── smoke/
│   │       └── harness-placeholder.spec.ts  ← Placeholder (chờ test thật)
│   ├── support/
│   │   ├── helpers.ts
│   │   ├── selectors.ts
│   │   ├── test-tags.ts
│   │   ├── capture-script.js                ← Script chụp evidence
│   │   └── screen-maps/                     ← Screen maps sinh ra sau live-execution
│   ├── fixtures/index.ts
│   ├── playwright.config.ts
│   ├── .env / .env.example                  ← BASE_URL, credentials
│   └── reports/                             ← Kết quả test & HTML report
│
├── 📁 skills/                               ← Skills cho coding assistant
│   ├── pipeline-orchestrator/SKILL.md       ← Orchestrator chính (full pipeline)
│   ├── live-execution/SKILL.md              ← Chạy thật & capture screen map
│   ├── automation-framework/SKILL.md        ← Sinh POM & test code từ screen map
│   ├── test-healer/SKILL.md                 ← Self-healing khi selector vỡ
│   ├── test-case-design/SKILL.md
│   ├── test-jira-reporter/SKILL.md
│   └── knowledge-base/SKILL.md
│
├── 📁 knowledge_base/                       ← RAG / Vector DB (ChromaDB)
│   ├── vector/chroma_db/                    ← Vector index
│   └── agent/                               ← KB agent
│
├── 📁 scripts/                              ← Setup & utility scripts
│   ├── setup.sh / setup-assistant.sh/.ps1
│   ├── execution_report_writer.py
│   ├── jira_report_writer.py
│   └── rag_answer.py
│
└── .mcp.json                                ← MCP config (Playwright MCP)
```

---

## Cài đặt một lần

```bash
git clone <repo-này>
cd <repo>
npm run setup:playwright   # cài deps, Chromium, đăng ký MCP Playwright
npm run verify:mcp         # xác nhận @playwright/mcp hoạt động
```

Sau đó set URL ứng dụng:

```env
# playwright-automation-framework/.env
BASE_URL=https://staging.your-app.com
```

Kiểm tra scaffold:

```bash
npm test        # 2 spec placeholder bị skip — bình thường trước khi có feature
npm run typecheck
```

---

## Đăng ký coding assistant

Chạy **một lần** để kết nối harness với assistant bạn đang dùng. Script tự động cài Playwright, cấu hình MCP, và link skills cho đúng assistant.

### Git Bash / WSL / macOS

```bash
# Chọn assistant
npm run setup:claudecode    # Claude Code
npm run setup:cursor        # Cursor
npm run setup:copilot       # GitHub Copilot (VS Code)

# Hoặc setup cả 3 cùng lúc
npm run setup:assistants
```

### Windows PowerShell (native)

```powershell
npm run setup:claudecode:win
npm run setup:cursor:win
npm run setup:copilot:win

# Hoặc cả 3
npm run setup:assistants:win
```

> **Windows:** Script PowerShell cần **Developer Mode** bật (Settings → For Developers → On) để tạo symlink. Nếu không, script tự fallback sang directory junction.

### Việc script làm cho từng assistant

| Assistant | Việc được làm |
|-----------|--------------|
| **Claude Code** | Link `skills/` → `.claude/skills/` + `~/.claude/skills/harness-*` |
| **Cursor** | Link `skills/` → `.cursor/skills/` + `~/.cursor/skills/harness-*` + cấu hình MCP |
| **GitHub Copilot** | Xác nhận `.github/copilot-instructions.md` + tạo `.vscode/settings.json` bật `useInstructionFiles` |

Tất cả lệnh đều chạy **Playwright install + MCP setup** trước, rồi mới setup riêng cho assistant.

### Kiểm tra sau khi đăng ký

- [ ] Claude Code: hỏi *"What harness skills are available?"* → phải liệt kê `pipeline-orchestrator`
- [ ] Cursor: `npm run verify:mcp` pass; restart Cursor để MCP playwright active
- [ ] Copilot: mở Copilot Chat trong VS Code → hỏi *"What is step 1 of pipeline-orchestrator?"*

Hướng dẫn chi tiết: [docs/register-your-assistant.md](docs/register-your-assistant.md)

---

## Dùng Pipeline Orchestrator (khuyên dùng)

Pipeline Orchestrator chạy toàn bộ harness trong **một lệnh duy nhất** — không cần approve từng bước.

### Cách dùng

Gõ vào Claude Code, Cursor, hoặc Copilot Chat:

```
Run pipeline-orchestrator for feature "checkout".
Flow: inputs/manual-flows/checkout.md
BASE_URL is in playwright-automation-framework/.env
```

### Những gì AI tự làm

```
Lệnh của bạn
      |
      v
[1] live-execution     -- mở browser thật, chụp screen maps tại mỗi route/modal
      |
      v
[2] automation-framework -- sinh pages/, flows/, tests/e2e/ từ screen maps
      |
      v
[3] verify             -- chạy npx playwright test, ghi pass/fail
      |
      v (nếu fail)
[4] test-healer        -- tự vá locator/wait, chạy lại (tối đa 3 lần)
      |
      v (tuỳ chọn)
[5] test-jira-reporter -- post kết quả lên JIRA nếu có ticket key
```

### AI chỉ dừng khi gặp blocker cứng

| Tình huống | Hành động |
|---|---|
| CAPTCHA / SMS OTP | Dừng, báo manual-only blocker |
| Login cần credentials thật | Dừng, hỏi bạn |
| Test-healer thất bại sau 3 lần | Dừng, yêu cầu recapture screen map |
| Chưa có screen map cho route chính | Dừng, chạy live-execution trước |

### Kết quả cuối

Sau khi xong, AI xuất báo cáo tóm tắt:

```
Feature:      checkout
Screen map:   support/screen-maps/checkout.screen.json
Automation:   pages/checkout.page.ts, flows/checkout.flow.ts, tests/e2e/checkout.spec.ts
Manifest:     reports/generation-manifest.json
Verification: N passed / M failed
Risks:        (danh sach canh bao RISK hoac "none")
```

> Nếu muốn chạy từng bước riêng lẻ (ví dụ chỉ recapture screen map, hoặc chỉ regenerate code), xem phần **Workflow thủ công** bên dưới.

---

## Workflow thủ công (từng bước)

### Bước 0 — Viết flow thủ công (QA làm, bắt buộc)

```bash
cp inputs/manual-flows/example-flow.template.md inputs/manual-flows/checkout.md
```

Điền vào bảng: **action**, **target** (tên nút/trường), **expected signal** (URL, message, màn hình tiếp theo). Dùng **feature slug** ngắn, khớp với tên file (`checkout` → `checkout.screen.json`, `checkout.spec.ts`).

```markdown
| Step | Action          | Expected signal                              |
|------|-----------------|----------------------------------------------|
| 1    | Navigate        | Trang tải; landmark chính hiển thị            |
| 2    | Accept cookie   | Banner biến mất                              |
| 3    | Click Place order | Redirect /order-confirmation; "Thank you"  |
```

---

### Bước 1 — live-execution (bắt buộc trước khi generate code)

Prompt trong Cursor hoặc Claude Code:

```
Run pipeline-orchestrator for feature "checkout".
Flow: inputs/manual-flows/checkout.md
BASE_URL is in playwright-automation-framework/.env
```

Agent sẽ:
- Mở trình duyệt thật qua MCP Playwright
- Capture **screen map** (DOM snapshot) tại mỗi route/modal mới — **trước khi click**
- Chạy từng step, ghi pass/fail và screenshot khi fail
- Ghi kết quả ra:
  - `playwright-automation-framework/support/screen-maps/checkout.screen.json`
  - `playwright-automation-framework/reports/execution-checkout.csv`
  - `playwright-automation-framework/reports/execution-checkout.md`

> **Gate cứng:** Không được generate code nếu chưa có screen map cho route chính.

---

### Bước 2 — automation-framework (generate POM)

Agent đọc screen map và sinh:

| File được tạo | Mục đích |
|---|---|
| `pages/checkout.page.ts` | Page Object với locators từ screen map |
| `flows/checkout.flow.ts` | Journey function tái sử dụng được |
| `tests/e2e/checkout.spec.ts` | Spec Playwright với tags smoke/regression |
| `support/selectors.ts` | Intent keys cho feature |
| `reports/generation-manifest.json` | Audit trail + cờ RISK |

**Quy tắc không thể phá vỡ:** Mọi selector phải đến từ `getSelector(map, intent)` — không bao giờ inline CSS, không bao giờ tự bịa.

---

### Bước 3 — Verify (chạy Playwright)

```bash
cd playwright-automation-framework
npx playwright test tests/e2e/checkout.spec.ts
npx playwright show-report reports/html
```

Kiểm tra những gì agent tạo ra trước khi tin tưởng:

| Artifact | Cần kiểm tra |
|---|---|
| `screen-maps/checkout.screen.json` | Intent có khớp UI thật? Selector ổn định (`data-testid`, aria)? |
| `pages/checkout.page.ts` | Không có selector hardcode ngoài screen map? |
| `tests/e2e/checkout.spec.ts` | Assertion khớp expected signal trong flow? |
| `reports/generation-manifest.json` | Có cờ `RISK:` nào không? |

---

### Bước 4 — test-healer (nếu test fail)

```
Use test-healer for tests/e2e/checkout.spec.ts.
Use the screen map and Playwright report; do not remove assertions.
```

Agent sẽ:
1. Phân loại lỗi: timeout / selector không tìm thấy / navigation / env
2. Áp dụng **một** thay đổi: cập nhật selector từ screen map, thêm `waitFor({ state: 'visible' })`, thu hẹp scope locator
3. Chạy lại test với scope hẹp
4. Tối đa **3 lần** — nếu vẫn fail, báo blocker, cần recapture screen map

**Không bao giờ được:**
- Xoá assertion
- Dùng `test.skip` để force green
- Bypass CAPTCHA hoặc payment thật

---

### Bước 5 — test-jira-reporter (tuỳ chọn)

```
Use test-jira-reporter for PROJ-123, feature checkout, with latest Playwright output.
```

Agent sẽ post comment wiki-markup lên JIRA và transition status:

| Kết quả | Transition |
|---|---|
| PASS | `In Review` / `QA Passed` / `Done` |
| FAIL | `In Progress` / `QA Failed` |

---

## Tuỳ chọn: Design test case trước khi chạy harness

Nếu chưa có flow rõ ràng, dùng **test-case-design** skill:

```
Design test cases for the checkout feature using BVA and state transition techniques.
Requirements: <mô tả feature hoặc link tài liệu>
```

Output: `inputs/test-cases/test_cases_checkout.md` — dùng file này thay cho `manual-flows/` làm input cho harness.

Các kỹ thuật được hỗ trợ: **BVA**, **Equivalence Partitioning**, **Decision Table**, **State Transition**, **Exploratory**.

---

## Tuỳ chọn: Knowledge Base (RAG)

Dùng KB khi muốn AI hiểu **yêu cầu nghiệp vụ** (what to test), không phải để lấy selector (how to automate).

```bash
npm run setup:kb
export ANTHROPIC_API_KEY=your_key

# Ingest tài liệu
python3 knowledge_base/vector/ingest.py inputs/

# Query
python3 knowledge_base/vector/query.py "payment validation rules" --n 5

# Hoặc chạy REST API
npm run kb:serve   # http://127.0.0.1:8765
```

| Dùng KB | Không dùng KB |
|---|---|
| Requirements, acceptance criteria, domain rules | CSS/XPath selector cho Playwright |
| Thiết kế test case trước automation | Discover live UI (dùng live-execution) |
| "Điều gì nên xảy ra?" khi có tài liệu | Đoán behaviour không có trong docs |

---

## Artifacts sau mỗi feature

| File | Mục đích |
|---|---|
| `support/screen-maps/<feature>.screen.json` | Contract của mọi selector |
| `pages/<feature>.page.ts` | Page Object Model |
| `flows/<feature>.flow.ts` | Journey function tái sử dụng |
| `tests/e2e/<feature>.spec.ts` | Spec chạy được |
| `reports/execution-<feature>.csv` | Evidence từ live run |
| `reports/generation-manifest.json` | Audit trail + cờ RISK |

---

## Commands tham khảo

```bash
# ── Cài đặt ──────────────────────────────────────────────────
npm run setup:playwright         # cài đặt tối thiểu (deps + MCP)
npm run setup                    # harness + KB tuỳ chọn

# ── Đăng ký assistant (chạy một lần) ─────────────────────────
npm run setup:assistants         # Claude Code + Cursor + Copilot (Git Bash)
npm run setup:claudecode         # chỉ Claude Code
npm run setup:cursor             # chỉ Cursor
npm run setup:copilot            # chỉ GitHub Copilot

npm run setup:assistants:win     # tất cả, Windows PowerShell native
npm run setup:claudecode:win     # chỉ Claude Code (PowerShell)
npm run setup:cursor:win         # chỉ Cursor (PowerShell)
npm run setup:copilot:win        # chỉ Copilot (PowerShell)

# ── Test ──────────────────────────────────────────────────────
npm test                         # chạy tất cả projects
npm run test:smoke               # chỉ smoke specs
npm run test:regression          # chỉ e2e specs
npm run typecheck                # kiểm tra TypeScript

# ── KB / RAG (tuỳ chọn) ──────────────────────────────────────
npm run setup:kb                 # cài KB
npm run kb:serve                 # khởi động RAG API (http://127.0.0.1:8765)
```

---

## Troubleshooting

| Vấn đề | Xử lý |
|---|---|
| `BASE_URL is required` | Tạo `.env` từ `.env.example`, set `BASE_URL` |
| Agent tự bịa selector | Yêu cầu live-execution trước; từ chối generate khi chưa có screen map |
| `No screen map entry for intent` | Chạy lại live-execution hoặc đổi tên intent trong map và `selectors.ts` |
| Test pass trên MCP nhưng fail trên Playwright | Chạy self-healing; kiểm tra `BASE_URL`, login, cookies |
| CAPTCHA / SMS OTP / payment thật | Dừng lại; ghi nhận là manual-only blocker |
| Test run rỗng | Chạy pipeline-orchestrator trước; placeholder spec sẽ skip cho đến khi đó |
| Screen map cũ hơn 7 ngày | Recapture (STALE_SOFT); nếu route thay đổi thì bắt buộc (STALE_HARD) |

---

## Quy tắc không thể phá vỡ

1. **Selector chỉ được lấy từ screen map** — không từ RAG, không đoán mò, không hardcode.
2. **Capture screen map trước khi click** trên mỗi route hoặc modal mới.
3. **Không được xoá assertion** để force green test.
4. **Flow và test case** thường được gitignore — lưu trong repo hoặc team repo riêng.
5. Sau khi có spec thật, xoá `harness-placeholder.spec.ts`.

---

## Skill index

| Skill | Khi nào dùng |
|---|---|
| [pipeline-orchestrator](skills/pipeline-orchestrator/SKILL.md) | **Bắt đầu ở đây** — pipeline end-to-end cho một feature |
| [live-execution](skills/live-execution/SKILL.md) | Recapture UI hoặc page/modal mới |
| [automation-framework](skills/automation-framework/SKILL.md) | Regenerate code sau khi cập nhật screen map |
| [test-healer](skills/test-healer/SKILL.md) | Test Playwright bị fail |
| [test-jira-reporter](skills/test-jira-reporter/SKILL.md) | Post kết quả lên JIRA |
| [test-case-design](skills/test-case-design/SKILL.md) | Thiết kế test case markdown trước automation |
| [knowledge-base](skills/knowledge-base/SKILL.md) | Query knowledge base về yêu cầu nghiệp vụ |

Templates cho generated code: [playwright-automation-framework/TEMPLATES.md](playwright-automation-framework/TEMPLATES.md)
