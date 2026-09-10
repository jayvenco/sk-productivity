<script>
  import { page } from '$app/stores';
  import { getUsername, clearAuth } from '$lib/api';
  import { goto } from '$app/navigation';
  import Calendar from '$lib/components/Calendar.svelte';
  import { getTheme, setTheme } from '$lib/theme';

  const links = [
    { href: '/', label: 'Home', icon: '◇' },
    { href: '/notes', label: 'Notities', icon: '📝' },
    { href: '/tasks', label: 'Taken', icon: '✓' },
    { href: '/kanban', label: 'Kanban', icon: '☰' },
    { href: '/pomodoro', label: 'Timer', icon: '⏱' },
    { href: '/wiki', label: 'Wiki', icon: '📖' },
    { href: '/snippets', label: 'Code', icon: '💻' },
    { href: '/tags', label: 'Tags', icon: '🏷️' },
    { href: '/reports', label: 'Rapport', icon: '📊' },
    { href: '/settings', label: '⚙', icon: '' },
  ];

  const HIDE_KEY = 'skp_hide_nav';
  let collapsed = $state(false);
  let calOpen = $state(true);
  let themeName = $state(getTheme());
  let hovered = $state(false);

  if (typeof localStorage !== 'undefined') {
    collapsed = localStorage.getItem(HIDE_KEY) === 'true';
  }

  function toggleCollapse() {
    collapsed = !collapsed;
    localStorage.setItem(HIDE_KEY, collapsed ? 'true' : 'false');
    document.documentElement.classList.toggle('nav-hidden', collapsed);
  }

  function toggleTheme() {
    const next = themeName === 'apple' ? '' : 'apple';
    themeName = next;
    setTheme(next);
  }

  function logout() {
    if (!confirm('Uitloggen?')) return;
    clearAuth();
    goto('/login');
  }

  function expand() { hovered = true; }
  function collapse() { hovered = false; }
</script>

<aside
  class="sidebar"
  class:collapsed
  class:expanded={hovered}
  onmouseenter={expand}
  onmouseleave={collapse}
>
  <div class="sb-inner">
    <div class="sb-links">
      {#each links as link}
        <a
          href={link.href}
          class="sb-item"
          class:active={$page.url.pathname === link.href}
          aria-label={link.label}
          title={link.label}
        >
          <span class="sb-icon">{link.icon}</span>
          <span class="sb-label" class:hidden={collapsed && !hovered}>{link.label}</span>
        </a>
      {/each}
    </div>
    <div class="sb-bottom">
      <button class="sb-item sb-logout" onclick={logout} aria-label="Uitloggen" title={getUsername() || 'admin'}>
        <span class="sb-icon">🚪</span>
        <span class="sb-label" class:hidden={collapsed && !hovered}>{getUsername() || 'admin'}</span>
      </button>
      <div class="sb-actions">
        <button class="sb-collapse-btn" onclick={toggleCollapse} aria-label="Vastzetten" title={collapsed ? 'Uitgeklapt laten' : 'Ingeklapt laten'}>
          📌
        </button>
        <button class="sb-collapse-btn" onclick={toggleTheme} aria-label="Thema" title={themeName === 'apple' ? 'Donker thema' : 'Apple light thema'}>
          {themeName === 'apple' ? '🌑' : '☀️'}
        </button>
      </div>
    </div>
  </div>
  <div class="sb-cal" class:hidden={collapsed && !hovered}>
    <Calendar bind:show={calOpen} />
  </div>
</aside>

<style>
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 200px;
    background: var(--bg-card);
    border-right: 1px solid var(--border);
    z-index: 100;
    display: flex;
    flex-direction: column;
    transition: width 0.2s ease;
    overflow: hidden;
  }

  .sidebar.collapsed {
    width: 48px;
  }

  .sidebar.collapsed.expanded {
    width: 200px;
    box-shadow: 4px 0 20px rgba(0,0,0,0.3);
  }

  .sb-inner {
    display: flex;
    flex-direction: column;
    flex: 1;
    padding: 8px;
    gap: 4px;
    overflow-y: auto;
  }

  .sb-links { display: flex; flex-direction: column; gap: 2px; flex: 1; }

  .sb-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    border-radius: var(--radius);
    color: var(--text-muted);
    text-decoration: none;
    font-size: 13px;
    transition: all 0.15s;
    white-space: nowrap;
    background: none;
    border: none;
    cursor: pointer;
    font-family: inherit;
    width: 100%;
    text-align: left;
  }

  .sb-item:hover { background: var(--bg-hover); color: var(--text); }
  .sb-item.active { color: var(--accent); background: var(--bg-hover); }
  .sb-icon { font-size: 18px; width: 24px; text-align: center; flex-shrink: 0; }

  .sb-label {
    font-size: 13px; font-weight: 500;
    overflow: hidden; text-overflow: ellipsis;
    transition: opacity 0.15s;
  }
  .sb-label.hidden { opacity: 0; width: 0; margin: 0; overflow: hidden; display: inline-block; }

  .sb-bottom { display: flex; flex-direction: column; gap: 2px; padding-top: 8px; border-top: 1px solid var(--border); }
  .sb-logout { opacity: 0.6; }
  .sb-logout:hover { opacity: 1; }

  .sb-actions { display: flex; gap: 2px; }
  .sb-collapse-btn {
    display: flex; align-items: center; justify-content: center;
    padding: 6px; border-radius: var(--radius); color: var(--text-muted);
    background: none; border: none; cursor: pointer; font-size: 12px; font-family: inherit; flex: 1;
  }
  .sb-collapse-btn:hover { background: var(--bg-hover); color: var(--text); }

  .sb-cal { padding: 8px; border-top: 1px solid var(--border); }
  .sb-cal.hidden { display: none; }
  .sidebar.collapsed:not(.expanded) .sb-cal { display: none; }
</style>