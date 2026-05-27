# support/components/

Project-specific component helpers. Each file handles one custom UI component type.

Core files (`helpers.ts`, `capture-script.js`) are never modified — all project extensions go here.

## Convention

| File | Component |
|---|---|
| `date-picker.ts` | Date/time picker widgets |
| `rich-editor.ts` | Rich text editors (Quill, TipTap, Slate) |
| `file-upload.ts` | File upload inputs (hidden or visible) |
| `multi-select.ts` | Multi-select dropdowns (react-select etc.) |
| `toast.ts` | Toast / snackbar / notification assertions |

## Usage in page objects

```typescript
import { selectDate } from '../support/components/date-picker';

export class CheckoutPage extends ProjectBasePage {
  async fillDeliveryDate(date: string) {
    await selectDate(this.page, '[data-testid="delivery-date"]', date);
  }
}
```

## Adding a new component

1. Create `support/components/<component-name>.ts`
2. Document it in `inputs/project-config/custom-components.md`
3. Import and use in the relevant page object
