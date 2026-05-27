(() => {
  const stability = (el) => {
    if (el.dataset.testid || el.dataset.qa || el.dataset.cy) return 'data-attribute';
    if (el.getAttribute('aria-label') || el.getAttribute('role')) return 'aria';
    if (el.id) return 'id';
    return 'css';
  };

  const bestSelector = (el) => {
    if (el.dataset.testid) return `[data-testid="${el.dataset.testid}"]`;
    if (el.dataset.qa) return `[data-qa="${el.dataset.qa}"]`;
    if (el.dataset.cy) return `[data-cy="${el.dataset.cy}"]`;
    if (el.id) return `#${el.id}`;
    const name = el.getAttribute('name');
    if (name) return `${el.tagName.toLowerCase()}[name="${name}"]`;
    const aria = el.getAttribute('aria-label');
    if (aria) return `[aria-label="${aria}"]`;
    return null;
  };

  const labelFor = (el) => {
    if (el.id) {
      const lbl = document.querySelector(`label[for="${el.id}"]`);
      if (lbl) return lbl.textContent.trim();
    }
    const parent = el.closest('label');
    if (parent) return parent.textContent.trim();
    return el.getAttribute('aria-label') || el.getAttribute('placeholder') || null;
  };

  const seen = new Set();
  const elements = [];

  document
    .querySelectorAll(
      'input, button, select, textarea, a[href], [data-testid], [data-qa], [role="button"], [role="link"]',
    )
    .forEach((el) => {
      const sel = bestSelector(el);
      if (!sel || seen.has(sel)) return;
      seen.add(sel);
      const raw = (el.dataset.testid || el.getAttribute('name') || el.id || el.textContent || '')
        .trim()
        .slice(0, 40)
        .replace(/\s+/g, '_')
        .toLowerCase();
      elements.push({
        intent: raw || 'unknown',
        selector: sel,
        tag: el.tagName.toLowerCase(),
        type: el.getAttribute('type') || el.tagName.toLowerCase(),
        label: labelFor(el),
        text: el.textContent?.trim().slice(0, 80) || null,
        placeholder: el.getAttribute('placeholder') || null,
        visible: el.offsetParent !== null,
        stability: stability(el),
      });
    });

  return JSON.stringify(
    {
      page: document.title || '',
      url: window.location.href,
      route: window.location.pathname,
      build_id:
        document.querySelector('meta[name="app-build-id"]')?.getAttribute('content') || null,
      captured_at: new Date().toISOString(),
      element_count: elements.length,
      elements,
    },
    null,
    2,
  );
})()
