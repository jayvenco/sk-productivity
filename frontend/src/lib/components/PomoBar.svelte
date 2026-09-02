<script>
  import { onMount, onDestroy } from 'svelte';
  import { api } from '$lib/api';
  import { goto } from '$app/navigation';

  let sessions = $state([]);
  let interval = null;

  onMount(async () => {
    await load();
    interval = setInterval(load, 5000);
  });

  onDestroy(() => { if (interval) clearInterval(interval); });

  async function load() {
    try {
      const res = await api.pomodoro.status();
      sessions = (res.sessions || []).filter(s => s.status === 'running' || s.status === 'paused');
    } catch {}
  }

  function timerStr(s) {
    const now = Date.now();
    const start = new Date(s.started_at).getTime();
    const elapsed = s.status === 'paused' ? (s.elapsed_seconds || 0) * 1000 : (now - start);
    const remaining = Math.max(0, s.duration_minutes * 60 * 1000 - elapsed);
    const mins = Math.floor(remaining / 60000);
    const secs = Math.floor((remaining % 60000) / 1000);
    return `${String(mins).padStart(2,'0')}:${String(secs).padStart(2,'0')}`;
  }

  function progress(s) {
    const now = Date.now();
    const start = new Date(s.started_at).getTime();
    const elapsed = s.status === 'paused' ? (s.elapsed_seconds || 0) * 1000 : (now - start);
    const total = s.duration_minutes * 60 * 1000;
    return Math.min(100, Math.max(0, (elapsed / total) * 100));
  }

  async function pause(s) {
    const now = Date.now();
    const start = new Date(s.started_at).getTime();
    const elapsed = Math.round((now - start) / 1000);
    try { await api.pomodoro.pause(s.id, elapsed); await load(); }
    catch {}
  }

  async function resume(s) {
    try { await api.pomodoro.resume(s.id); await load(); }
    catch {}
  }

  async function stop(s) {
    const now = Date.now();
    const start = new Date(s.started_at).getTime();
    const elapsed = Math.round((now - start) / 1000);
    try { await api.pomodoro.stop(s.id, elapsed); await load(); }
    catch {}
  }
</script>

{#if sessions.length > 0}
  <div class="pomo-bar">
    <div class="pb-inner">
      {#each sessions as s (s.id)}
        <div class="pb-item" class:paused={s.status === 'paused'}>
          <div class="pb-progress" style="width: {progress(s)}%;"></div>
          <div class="pb-content">
            <span class="pb-icon">{s.status === 'running' ? '⏳' : '⏸'}</span>
            <span class="pb-type">{s.session_type}</span>
            <span class="pb-time">{timerStr(s)}</span>
            <span class="pb-dur">{s.duration_minutes}min</span>
            <div class="pb-actions">
              {#if s.status === 'running'}
                <button class="pb-btn" onclick={() => pause(s)} title="Pauze">⏸</button>
              {:else}
                <button class="pb-btn" onclick={() => resume(s)} title="Hervat">▶</button>
              {/if}
              <button class="pb-btn pb-stop" onclick={() => stop(s)} title="Stop">⏹</button>
            </div>
          </div>
        </div>
      {/each}
      <button class="pb-goto" onclick={() => goto('/pomodoro')} title="Naar Pomodoro">📊</button>
    </div>
  </div>
{/if}

<style>
  .pomo-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 200;
    background: var(--bg-card);
    border-top: 1px solid var(--border);
    box-shadow: 0 -2px 12px rgba(0,0,0,0.2);
  }

  .pb-inner {
    display: flex;
    gap: 8px;
    padding: 6px 16px;
    align-items: center;
    overflow-x: auto;
  }

  .pb-item {
    position: relative;
    display: flex;
    align-items: center;
    min-width: 200px;
    background: var(--bg-hover);
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid var(--border);
  }

  .pb-item.paused {
    opacity: 0.7;
  }

  .pb-progress {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    background: rgba(239, 131, 84, 0.15);
    transition: width 1s linear;
    pointer-events: none;
  }

  .pb-content {
    position: relative;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    width: 100%;
    z-index: 1;
  }

  .pb-icon { font-size: 14px; }
  .pb-type { font-size: 11px; font-weight: 600; color: var(--text); text-transform: capitalize; }
  .pb-time { font-size: 13px; font-weight: 700; color: var(--accent); font-variant-numeric: tabular-nums; }
  .pb-dur { font-size: 10px; color: var(--text-muted); }
  .pb-actions { display: flex; gap: 2px; margin-left: auto; }
  .pb-btn {
    background: none; border: none; cursor: pointer; font-size: 12px;
    padding: 2px 4px; border-radius: 3px; color: var(--text-muted); line-height: 1;
  }
  .pb-btn:hover { background: var(--bg-card); color: var(--text); }
  .pb-stop:hover { color: var(--red); }
  .pb-goto {
    background: none; border: none; cursor: pointer; font-size: 16px;
    padding: 4px 6px; border-radius: 4px; color: var(--text-muted); margin-left: auto; flex-shrink: 0;
  }
  .pb-goto:hover { background: var(--bg-hover); color: var(--text); }
</style>