<script>
  import '../app.css';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import { isAuthenticated, clearAuth } from '$lib/api';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { getTheme, applyTheme, getFont, applyFont } from '$lib/theme';

  let { children } = $props();
  let authed = $state(false);
  let checking = $state(true);

  onMount(() => {
    authed = isAuthenticated();
    checking = false;
    applyTheme(getTheme());
    applyFont(getFont());
    if (typeof localStorage !== 'undefined' && localStorage.getItem('skp_hide_nav') === 'true') {
      document.documentElement.classList.add('nav-hidden');
    }
    if (!authed && window.location.pathname !== '/login') {
      goto('/login');
    }
  });
</script>

{#if checking}
  <div class="loading-page">
    <p>Laden...</p>
  </div>
{:else if !authed}
  <div class="app-layout">
    <main class="main-content no-sidebar">
      {@render children()}
    </main>
  </div>
{:else}
  <div class="app-layout">
    <Sidebar />
    <main class="main-content">
      {@render children()}
    </main>
  </div>
{/if}

<style>
  .app-layout {
    display: flex;
    min-height: 100vh;
  }

  .main-content {
    flex: 1;
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
    padding-left: 220px;
  }

  .main-content.no-sidebar {
    padding-left: 20px;
    padding-bottom: 20px;
    padding: 0;
    margin: 0;
    max-width: none;
  }

  :global(.nav-hidden) .main-content {
    padding-left: 68px;
  }

  .loading-page {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    color: var(--text-muted);
  }

  @media (max-width: 768px) {
    .main-content {
      padding-left: 20px;
      padding: 12px;
    }
  }
</style>