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

## Tuỳ chọn: Knowledge Base (RAG)

KB là lớp RAG cho **yêu cầu nghiệp vụ** — AI hiểu "cần test gì" thay vì tự đoán. Không dùng cho selector (selector luôn từ screen map).

### Kiến trúc 3 lớp

```
docs, requirements, test-cases (.md files)
        |
        v
[1] Vector store (ChromaDB)          -- ingest.py / query.py
        |
        v
[2] KB Agent (agentic RAG)           -- retrieve -> grade -> answer
        |                               knowledge_base/agent/
        v
[3] REST API (kb_server)             -- http://127.0.0.1:8765
                                        dùng cho tích hợp CI hoặc chat UI
```

| Lớp | Dùng khi |
|---|---|
| **Vector store** (CLI) | Query nhanh từ terminal, dùng trong skills |
| **KB Agent** | Cần câu trả lời có reasoning, grading độ tin cậy của chunk |
| **REST API** | Tích hợp CI pipeline hoặc chat UI bên ngoài |

### Cài đặt

```bash
npm run setup:kb
export ANTHROPIC_API_KEY=your_key   # bắt buộc cho KB Agent và REST API
```

### Ingest tài liệu

```bash
# Ingest thư mục inputs/ (user stories, test cases, flow docs)
python3 knowledge_base/vector/ingest.py inputs/

# Ingest toàn bộ project (requirements + skills + flows)
python3 knowledge_base/vector/ingest.py .

# Append thêm tài liệu mà không xoá dữ liệu cũ
python3 knowledge_base/vector/ingest.py inputs/ --no-reset
```

Nguồn tốt để ingest: user stories, Confluence export dạng `.md`, feature specs, BDD scenarios, API docs.

### Retrieve (query)

```bash
# Query CLI — trả về top-5 chunk liên quan nhất
python3 knowledge_base/vector/query.py "checkout payment validation rules" --n 5

# Dùng KB Agent để trả lời có reasoning + citation
python3 scripts/rag_answer.py "What are the acceptance criteria for checkout?"

# REST API
npm run kb:serve   # http://127.0.0.1:8765
curl -X POST http://127.0.0.1:8765/kb/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "payment validation rules"}'
```

Output query cho biết score cosine similarity — chunk có score > 0.5 là liên quan.

### Giới hạn rõ ràng

| Dùng KB | Không dùng KB |
|---|---|
| Requirements, acceptance criteria, BDD scenarios | CSS/XPath selector cho Playwright |
| Domain rules, naming conventions từ docs | Discover live UI layout |
| "App phải làm gì?" khi có tài liệu | Đoán behaviour không có trong docs |

> Nếu KB không có câu trả lời, agent ghi `[KB gap — not documented]` thay vì tự bịa.

---

## Tuỳ chọn: Design test case trước khi chạy harness

**Test-case-design** tự động query KB trước khi thiết kế — đây là điểm leverage chính giữa KB và test design.

### Luồng KB -> Test case -> Harness

```
KB (requirements, acceptance criteria)
        |
        | query tự động (Step 0)
        v
test-case-design     -- sinh test cases từ context KB + kỹ thuật QA
        |
        v
inputs/test-cases/test_cases_<feature>.md
        |
        v
pipeline-orchestrator  -- dùng file này thay cho manual-flows làm input
```

### Cách dùng

```
Design test cases for the checkout feature using BVA and state transition techniques.
Requirements: <mô tả feature hoặc link tài liệu>
```

Agent tự làm:
1. Query KB lấy context (acceptance criteria, domain rules, BDD scenarios)
2. Phân tích requirements + KB context
3. Áp dụng kỹ thuật QA phù hợp
4. Xuất file `inputs/test-cases/test_cases_checkout.md`

### Kỹ thuật được hỗ trợ

| Kỹ thuật | Khi nào dùng |
|---|---|
| **BVA** — Boundary Value Analysis | Input có giới hạn số, ngày, ký tự |
| **EP** — Equivalence Partitioning | Nhóm input có hành vi giống nhau |
| **Decision Table** | Business rules nhiều điều kiện kết hợp |
| **State Transition** | Luồng có trạng thái (Draft → Submitted → Approved) |
| **Exploratory** | Vùng rủi ro, timeout, network chậm |

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

## Token optimization

Harness được tối ưu để giảm lượng token tiêu thụ trong mỗi session AI — giúp chạy nhanh hơn, rẻ hơn, và ít bị cắt context hơn trên các trang phức tạp.

### 1. DOM pruning — screen map chỉ giữ element cần thiết

`playwright-automation-framework/support/capture-script.js`

| Thay đổi | Chi tiết |
|---|---|
| **Visible-only** | Bỏ tất cả element bị ẩn (`display:none`, `visibility:hidden`, zero-size) |
| **Input hidden loại bỏ** | `input[type="hidden"]` không bao giờ được capture |
| **Element budget = 50** | Tối đa 50 element/screen map; ưu tiên `data-testid` → `aria-*` → `id` → css |
| **Null fields bị bỏ** | `label`, `text`, `placeholder`, `type` chỉ xuất hiện khi có giá trị thực |
| **Text truncate 40 chars** | Giảm từ 80 xuống 40 ký tự |
| **`dom_fingerprint` inline** | Hash tính sẵn trong script, không cần bước post-processing |

**Tác động thực tế:** Trang có 200 element DOM → còn ~30–50 element visible interactive → giảm 70–85% kích thước screen map.

---

### 2. Lazy skill loading — chỉ đọc SKILL.md của phase đang chạy

`skills/pipeline-orchestrator/SKILL.md`

Trước đây orchestrator đọc tất cả SKILL.md ngay từ đầu. Bây giờ mỗi SKILL.md chỉ được đọc khi bước đó bắt đầu:

```
Bước 1 bắt đầu  →  đọc live-execution/SKILL.md
Bước 2 bắt đầu  →  đọc automation-framework/SKILL.md
Bước 3 pass     →  SKIP bước 4 (không đọc test-healer/SKILL.md)
Bước 5 không có JIRA key  →  SKIP (không đọc test-jira-reporter/SKILL.md)
```

**Tác động:** Pipeline happy-path (không fail, không JIRA) chỉ đọc 2 SKILL.md thay vì 4–5.

---

### 3. Differential capture — bỏ qua recapture nếu DOM không đổi

`skills/live-execution/SKILL.md`

Trước khi chạy capture script, AI so sánh `dom_fingerprint` hiện tại với map đã lưu:

- Fingerprint khớp + route khớp → **dùng lại map cũ**, không ghi đè
- Fingerprint khác hoặc chưa có map → capture và lưu mới

**Tác động:** Tránh re-embed cùng một DOM nhiều lần trong session (thường xảy ra khi retry hoặc navigate quay lại trang cũ).

---

### 4. Compact error context — test-healer đọc tối thiểu trước

`skills/test-healer/SKILL.md`

| Attempt | Context được đọc |
|---|---|
| Attempt 1 | Chỉ stderr + test title → phân loại lỗi |
| Attempt 2 | Thêm entry element trong screen map của intent bị lỗi |
| Attempt 3 | Mới load trace zip nếu 2 lần trước chưa giải quyết được |

**Tác động:** Tránh load full HTML report + trace zip (~vài MB) ngay từ lần đầu khi thường chỉ cần 2–3 dòng stderr.

---

### 5. Selective template reading — chỉ đọc section cần trong TEMPLATES.md

`skills/automation-framework/SKILL.md`

Thay vì đọc toàn bộ `TEMPLATES.md`, AI chỉ đọc section tương ứng với artifact đang sinh:

| Đang tạo file | Chỉ đọc section |
|---|---|
| `pages/<feature>.page.ts` | `## pages/<feature>.page.ts` |
| `tests/e2e/<feature>.spec.ts` | `## tests/e2e/<feature>.spec.ts` |
| `reports/generation-manifest.json` | `## reports/generation-manifest.json` |

**Tác động:** Không load boilerplate của các artifact khác khi chỉ cần regenerate một file.

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
