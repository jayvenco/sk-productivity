<script>
  import { api, getToken, getUsername, clearAuth, setAuth } from '$lib/api';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  import { themes, getTheme, setTheme } from '$lib/theme';

  let username = $state(getUsername() || 'admin');
  let currentPw = $state('');
  let newPw = $state('');
  let confirmPw = $state('');
  let error = $state('');
  let success = $state('');
  let currentTheme = $state(getTheme());
  let backups = $state([]);
  let backupLoading = $state(false);
  let restoring = $state(null);

  onMount(async () => {
    try {
      await api.auth.verify();
      await loadBackups();
    } catch {
      clearAuth();
      goto('/login');
    }
  });

  async function loadBackups() {
    try {
      backups = await api.backup.list();
    } catch {}
  }

  async function createBackup() {
    backupLoading = true;
    error = '';
    success = '';
    try {
      const res = await api.backup.create();
      success = `Backup gemaakt: ${res.filename} (${(res.size_bytes / 1024).toFixed(1)} KB)`;
      await loadBackups();
    } catch (e) {
      error = e.message;
    } finally {
      backupLoading = false;
    }
  }

  async function restoreBackup(filename) {
    if (!confirm(`Weet je zeker dat je "${filename}" wilt terugzetten?\n\nLet op: de server moet opnieuw opgestart worden!`)) return;
    restoring = filename;
    error = '';
    success = '';
    try {
      const res = await api.backup.restore(filename);
      success = res.message;
    } catch (e) {
      error = e.message;
    } finally {
      restoring = null;
    }
  }

  async function deleteBackup(filename) {
    if (!confirm(`Verwijder backup "${filename}"?`)) return;
    error = '';
    success = '';
    try {
      await api.backup.delete(filename);
      success = `Backup verwijderd`;
      await loadBackups();
    } catch (e) {
      error = e.message;
    }
  }

  function selectTheme(name) {
    currentTheme = name;
    setTheme(name);
    success = 'Thema gewijzigd ✅';
    setTimeout(() => success = '', 2000);
  }

  async function changePassword() {
    error = '';
    success = '';
    if (!currentPw || !newPw) { error = 'Vul alle velden in'; return; }
    if (newPw !== confirmPw) { error = 'Nieuw wachtwoord komt niet overeen'; return; }
    if (newPw.length < 4) { error = 'Wachtwoord moet minimaal 4 tekens zijn'; return; }
    try {
      await api.auth.changePassword({ current_password: currentPw, new_password: newPw });
      success = 'Wachtwoord gewijzigd ✅';
      currentPw = '';
      newPw = '';
      confirmPw = '';
    } catch (e) {
      error = e.message;
    }
  }

  async function changeUsername() {
    error = '';
    success = '';
    if (!username) { error = 'Vul een gebruikersnaam in'; return; }
    try {
      const res = await api.auth.changeUsername({ new_username: username });
      setAuth(getToken(), res.username);
      success = 'Gebruikersnaam gewijzigd ✅';
    } catch (e) {
      error = e.message;
    }
  }

  function logout() {
    if (!confirm('Uitloggen?')) return;
    clearAuth();
    goto('/login');
  }

  const themeList = Object.entries(themes);
</script>

<h1>Instellingen</h1>

{#if error}
  <div class="error-msg" role="alert">{error}</div>
{/if}
{#if success}
  <div class="success-msg">{success}</div>
{/if}

<!-- Theme -->
<div class="card settings-section">
  <h2>Weergave</h2>
  <div class="theme-grid">
    {#each themeList as [key, theme]}
      <button
        class="theme-card"
        class:active={currentTheme === key}
        onclick={() => selectTheme(key)}
        aria-label={theme.name}
      >
        <span class="theme-icon">{theme.icon}</span>
        <span class="theme-name">{theme.name}</span>
        <div class="theme-swatches">
          <span class="swatch" style="background: {theme.colors['--accent']}" title="accent"></span>
          <span class="swatch" style="background: {theme.colors['--bg']}" title="bg"></span>
          <span class="swatch" style="background: {theme.colors['--bg-card']}" title="card"></span>
          <span class="swatch" style="background: {theme.colors['--text']}" title="text"></span>
        </div>
      </button>
    {/each}
  </div>
</div>

<!-- Account -->
<div class="card settings-section">
  <h2>Account</h2>
  <div class="flex-col gap-2">
    <label>
      <span class="label">Gebruikersnaam</span>
      <div class="flex gap-2">
        <input bind:value={username} placeholder="Gebruikersnaam" aria-label="Gebruikersnaam" />
        <button class="secondary" onclick={changeUsername}>Opslaan</button>
      </div>
    </label>
  </div>
</div>

<!-- Password -->
<div class="card settings-section">
  <h2>Wachtwoord wijzigen</h2>
  <div class="flex-col gap-2">
    <input type="password" bind:value={currentPw} placeholder="Huidig wachtwoord" aria-label="Huidig wachtwoord" />
    <input type="password" bind:value={newPw} placeholder="Nieuw wachtwoord" aria-label="Nieuw wachtwoord" />
    <input type="password" bind:value={confirmPw} placeholder="Bevestig nieuw wachtwoord" aria-label="Bevestig" />
    <button class="primary" onclick={changePassword}>Wachtwoord wijzigen</button>
  </div>
</div>

<!-- Backup -->
<div class="card settings-section">
  <h2>Backup</h2>
  <div class="flex gap-2" style="margin-bottom: 12px;">
    <button class="primary" onclick={createBackup} disabled={backupLoading}>
      {backupLoading ? 'Bezig...' : '💾 Backup maken'}
    </button>
  </div>
  {#if backups.length > 0}
    <div class="backup-list">
      {#each backups as b}
        <div class="backup-item">
          <div class="backup-info">
            <span class="backup-name">{b.filename}</span>
            <span class="backup-size">{(b.size_bytes / 1024).toFixed(1)} KB</span>
            <span class="backup-date">{b.created_at}</span>
          </div>
          <div class="flex gap-2">
            <button class="secondary small" onclick={() => restoreBackup(b.filename)} disabled={restoring === b.filename}>
              {restoring === b.filename ? 'Bezig...' : 'Terugzetten'}
            </button>
            <button class="danger small" onclick={() => deleteBackup(b.filename)}>Verwijder</button>
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <p class="muted">Nog geen backups</p>
  {/if}
</div>

<!-- Logout -->
<div class="card settings-section" style="margin-top: 16px;">
  <button class="danger" onclick={logout}>Uitloggen</button>
</div>

<style>
  .settings-section {
    margin-bottom: 16px;
  }
  .settings-section h2 {
    font-size: 18px;
    margin-bottom: 12px;
  }
  .label {
    display: block;
    font-size: 14px;
    color: var(--text-muted);
    margin-bottom: 4px;
  }
  .theme-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 8px;
  }
  .theme-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 12px 8px;
    background: var(--bg-card);
    border: 2px solid var(--border);
    border-radius: var(--radius);
    cursor: pointer;
    transition: all 0.15s;
    color: var(--text);
  }
  .theme-card:hover {
    border-color: var(--accent);
    background: var(--bg-hover);
  }
  .theme-card.active {
    border-color: var(--accent);
    background: var(--bg-hover);
  }
  .theme-icon { font-size: 24px; }
  .theme-name { font-size: 12px; font-weight: 600; }
  .theme-swatches {
    display: flex;
    gap: 3px;
  }
  .swatch {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    border: 1px solid var(--border);
  }
  .error-msg {
    background: #3a1a1a;
    border: 1px solid var(--red);
    padding: 10px 14px;
    border-radius: var(--radius);
    margin-bottom: 16px;
    font-size: 14px;
    color: #ff8a80;
  }
  .success-msg {
    background: #1a3a1a;
    border: 1px solid var(--green);
    padding: 10px 14px;
    border-radius: var(--radius);
    margin-bottom: 16px;
    font-size: 14px;
    color: #81c784;
  }
  .backup-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .backup-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 10px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    gap: 8px;
  }
  .backup-info {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    align-items: baseline;
    flex: 1;
    min-width: 0;
  }
  .backup-name {
    font-size: 13px;
    font-weight: 500;
    word-break: break-all;
  }
  .backup-size {
    font-size: 11px;
    color: var(--text-muted);
    white-space: nowrap;
  }
  .backup-date {
    font-size: 11px;
    color: var(--text-muted);
    white-space: nowrap;
  }
  button.small { padding: 4px 8px; font-size: 12px; }
</style>