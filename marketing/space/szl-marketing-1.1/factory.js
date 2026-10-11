() => {
  const root = document.documentElement;
  const scheme = window.matchMedia('(prefers-color-scheme: dark)');
  let chosen = null;
  try {
    const saved = localStorage.getItem('szl-marketing-surface');
    if (saved === 'light' || saved === 'dark') chosen = saved;
  } catch { /* A blocked storage area does not disable the theme control. */ }
  const apply = (surface) => {
    root.dataset.surface = surface;
    root.classList.toggle('dark', surface === 'dark');
    document.querySelectorAll('gradio-app, .gradio-container').forEach((node) => {
      node.classList.toggle('dark', surface === 'dark');
    });
    const button = document.getElementById('factory-theme-toggle');
    if (button) {
      button.textContent = surface === 'dark' ? 'Light mode' : 'Dark mode';
      button.setAttribute('aria-label', `Switch to ${surface === 'dark' ? 'light' : 'dark'} color theme`);
    }
  };
  const synchronize = () => {
    apply(chosen || (scheme.matches ? 'dark' : 'light'));
    const main = document.getElementById('factory-workspace');
    if (main) {
      main.setAttribute('role', 'main');
      main.setAttribute('tabindex', '-1');
      main.setAttribute('aria-label', 'Governed marketing workspace');
    }
    document.querySelector('#factory-tabs [role="tablist"]')?.setAttribute('aria-label', 'Factory workspaces');
  };
  synchronize();
  document.addEventListener('click', (event) => {
    if (!(event.target instanceof Element)) return;
    if (event.target.closest('#factory-theme-toggle')) {
      chosen = root.dataset.surface === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem('szl-marketing-surface', chosen); } catch { /* Optional preference only. */ }
      apply(chosen);
    }
    if (event.target.closest('.mf-skip')) {
      document.getElementById('factory-workspace')?.focus({ preventScroll: true });
    }
  });
  document.addEventListener('keydown', (event) => {
    if (!(event.target instanceof Element)) return;
    const current = event.target.closest('#factory-tabs [role="tab"]');
    if (!current || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    const tabs = [...document.querySelectorAll('#factory-tabs [role="tab"]')]
      .filter(tab => tab.getAttribute('aria-disabled') !== 'true');
    const index = tabs.indexOf(current);
    if (index < 0 || !tabs.length) return;
    const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1
      : (index + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
    event.preventDefault();
    tabs[next].focus();
    tabs[next].click();
  });
  scheme.addEventListener('change', () => { if (!chosen) synchronize(); });
  // Gradio invokes launch JS after initial render. A bounded observer covers
  // delayed root hydration without leaving a recurring timer or provider read.
  const observer = new MutationObserver(() => {
    if (document.getElementById('factory-theme-toggle')) {
      synchronize();
      observer.disconnect();
    }
  });
  if (!document.getElementById('factory-theme-toggle')) {
    observer.observe(document.body, { childList: true, subtree: true });
    setTimeout(() => observer.disconnect(), 5000);
  }
}
