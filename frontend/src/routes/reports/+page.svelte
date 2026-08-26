<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let report = $state({ items: [], total: 0 });
  let days = $state(7);
  let filterType = $state('');
  let loading = $state(true);
  let error = $state('');

  const modules = ['', 'task', 'note', 'kanban', 'wiki', 'snippet'];

  onMount(async () => { await load(); });

  async function load() {
    error = '';
    loading = true;
    try {
      const params = { days };
      if (filterType) params.item_type = filterType;
      report = await api.pomodoro.report(params);
    } catch (e) { error = e.message; }
    finally { loading = false; }
  }

  function typeIcon(t) {
    return { task: '✓', note: '📝', kanban: '☰', wiki: '📖', snippet: '💻' }[t] || '•';
  }
</script>

<div class="header">
  <h1>📊 Rapportage</h1>
</div>

{#if error}
  <div class="error-msg" role="alert">{error}</div>
{/if}

<div class="card filter-bar">
  <div class="flex gap-2 items-center">
    <label>Periode:</label>
    <select bind:value={days} onchange={load} aria-label="Periode">
      <option value={1}>Vandaag</option>
      <option value={7}>Afgelopen 7 dagen</option>
      <option value={14}>Afgelopen 14 dagen</option>
      <option value={30}>Afgelopen 30 dagen</option>
      <option value={90}>Afgelopen 90 dagen</option>
    </select>
    <label>Type:</label>
    <select bind:value={filterType} onchange={load} aria-label="Type">
      <option value="">Alle</option>
      <option value="task">Taken</option>
      <option value="note">Notities</option>
      <option value="kanban">Kanban</option>
      <option value="wiki">Wiki</option>
      <option value="snippet">Snippets</option>
    </select>
  </div>
</div>

{#if loading}
  <p class="muted">Laden...</p>
{:else if report.items.length === 0}
  <p class="muted">Geen rapportage gevonden voor deze periode. Start een pomodoro op een taak om tijd te registreren.</p>
{:else}
  <div class="report-summary card">
    <div class="flex gap-4">
      <div class="stat"><span class="stat-val">{report.total}</span><span class="stat-lbl">Items</span></div>
      <div class="stat"><span class="stat-val">{report.items.reduce((a,i) => a + i.total_sessions, 0)}</span><span class="stat-lbl">Sessies</span></div>
      <div class="stat"><span class="stat-val">{report.items.reduce((a,i) => a + i.total_minutes, 0)}</span><span class="stat-lbl">Minuten</span></div>
    </div>
  </div>

  <div class="items-list">
    {#each report.items as item (item.item_type + item.item_id)}
      <div class="card report-item">
        <div class="flex justify-between items-center">
          <div class="flex items-center gap-2">
            <span class="type-icon">{typeIcon(item.item_type)}</span>
            <span class="item-meta">#{item.item_id} ({item.item_type})</span>
          </div>
          <div class="flex gap-3 stats">
            <span class="sessions">{item.total_sessions}×</span>
            <span class="minutes">{item.total_minutes} min</span>
          </div>
        </div>
        {#if item.last_session}
          <span class="last-date">Laatste: {new Date(item.last_session).toLocaleDateString('nl-NL')}</span>
        {/if}
      </div>
    {/each}
  </div>
{/if}

<style>
  .header { margin-bottom: 16px; }
  .filter-bar { margin-bottom: 16px; padding: 12px 16px; }
  .filter-bar label { font-size: 14px; color: var(--text-muted); }
  .filter-bar select { width: auto; }
  .report-summary { margin-bottom: 16px; text-align: center; }
  .stat { display: flex; flex-direction: column; align-items: center; flex: 1; }
  .stat-val { font-size: 28px; font-weight: 700; color: var(--accent); }
  .stat-lbl { font-size: 12px; color: var(--text-muted); }
  .gap-4 { gap: 16px; }
  .items-list { display: flex; flex-direction: column; gap: 6px; }
  .report-item { padding: 12px 16px; }
  .type-icon { font-size: 16px; }
  .item-meta { font-size: 14px; color: var(--text); }
  .stats { font-variant-numeric: tabular-nums; }
  .sessions { font-size: 14px; color: var(--text-muted); }
  .minutes { font-size: 16px; font-weight: 600; color: var(--accent); }
  .last-date { font-size: 11px; color: var(--text-muted); margin-top: 4px; display: block; }
  .error-msg { background: #3a1a1a; border: 1px solid var(--red); padding: 12px; border-radius: var(--radius); margin-bottom: 16px; font-size: 14px; }
  .muted { color: var(--text-muted); font-style: italic; }
</style>