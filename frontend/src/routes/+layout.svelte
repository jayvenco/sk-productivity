<script>
  import '../app.css';
  import Sidebar from '$lib/components/Sidebar.svelte';
  import { isAuthenticated, clearAuth } from '$lib/api';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { getTheme, applyTheme } from '$lib/theme';

  let { children } = $props();
  let authed = $state(false);
  let checking = $state(true);

  onMount(() => {
    authed = isAuthenticated();
    checking = false;
    applyTheme(getTheme());
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
    margin-left: var(--sidebar);
    padding: 20px;
    max-width: 1200px;
  }

  .main-content.no-sidebar {
    margin-left: 0;
  }

  .loading-page {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    color: var(--text-muted);
  }

  @media (max-width: 640px) {
    .main-content {
      margin-left: 0;
      padding: 12px;
      padding-top: 56px;
    }
  }
</style>