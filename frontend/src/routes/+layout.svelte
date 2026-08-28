<script>
  import '../app.css';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import Calendar from '$lib/components/Calendar.svelte';
  import { isAuthenticated, clearAuth } from '$lib/api';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { getTheme, applyTheme, getFont, applyFont } from '$lib/theme';

  let { children } = $props();
  let authed = $state(false);
  let checking = $state(true);
  let calOpen = $state(true);

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
    <div class="cal-container">
      <Calendar bind:show={calOpen} />
    </div>
    <main class="main-content" class:cal-open={calOpen}>
      {@render children()}
    </main>
    <Sidebar />
  </div>
{/if}

<style>
  .app-layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  .cal-container {
    position: fixed;
    top: 12px;
    left: 12px;
    width: 230px;
    z-index: 50;
  }

  .main-content {
    flex: 1;
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
    padding-bottom: 80px;
  }

  .main-content.cal-open {
    padding-left: 260px;
  }

  .main-content.no-sidebar {
    padding-bottom: 20px;
    padding: 0;
    margin: 0;
    max-width: none;
  }

  :global(.nav-hidden) .main-content {
    padding-bottom: 20px;
  }

  .loading-page {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    color: var(--text-muted);
  }

  @media (max-width: 768px) {
    .cal-container { display: none; }
    .main-content.cal-open { padding-left: 20px; }
  }
</style>