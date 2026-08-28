<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let data = $state(null);
  let days = $state(90);
  let loading = $state(true);
  let error = $state('');

  onMount(async () => { await load(); });

  async function load() {
    error = '';
    loading = true;
    try {
      data = await api.reports.dashboard(days);
    } catch (e) { error = e.message; }
    finally { loading = false; }
  }

  const moduleIcons = { notes: '📝', tasks: '✓', kanban: '☰', wiki: '📖', snippets: '💻' };
  const moduleColors = { notes: '#6b7a8f', tasks: '#ef8354', kanban: '#3b82f6', wiki: '#22c55e', snippets: '#a78bfa' };

  function maxVal(arr, key) {
    return Math.max(...arr.map(i => i[key] || 0), 1);
  }

  function barHeight(val, max) {
    return Math.max(4, (val / max) * 120);
  }
</script>

<div class="header">
  <h1>📊 Rapportage</h1>
  <select bind:value={days} onchange={load} aria-label="Periode" class="period-select">
    <option value={7}>7 dagen</option>
    <option value={30}>30 dagen</option>
    <option value={90}>90 dagen</option>
    <option value={365}>1 jaar</option>
  </select>
</div>

{#if error}
  <div class="error-msg" role="alert">{error}</div>
{/if}

{#if loading}
  <p class="muted">Laden...</p>
{:else if data}
  <!-- ── Summary Cards ── -->
  <div class="summary-row">
    <div class="card summary-card">
      <span class="s-num">{data.total_items}</span>
      <span class="s-lbl">Totaal items</span>
    </div>
    <div class="card summary-card">
      <span class="s-num">{data.total_completed}</span>
      <span class="s-lbl">Afgerond</span>
    </div>
    <div class="card summary-card">
      <span class="s-num">{data.avg_completion_rate}%</span>
      <span class="s-lbl">Voltooiingsgraad</span>
    </div>
  </div>

  <!-- ── Per Module Grafiek ── -->
  <div class="card section">
    <h2>Items per module</h2>
    <div class="bar-chart">
      {#each data.totals as m}
        <div class="bar-item">
          <span class="bar-icon">{moduleIcons[m.module] || '•'}</span>
          <div class="bar-track">
            <div class="bar-fill" style="width: {m.total > 0 ? Math.max(5, (m.total / maxVal(data.totals, 'total')) * 100) : 0}%; background: {moduleColors[m.module]};" title="{m.total} totaal, {m.completed} afgerond"></div>
          </div>
          <div class="bar-info">
            <span class="bar-name">{m.module}</span>
            <span class="bar-nums">{m.completed}/{m.total}</span>
            {#if m.completion_rate > 0}
              <span class="bar-pct">{m.completion_rate}%</span>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  </div>

  <!-- ── Tags / Categorieën ── -->
  {#if data.by_tag.length > 0}
    <div class="card section">
      <h2>Per categorie (tag)</h2>
      <table class="report-table">
        <thead>
          <tr>
            <th>Tag</th>
            <th>Totaal</th>
            <th>Afgerond</th>
            <th>%</th>
          </tr>
        </thead>
        <tbody>
          {#each data.by_tag as t}
            <tr>
              <td>
                <span class="tag-dot" style="background: {t.tag_color};"></span>
                {t.tag_name}
              </td>
              <td>{t.total}</td>
              <td>{t.completed}</td>
              <td>{t.total > 0 ? Math.round(t.completed / t.total * 100) : 0}%</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {:else}
    <div class="card section">
      <h2>Per categorie (tag)</h2>
      <p class="muted">Nog geen tags gebruikt. Ken tags toe aan items om hier categorieën te zien.</p>
    </div>
  {/if}

  <!-- ── Dagelijkse activiteit ── -->
  {#if data.by_day.length > 0}
    <div class="card section">
      <h2>Activiteit (per dag)</h2>
      <div class="activity-chart">
        <svg width="100%" height="160" viewBox="0 0 {data.by_day.length * 30} 160" preserveAspectRatio="none">
          {#each data.by_day as d, i}
            {@const x = i * 30 + 4}
            {@const maxC = maxVal(data.by_day, 'created')}
            {@const maxP = maxVal(data.by_day, 'completed')}
            {@const hC = barHeight(d.created, maxC)}
            {@const hP = barHeight(d.completed, maxP)}
            <!-- Created bar -->
            <rect x={x} y={155 - hC} width="10" height={hC} fill="var(--accent)" rx="2" opacity="0.8">
              <title>{d.date}: {d.created} aangemaakt</title>
            </rect>
            <!-- Completed bar -->
            <rect x={x + 12} y={155 - hP} width="10" height={hP} fill="var(--green)" rx="2" opacity="0.8">
              <title>{d.date}: {d.completed} afgerond</title>
            </rect>
          {/each}
        </svg>
        <div class="chart-legend">
          <span class="legend-item"><span class="legend-dot" style="background: var(--accent);"></span> Aangemaakt</span>
          <span class="legend-item"><span class="legend-dot" style="background: var(--green);"></span> Afgerond</span>
        </div>
      </div>
    </div>
  {/if}

  <!-- ── Module Tabel ── -->
  <div class="card section">
    <h2>Overzicht per module</h2>
    <table class="report-table">
      <thead>
        <tr>
          <th>Module</th>
          <th>Totaal</th>
          <th>Afgerond</th>
          <th>Voltooiing</th>
        </tr>
      </thead>
      <tbody>
        {#each data.totals as m}
          <tr>
            <td><span class="module-icon">{moduleIcons[m.module] || '•'}</span> {m.module}</td>
            <td>{m.total}</td>
            <td>{m.completed}</td>
            <td>
              {#if m.completion_rate > 0}
                <div class="pct-bar">
                  <div class="pct-fill" style="width: {m.completion_rate}%; background: {moduleColors[m.module]};"></div>
                </div>
                <span class="pct-text">{m.completion_rate}%</span>
              {:else}
                —
              {/if}
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}

<style>
  .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
  .period-select { width: auto; padding: 6px 10px; font-size: 13px; }
  .error-msg { background: #3a1a1a; border: 1px solid var(--red); padding: 12px; border-radius: var(--radius); margin-bottom: 16px; font-size: 14px; }
  .muted { color: var(--text-muted); font-style: italic; }
  .section { margin-bottom: 16px; }
  .section h2 { font-size: 16px; margin-bottom: 12px; }

  /* Summary */
  .summary-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }
  .summary-card { text-align: center; padding: 20px; }
  .s-num { display: block; font-size: 32px; font-weight: 700; color: var(--accent); }
  .s-lbl { display: block; font-size: 12px; color: var(--text-muted); margin-top: 4px; }

  /* Bar chart */
  .bar-chart { display: flex; flex-direction: column; gap: 10px; }
  .bar-item { display: flex; align-items: center; gap: 10px; }
  .bar-icon { font-size: 18px; width: 24px; text-align: center; }
  .bar-track { flex: 1; height: 22px; background: var(--bg-hover); border-radius: 11px; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 11px; transition: width 0.5s; min-width: 8px; }
  .bar-info { display: flex; gap: 8px; align-items: baseline; min-width: 140px; }
  .bar-name { font-size: 13px; font-weight: 500; }
  .bar-nums { font-size: 12px; color: var(--text-muted); }
  .bar-pct { font-size: 12px; color: var(--accent); font-weight: 600; }

  /* Activity chart */
  .activity-chart { margin-top: 8px; }
  .chart-legend { display: flex; gap: 16px; margin-top: 8px; font-size: 12px; color: var(--text-muted); }
  .legend-dot { display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 4px; vertical-align: middle; }

  /* Table */
  .report-table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .report-table th { text-align: left; padding: 8px 10px; border-bottom: 2px solid var(--border); color: var(--text-muted); font-weight: 600; font-size: 12px; }
  .report-table td { padding: 8px 10px; border-bottom: 1px solid var(--border); }
  .report-table tr:last-child td { border-bottom: none; }
  .tag-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; vertical-align: middle; }
  .module-icon { font-size: 14px; margin-right: 4px; }

  /* Percentage bar in table */
  .pct-bar { display: inline-block; width: 60px; height: 8px; background: var(--bg-hover); border-radius: 4px; overflow: hidden; vertical-align: middle; margin-right: 6px; }
  .pct-fill { height: 100%; border-radius: 4px; }
  .pct-text { font-size: 12px; color: var(--text-muted); }
</style>