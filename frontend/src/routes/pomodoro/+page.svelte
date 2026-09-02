<script>
  import { onMount, onDestroy } from 'svelte';
  import { api } from '$lib/api';

  let sessions = $state([]);
  let history = $state([]);
  let loading = $state(true);
  let error = $state('');
  let interval = null;
  let form = $state({ duration: 25, type: 'focus' });

  onMount(async () => {
    await load();
    interval = setInterval(tick, 1000);
  });

  onDestroy(() => { if (interval) clearInterval(interval); });

  async function load() {
    try {
      const [s, h] = await Promise.all([
        api.pomodoro.status().catch(() => ({ sessions: [] })),
        api.pomodoro.history(10).catch(() => ({ sessions: [] })),
      ]);
      sessions = s.sessions || [];
      history = h.sessions || [];
    } catch (e) { error = e.message; }
    finally { loading = false; }
  }

  function tick() {
    // Re-render timers by updating a dummy state
    sessions = [...sessions];
  }

  function timerStr(s) {
    const now = Date.now();
    const start = new Date(s.started_at).getTime();
    const elapsed = s.status === 'paused' ? (s.elapsed_seconds || 0) * 1000 : (now - start);
    const remaining = Math.max(0, s.duration_minutes * 60 * 1000 - elapsed);
    const mins = Math.floor(remaining / 60000);
    const secs = Math.floor((remaining % 60000) / 1000);
    const pct = ((s.duration_minutes * 60 * 1000 - remaining) / (s.duration_minutes * 60 * 1000)) * 100;
    return { display: `${String(mins).padStart(2,'0')}:${String(secs).padStart(2,'0')}`, pct, remaining };
  }

  async function start() {
    error = '';
    try {
      await api.pomodoro.start({ session_type: form.type, duration_minutes: form.duration });
      await load();
    } catch (e) { error = e.message; }
  }

  async function pause(s) {
    const t = timerStr(s);
    const elapsed = Math.round((s.duration_minutes * 60 * 1000 - t.remaining) / 1000);
    try { await api.pomodoro.pause(s.id, elapsed); await load(); }
    catch (e) { error = e.message; }
  }

  async function resume(s) {
    try { await api.pomodoro.resume(s.id); await load(); }
    catch (e) { error = e.message; }
  }

  async function stop(s) {
    const t = timerStr(s);
    const elapsed = Math.round((s.duration_minutes * 60 * 1000 - t.remaining) / 1000);
    try { await api.pomodoro.stop(s.id, elapsed); await load(); }
    catch (e) { error = e.message; }
  }

  async function deleteSession(id) {
    if (!confirm('Verwijder deze sessie?')) return;
    try { await api.pomodoro.delete(id); await load(); }
    catch (e) { error = e.message; }
  }

  function elapsedStr(s) {
    const mins = Math.floor(s.elapsed_seconds / 60);
    const secs = s.elapsed_seconds % 60;
    return `${mins}:${String(secs).padStart(2,'0')}`;
  }
</script>

<h1>Pomodoro</h1>

{#if error}
  <div class="error-msg" role="alert">{error}</div>
{/if}

{#if loading}
  <p class="muted">Laden...</p>
{:else}
  <!-- Start new -->
  <div class="card start-card">
    <h3>Nieuwe sessie</h3>
    <div class="flex gap-2 items-center" style="flex-wrap: wrap;">
      <select bind:value={form.type} aria-label="Type">
        <option value="focus">Focus</option>
        <option value="break">Pauze</option>
      </select>
      <input type="number" bind:value={form.duration} min="1" max="180" style="width: 80px;" aria-label="Minuten" />
      <span class="muted">min</span>
      <button class="primary" onclick={start}>Start</button>
    </div>
  </div>

  <!-- Active sessions -->
  {#if sessions.length > 0}
    <h2>Actieve sessies ({sessions.length})</h2>
    <div class="pomo-grid">
      {#each sessions as s (s.id)}
        {@const t = timerStr(s)}
        <div class="card pomo-card" class:paused={s.status === 'paused'}>
          <div class="pomo-header">
            <span class="pomo-type">{s.session_type}</span>
            <span class="pomo-status" class:running={s.status === 'running'}>{s.status === 'running' ? '⏳' : '⏸'}</span>
          </div>
          <div class="pomo-ring">
            <svg width="140" height="140" viewBox="0 0 140 140">
              <circle cx="70" cy="70" r="56" fill="none" stroke="var(--bg-hover)" stroke-width="10" />
              <circle cx="70" cy="70" r="56" fill="none" stroke="var(--accent)" stroke-width="10" stroke-linecap="round"
                stroke-dasharray={2 * Math.PI * 56}
                stroke-dashoffset={2 * Math.PI * 56 * (1 - Math.max(0, t.pct) / 100)}
                transform="rotate(-90 70 70)"
                style="transition: stroke-dashoffset 0.5s linear;"
              />
              <text x="70" y="66" text-anchor="middle" dominant-baseline="middle" class="ring-time">{t.display}</text>
              <text x="70" y="86" text-anchor="middle" dominant-baseline="middle" class="ring-pct">{Math.round(t.pct)}%</text>
            </svg>
          </div>
          <div class="pomo-actions">
            {#if s.status === 'running'}
              <button class="secondary small" onclick={() => pause(s)}>⏸ Pauze</button>
              <button class="danger small" onclick={() => stop(s)}>⏹ Stop</button>
            {:else if s.status === 'paused'}
              <button class="primary small" onclick={() => resume(s)}>▶ Hervat</button>
              <button class="danger small" onclick={() => stop(s)}>⏹ Stop</button>
            {/if}
            <button class="secondary small" onclick={() => deleteSession(s.id)} title="Verwijder">✕</button>
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <p class="muted">Geen actieve sessies. Start er een!</p>
  {/if}

  <!-- History -->
  {#if history.length > 0}
    <h2>Geschiedenis</h2>
    <div class="history-list">
      {#each history as s (s.id)}
        <div class="card history-item">
          <div class="flex justify-between items-center">
            <div>
              <span class="pomo-type">{s.session_type}</span>
              <span class="history-duration">{s.duration_minutes} min</span>
              <span class="history-elapsed">{elapsedStr(s)}</span>
            </div>
            <div class="flex gap-2 items-center">
              <span class="history-date">{new Date(s.started_at).toLocaleDateString('nl-NL', {day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'})}</span>
              <button class="secondary small" onclick={() => deleteSession(s.id)} title="Verwijder">✕</button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
{/if}

<style>
  .error-msg { background: #3a1a1a; border: 1px solid var(--red); padding: 12px; border-radius: var(--radius); margin-bottom: 16px; font-size: 14px; }
  .muted { color: var(--text-muted); font-style: italic; }
  .start-card { margin-bottom: 20px; padding: 16px; }
  .start-card h3 { margin-bottom: 10px; }
  .start-card select, .start-card input { padding: 8px 10px; font-size: 14px; }

  .pomo-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; margin-bottom: 24px; }
  .pomo-card { text-align: center; padding: 16px; display: flex; flex-direction: column; align-items: center; gap: 8px; }
  .pomo-card.paused { opacity: 0.7; }
  .pomo-header { display: flex; justify-content: space-between; width: 100%; align-items: center; }
  .pomo-type { font-size: 13px; font-weight: 600; color: var(--text); text-transform: capitalize; }
  .pomo-status { font-size: 16px; }
  .pomo-ring svg { display: block; }
  :global(.ring-time) { font-size: 22px; font-weight: 700; fill: var(--accent); font-variant-numeric: tabular-nums; }
  :global(.ring-pct) { font-size: 11px; fill: var(--text-muted); }
  .pomo-actions { display: flex; gap: 4px; margin-top: 4px; }

  .history-list { display: flex; flex-direction: column; gap: 4px; }
  .history-item { padding: 10px 14px; }
  .history-duration { font-size: 12px; color: var(--text-muted); margin-left: 8px; }
  .history-elapsed { font-size: 12px; color: var(--accent); margin-left: 4px; font-weight: 600; }
  .history-date { font-size: 11px; color: var(--text-muted); }

  h2 { font-size: 16px; margin-bottom: 10px; margin-top: 8px; }
  button.small { padding: 4px 8px; font-size: 11px; }
</style>