// NUI 0.9.3 parses absent storage keys as null. Establish valid defaults before
// its application module loads. Only browser layout keys are involved.
(() => {
  const defaults = {
    'docs-state': {}, 'cards-all': [], 'cards-deck-uuid': [],
    'cards-drawer-uuid': [], 'links-menu-uuid': [], 'logs': [],
  };
  try {
    for (const [key, fallback] of Object.entries(defaults)) {
      let value;
      try { value = JSON.parse(localStorage.getItem(key)); } catch { value = null; }
      const valid = Array.isArray(fallback)
        ? Array.isArray(value)
        : value !== null && typeof value === 'object' && !Array.isArray(value);
      if (!valid) localStorage.setItem(key, JSON.stringify(fallback));
    }
  } catch {
    // Browser storage restrictions are handled by the upstream interface.
  }
})();
