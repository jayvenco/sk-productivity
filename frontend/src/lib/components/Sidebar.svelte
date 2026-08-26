<script>
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import PomodoroTimer from './PomodoroTimer.svelte';

  let menuOpen = $state(false);

  const links = [
    { href: '/', label: 'Dashboard', icon: '◇' },
    { href: '/notes', label: 'Notities', icon: '📝' },
    { href: '/tasks', label: 'Taken', icon: '✓' },
    { href: '/kanban', label: 'Kanban', icon: '☰' },
    { href: '/pomodoro', label: 'Pomodoro', icon: '⏱' },
    { href: '/wiki', label: 'Wiki', icon: '📖' },
    { href: '/snippets', label: 'Snippets', icon: '💻' },
    { href: '/reports', label: 'Rapportage', icon: '📊' },
  ];

  function toggleMenu() { menuOpen = !menuOpen; }
  function closeMenu() { menuOpen = false; }

  function handleKeydown(e) {
    if (e.key === 'Escape' && menuOpen) menuOpen = false;
  }

  onMount(() => {
    if (typeof window !== 'undefined') {
      window.addEventListener('keydown', handleKeydown);
      return () => window.removeEventListener('keydown', handleKeydown);
    }
  });
</script>

<button class="hamburger" onclick={toggleMenu} aria-label="Menu" aria-expanded={menuOpen}>
  <span class="hamburger-line"></span>
  <span class="hamburger-line"></span>
  <span class="hamburger-line"></span>
</button>

{#if menuOpen}
  <div class="overlay" onclick={closeMenu} role="presentation"></div>
{/if}

<aside class="sidebar" class:open={menuOpen}>
  <div class="logo">
    <span class="logo-icon">🔧</span>
    <span class="logo-text">SKP</span>
  </div>
  <nav class="nav">
    {#each links as link}
      <a href={link.href} class="nav-link" data-selected={$page.url.pathname === link.href} onclick={closeMenu}>
        <span class="nav-icon">{link.icon}</span>
        <span class="nav-label">{link.label}</span>
      </a>
    {/each}
  </nav>
  <div class="sidebar-footer">
    <PomodoroTimer />
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
    z-index: 20;
    transition: transform 0.25s ease;
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

  .nav { display: flex; flex-direction: column; gap: 4px; flex: 1; }

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

  .nav-link:hover { background: var(--bg-hover); color: var(--text); }
  .nav-link[data-selected="true"] { background: var(--bg-hover); color: var(--accent); font-weight: 500; }

  .nav-icon { font-size: 16px; width: 20px; text-align: center; }

  .sidebar-footer { padding-top: 12px; border-top: 1px solid var(--border); display: flex; flex-direction: column; gap: 8px; }
  .version { font-size: 12px; color: var(--text-muted); }

  .hamburger {
    display: none;
    position: fixed;
    top: 12px;
    left: 12px;
    z-index: 30;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 8px 10px;
    cursor: pointer;
    flex-direction: column;
    gap: 4px;
  }

  .hamburger-line {
    display: block;
    width: 20px;
    height: 2px;
    background: var(--text);
    border-radius: 1px;
    transition: transform 0.2s;
  }

  .overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    z-index: 15;
  }

  @media (max-width: 640px) {
    .sidebar {
      transform: translateX(-100%);
    }
    .sidebar.open {
      transform: translateX(0);
    }
    .hamburger {
      display: flex;
    }
    .overlay {
      display: block;
    }
  }
</style>