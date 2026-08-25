<script>
  import '../app.css';
  import Sidebar from '$lib/components/Sidebar.svelte';

  let { children } = $props();
</script>

<div class="app-layout">
  <Sidebar />
  <main class="main-content">
    {@render children()}
  </main>
</div>

<style>
  .app-layout {
    display: flex;
    min-height: 100vh;
  }

  .main-content {
    flex: 1;
    margin-left: var(--sidebar);
    padding: 24px;
    max-width: 1200px;
  }

  @media (max-width: 640px) {
    .main-content {
      margin-left: 0;
      padding: 16px;
      padding-top: 60px;
    }
  }
</style>