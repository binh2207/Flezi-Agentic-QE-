# Auth flow — <Project Name>

Copy to `inputs/project-config/auth-flow.md` and fill in your project's authentication details.
AI reads this before executing any flow that requires a logged-in state.

---

## Auth strategy

<!-- Choose one and fill in details -->

### Option A — Username / password (standard)

**Login URL:** `${BASE_URL}/login`  
**Credentials source:** `playwright-automation-framework/.env` (TEST_USER, TEST_PASS)  
**Success signal:** Redirect to `/dashboard` or presence of `[data-testid="user-menu"]`  
**Session reuse:** storageState saved to `playwright-automation-framework/.auth/session.json`

### Option B — SSO / OAuth (redirect flow)

**Entry point:** `${BASE_URL}/login` → redirects to IdP  
**IdP URL pattern:** `https://sso.example.com/...`  
**Credentials:** Same env vars (TEST_USER, TEST_PASS) entered on IdP form  
**Success signal:** Redirected back to `${BASE_URL}/dashboard`  
**Blocker:** MFA / CAPTCHA on IdP → mark as manual-only blocker

### Option C — API token (Bearer)

**Token source:** `TEST_API_TOKEN` in `.env`  
**Inject via:** `playwright.config.ts` extraHTTPHeaders  
**No browser login needed**

---

## Session reuse (storageState)

To avoid logging in before every test, save and reuse session state:

```typescript
// In playwright.config.ts — globalSetup
// globalSetup: './support/global-setup.ts'
```

```typescript
// support/global-setup.ts
import { chromium } from '@playwright/test';
export default async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(process.env.BASE_URL + '/login');
  await page.fill('[name="email"]', process.env.TEST_USER!);
  await page.fill('[name="password"]', process.env.TEST_PASS!);
  await page.click('[type="submit"]');
  await page.waitForURL('**/dashboard');
  await page.context().storageState({ path: '.auth/session.json' });
  await browser.close();
};
```

---

## Blockers (manual-only — AI must stop)

List any auth steps that cannot be automated:

- [ ] SMS OTP / TOTP (2FA)
- [ ] Email verification link
- [ ] CAPTCHA on login page
- [ ] Hardware security key

When a blocker is hit during live-execution, agent MUST stop and document:
```
BLOCKER: <blocker type> encountered at <URL>. Manual intervention required.
```

---

## Test accounts

| Role | Env var (user) | Env var (pass) | Permissions |
|---|---|---|---|
| Admin | `TEST_ADMIN_USER` | `TEST_ADMIN_PASS` | Full access |
| Standard | `TEST_USER` | `TEST_PASS` | Standard user |
| Read-only | `TEST_READONLY_USER` | `TEST_READONLY_PASS` | View only |

All credentials must be in `.env` — never hardcode in test files.
