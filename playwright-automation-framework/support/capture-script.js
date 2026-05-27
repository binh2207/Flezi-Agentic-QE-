(() => {
  const BUDGET = 50; // max elements per screen map

  const stabilityRank = (el) => {
    if (el.dataset.testid || el.dataset.qa || el.dataset.cy) return 0;
    if (el.getAttribute('aria-label') || el.getAttribute('role')) return 1;
    if (el.id) return 2;
    return 3;
  };

  const STABILITY_LABEL = ['data-attribute', 'aria', 'id', 'css'];

  const bestSelector = (el) => {
    if (el.dataset.testid) return `[data-testid="${el.dataset.testid}"]`;
    if (el.dataset.qa)     return `[data-qa="${el.dataset.qa}"]`;
    if (el.dataset.cy)     return `[data-cy="${el.dataset.cy}"]`;
    if (el.id)             return `#${el.id}`;
    const name = el.getAttribute('name');
    if (name) return `${el.tagName.toLowerCase()}[name="${name}"]`;
    const aria = el.getAttribute('aria-label');
    if (aria) return `[aria-label="${aria}"]`;
    return null;
  };

  const labelFor = (el) => {
    if (el.id) {
      const lbl = document.querySelector(`label[for="${el.id}"]`);
      if (lbl) return lbl.textContent.trim() || null;
    }
    return (
      el.closest('label')?.textContent.trim() ||
      el.getAttribute('aria-label') ||
      el.getAttribute('placeholder') ||
      null
    );
  };

  // Strict visibility: must have non-zero bounding rect AND be in layout flow
  const isVisible = (el) => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && el.offsetParent !== null;
  };

  const seen = new Set();
  const candidates = [];

  document
    .querySelectorAll(
      'input:not([type="hidden"]), button, select, textarea, ' +
      'a[href], [data-testid], [data-qa], [role="button"], [role="link"]'
    )
    .forEach((el) => {
      if (!isVisible(el)) return;
      const sel = bestSelector(el);
      if (!sel || seen.has(sel)) return;
      seen.add(sel);

      const rank = stabilityRank(el);
      const raw = (el.dataset.testid || el.getAttribute('name') || el.id || el.textContent || '')
        .trim().slice(0, 40).replace(/\s+/g, '_').toLowerCase();

      const entry = {
        intent:    raw || 'unknown',
        selector:  sel,
        tag:       el.tagName.toLowerCase(),
        stability: STABILITY_LABEL[rank],
        _rank:     rank,
      };

      // Only include optional fields when they carry information
      const type = el.getAttribute('type');
      if (type && type !== entry.tag) entry.type = type;

      const lbl = labelFor(el);
      if (lbl) entry.label = lbl.slice(0, 60);

      const txt = el.textContent?.trim().slice(0, 40);
      if (txt && txt !== entry.label) entry.text = txt;

      const ph = el.getAttribute('placeholder');
      if (ph) entry.placeholder = ph.slice(0, 60);

      candidates.push(entry);
    });

  // Stable selectors first; within same rank keep DOM order (stable sort via index)
  candidates.sort((a, b) => a._rank - b._rank);
  const elements = candidates.slice(0, BUDGET).map(({ _rank, ...rest }) => rest);

  // Lightweight dom_fingerprint: djb2 hash of sorted selectors string
  const fp = elements.map((e) => e.selector).sort().join('|');
  let h = 5381;
  for (let i = 0; i < fp.length; i++) h = (((h << 5) + h) ^ fp.charCodeAt(i)) >>> 0;
  const dom_fingerprint = h.toString(16).padStart(8, '0');

  const result = {
    page:            document.title || '',
    url:             window.location.href,
    route:           window.location.pathname,
    dom_fingerprint,
    captured_at:     new Date().toISOString(),
    element_count:   elements.length,
    elements,
  };

  const buildId = document.querySelector('meta[name="app-build-id"]')?.getAttribute('content');
  if (buildId) result.build_id = buildId;

  return JSON.stringify(result, null, 2);
})();
