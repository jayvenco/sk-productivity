<script>
  import { page } from '$app/stores';
  import { getUsername, clearAuth } from '$lib/api';
  import { goto } from '$app/navigation';

  const links = [
    { href: '/', label: 'Home', icon: '◇' },
    { href: '/notes', label: 'Notities', icon: '📝' },
    { href: '/tasks', label: 'Taken', icon: '✓' },
    { href: '/kanban', label: 'Kanban', icon: '☰' },
    { href: '/pomodoro', label: 'Timer', icon: '⏱' },
    { href: '/wiki', label: 'Wiki', icon: '📖' },
    { href: '/snippets', label: 'Code', icon: '💻' },
    { href: '/stickies', label: 'Stickies', icon: '📌' },
    { href: '/tags', label: 'Tags', icon: '🏷️' },
    { href: '/reports', label: 'Rapport', icon: '📊' },
    { href: '/settings', label: '⚙', icon: '' },
  ];

  const HIDE_KEY = 'skp_hide_nav';

  let hidden = $state(false);
  let expanded = $state(false);

  if (typeof localStorage !== 'undefined') {
    hidden = localStorage.getItem(HIDE_KEY) === 'true';
  }

  function toggleHide() {
    hidden = !hidden;
    localStorage.setItem(HIDE_KEY, hidden ? 'true' : 'false');
    document.documentElement.classList.toggle('nav-hidden', hidden);
  }

  function logout() {
    if (!confirm('Uitloggen?')) return;
    clearAuth();
    goto('/login');
  }
</script>

<nav class="bottombar" class:hidden>
  <div class="bb-inner">
    {#each links as link}
      <a
        href={link.href}
        class="bb-item"
        class:active={$page.url.pathname === link.href}
        aria-label={link.label}
      >
        <span class="bb-icon">{link.icon}</span>
        {#if expanded || window.innerWidth > 768}
          <span class="bb-label">{link.label}</span>
        {/if}
      </a>
    {/each}
    <button class="bb-item bb-logout" onclick={logout} aria-label="Uitloggen" title={getUsername() || 'admin'}>
      <span class="bb-icon">🚪</span>
      {#if expanded || window.innerWidth > 768}
        <span class="bb-label">{getUsername() || 'admin'}</span>
      {/if}
    </button>
  </div>
  <div class="bb-controls">
    <button class="bb-toggle" onclick={() => expanded = !expanded} aria-label="Uitklappen">
      {expanded ? '▼' : '▲'}
    </button>
  </div>
</nav>

<button class="nav-hide-fab" onclick={toggleHide} aria-label="Toon navigatie" title="Toon/verberg navigatie">
  {hidden ? '⬆' : '⬇'}
</button>

<style>
  .bottombar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--bg-card);
    border-top: 1px solid var(--border);
    z-index: 100;
    display: flex;
    flex-direction: column;
    align-items: center;
    transition: transform 0.25s ease;
  }

  .bottombar.hidden {
    transform: translateY(100%);
  }

  .bb-inner {
    display: flex;
    overflow-x: auto;
    gap: 2px;
    padding: 6px 8px;
    width: 100%;
    justify-content: center;
    scrollbar-width: none;
  }

  .bb-inner::-webkit-scrollbar { display: none; }

  .bb-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    padding: 6px 10px;
    border-radius: var(--radius);
    color: var(--text-muted);
    text-decoration: none;
    font-size: 11px;
    transition: all 0.15s;
    white-space: nowrap;
    background: none;
    border: none;
    cursor: pointer;
    font-family: inherit;
    min-width: 0;
  }

  .bb-item:hover {
    background: var(--bg-hover);
    color: var(--text);
  }

  .bb-item.active {
    color: var(--accent);
  }

  .bb-icon { font-size: 18px; line-height: 1; }
  .bb-label { font-size: 10px; font-weight: 500; }

  .bb-logout { opacity: 0.6; }
  .bb-logout:hover { opacity: 1; }

  .bb-controls {
    display: flex;
    position: absolute;
    top: -20px;
    right: 12px;
  }

  .bb-toggle {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-bottom: none;
    border-radius: 8px 8px 0 0;
    color: var(--text-muted);
    font-size: 10px;
    padding: 2px 12px;
    cursor: pointer;
    font-family: inherit;
  }

  .bb-toggle:hover { color: var(--text); }

  .nav-hide-fab {
    position: fixed;
    bottom: 4px;
    right: 12px;
    z-index: 101;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text-muted);
    font-size: 12px;
    padding: 3px 10px;
    cursor: pointer;
    font-family: inherit;
    opacity: 0.5;
    transition: opacity 0.15s;
    line-height: 1.4;
  }

  .bottombar.hidden ~ .nav-hide-fab {
    bottom: 4px;
    opacity: 0.8;
  }

  .nav-hide-fab:hover { opacity: 1; color: var(--text); }
</style>