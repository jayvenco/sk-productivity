<script>
  import { page } from '$app/stores';

  const links = [
    { href: '/', label: 'Dashboard', icon: '◇' },
    { href: '/notes', label: 'Notities', icon: '📝' },
    { href: '/tasks', label: 'Taken', icon: '✓' },
    { href: '/kanban', label: 'Kanban', icon: '☰' },
    { href: '/pomodoro', label: 'Pomodoro', icon: '⏱' },
    { href: '/wiki', label: 'Wiki', icon: '📖' },
    { href: '/snippets', label: 'Snippets', icon: '💻' },
  ];
</script>

<aside class="sidebar">
  <div class="logo">
    <span class="logo-icon">🔧</span>
    <span class="logo-text">SKP</span>
  </div>
  <nav class="nav">
    {#each links as link}
      <a href={link.href} class="nav-link" data-selected={$page.url.pathname === link.href}>
        <span class="nav-icon">{link.icon}</span>
        <span class="nav-label">{link.label}</span>
      </a>
    {/each}
  </nav>
  <div class="sidebar-footer">
    <span class="version">v0.1.0</span>
  </div>
</aside>

<style>
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    width: var(--sidebar);
    height: 100vh;
    background: var(--bg-card);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    padding: 16px;
    z-index: 10;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 0 20px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 16px;
  }

  .logo-icon { font-size: 24px; }
  .logo-text { font-size: 18px; font-weight: 700; color: var(--accent); }

  .nav {
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
  }

  .nav-link {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: var(--radius);
    color: var(--text-muted);
    transition: all 0.15s;
    font-size: 14px;
  }

  .nav-link:hover {
    background: var(--bg-hover);
    color: var(--text);
  }

  .nav-link[data-selected="true"] {
    background: var(--bg-hover);
    color: var(--accent);
    font-weight: 500;
  }

  .nav-icon { font-size: 16px; width: 20px; text-align: center; }

  .sidebar-footer {
    padding-top: 16px;
    border-top: 1px solid var(--border);
  }

  .version {
    font-size: 12px;
    color: var(--text-muted);
  }
</style>