# Custom components — <Project Name>

Copy this file to `inputs/project-config/custom-components.md` and fill in the details for your project.
AI reads this file before generating page objects for features that use these components.

---

## How to document a component

For each custom component, provide:
- **Selector** — how to find it in the DOM (prefer data-testid or aria-label)
- **Interaction** — step-by-step action sequence (clicks, waits, keystrokes)
- **Special waits** — any non-standard waiting behaviour
- **Helper** — path to the reusable helper function (if created)

---

## Example: Date Picker

**Library:** react-datepicker / custom  
**Selector:** `[data-testid="date-input"]` or `.date-picker input`  
**Interaction:**
1. Click the input to open calendar
2. Wait for `[class*="calendar"]` to be visible
3. Navigate month if needed (click prev/next arrow)
4. Click the target day cell

**Special waits:** Calendar closes with animation — wait 300ms after selection before next action  
**Helper:** `support/components/date-picker.ts > selectDate(page, selector, dateStr)`

---

## Example: Rich Text Editor (Quill / TipTap / Slate)

**Library:** Quill  
**Selector:** `.ql-editor` or `[data-testid="rich-editor"]`  
**Interaction:**
1. Click editor container to focus
2. Use `page.keyboard.type()` for plain text
3. For formatting: select text then click toolbar button

**Special waits:** Editor initialises async — `waitFor({ state: 'visible' })` on `.ql-editor` before interacting  
**Helper:** `support/components/rich-editor.ts > typeInEditor(page, selector, text)`

---

## Example: File Upload

**Selector:** `input[type="file"]` (may be visually hidden)  
**Interaction:** Use `setInputFiles()` directly — do NOT click the hidden input  
**Special waits:** Wait for upload progress indicator to disappear after upload  
**Helper:** `support/components/file-upload.ts > uploadFile(page, intent, filePath)`

---

## Example: Multi-select Dropdown

**Library:** react-select / custom  
**Selector:** `[data-testid="multi-select"]` or `.react-select__control`  
**Interaction:**
1. Click control to open dropdown
2. Type to filter options
3. Click the option in the dropdown menu
4. Repeat for additional values

**Special waits:** Dropdown list renders async — wait for `[class*="menu"]` to be visible  
**Helper:** `support/components/multi-select.ts > selectOption(page, selector, optionText)`

---

## Example: Toast / Notification

**Selector:** `[role="alert"]` or `[data-testid="toast"]`  
**Interaction:** Observation only — do not click unless dismissing  
**Special waits:** Toast auto-dismisses — assert within 3s of trigger action  
**Helper:** `support/components/toast.ts > waitForToast(page, expectedText)`

---

## Add your project components below

<!-- Replace with your project-specific components -->
