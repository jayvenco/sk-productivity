<script>
  import { api, setAuth } from '$lib/api';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { getTheme, applyTheme, getFont, applyFont } from '$lib/theme';

  let username = $state('');
  let password = $state('');
  let error = $state('');
  let loading = $state(false);

  onMount(() => {
    applyTheme(getTheme());
    applyFont(getFont());
  });

  async function login() {
    error = '';
    if (!username || !password) { error = 'Vul alle velden in'; return; }
    loading = true;
    try {
      const res = await api.auth.login({ username, password });
      setAuth(res.token, res.username);
      goto('/');
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Enter') login();
  }
</script>

<div class="login-page">
  <div class="login-card card">
    <div class="logo-area">
      <span class="logo-icon">🔧</span>
      <h1>swissknife-productivity</h1>
    </div>

    {#if error}
      <div class="error-msg" role="alert">{error}</div>
    {/if}

    <div class="flex-col gap-2">
      <input
        bind:value={username}
        placeholder="Gebruikersnaam"
        onkeydown={handleKeydown}
        aria-label="Gebruikersnaam"
        autocomplete="username"
        disabled={loading}
      />
      <input
        type="password"
        bind:value={password}
        placeholder="Wachtwoord"
        onkeydown={handleKeydown}
        aria-label="Wachtwoord"
        autocomplete="current-password"
        disabled={loading}
      />
      <button class="primary" onclick={login} disabled={loading}>
        {loading ? 'Bezig...' : 'Inloggen'}
      </button>
    </div>
  </div>
</div>

<style>
  .login-page {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    width: 100%;
    background: var(--bg);
    padding: 20px;
    box-sizing: border-box;
  }

  .login-card {
    width: 100%;
    max-width: 380px;
    padding: 32px;
  }

  .logo-area {
    text-align: center;
    margin-bottom: 24px;
  }

  .logo-icon { font-size: 48px; display: block; margin-bottom: 8px; }
  .logo-area h1 { font-size: 20px; color: var(--text); }

  .error-msg {
    background: #3a1a1a;
    border: 1px solid var(--red);
    padding: 10px 14px;
    border-radius: var(--radius);
    margin-bottom: 16px;
    font-size: 14px;
    color: #ff8a80;
  }
</style>