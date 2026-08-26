<script>
  import { onMount, onDestroy } from 'svelte';
  import { api } from '$lib/api';

  let { itemType = null, itemId = null, onStart = null, onStop = null } = $props();
  let status = $state({ active: false, session: null });
  let timer = $state('00:00');
  let interval = null;
  let loading = $state(true);

  onMount(async () => {
    try {
      status = await api.pomodoro.status();
      if (status.active) startTimer(status.session);
    } catch (e) { /* silent */ }
    finally { loading = false; }
  });

  onDestroy(() => { if (interval) clearInterval(interval); });

  function startTimer(session) {
    const start = new Date(session.started_at).getTime();
    const duration = session.duration_minutes * 60 * 1000;
    if (interval) clearInterval(interval);
    interval = setInterval(() => {
      const now = Date.now();
      const remaining = Math.max(0, duration - (now - start));
      const mins = Math.floor(remaining / 60000);
      const secs = Math.floor((remaining % 60000) / 1000);
      timer = `${String(mins).padStart(2,'0')}:${String(secs).padStart(2,'0')}`;
      if (remaining <= 0) { clearInterval(interval); timer = '00:00'; }
    }, 1000);
  }

  async function start() {
    const data = { session_type: 'focus', duration_minutes: 25 };
    if (itemType && itemId) { data.item_type = itemType; data.item_id = itemId; }
    status = await api.pomodoro.start(data);
    startTimer(status);
    if (onStart) onStart(status);
  }

  async function stop() {
    clearInterval(interval);
    status = await api.pomodoro.stop();
    timer = '00:00';
    if (onStop) onStop(status);
  }

  // Expose for parent
  defineExpose?.({ start, stop, status, timer });
</script>

{#if !loading}
  <div class="pomo-timer" class:active={status.active} aria-live="polite" aria-label={status.active ? `Timer: ${timer}` : 'Pomodoro'}>
    <span class="pomo-icon">⏱</span>
    <span class="pomo-time">{timer}</span>
    {#if status.active}
      <button class="pomo-btn stop" onclick={stop} title="Stop">■</button>
    {:else}
      <button class="pomo-btn start" onclick={start} title="Start (25 min)">▶</button>
    {/if}
  </div>
{/if}

<style>
  .pomo-timer {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 10px;
    border-radius: var(--radius);
    background: var(--bg-hover);
    font-size: 13px;
    transition: all 0.2s;
  }
  .pomo-timer.active {
    background: #1a3a1a;
    border: 1px solid var(--green);
  }
  .pomo-icon { font-size: 14px; }
  .pomo-time {
    font-variant-numeric: tabular-nums;
    font-weight: 600;
    font-size: 14px;
    min-width: 40px;
    color: var(--accent);
  }
  .pomo-timer.active .pomo-time { color: var(--green); }
  .pomo-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 12px;
    padding: 2px 6px;
    border-radius: 4px;
  }
  .pomo-btn.start { color: var(--green); }
  .pomo-btn.stop { color: var(--red); }
  .pomo-btn:hover { opacity: 0.8; }
</style>