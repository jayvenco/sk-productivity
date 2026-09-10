<script>
  import { onMount, onDestroy } from 'svelte';
  import { api } from '$lib/api';

  let sessions = $state([]);
  let timer = $state('00:00');
  let interval = null;
  let loading = $state(true);

  onMount(async () => {
    try {
      const data = await api.pomodoro.status();
      sessions = data.sessions || [];
      if (sessions.length > 0) startTimer(sessions[0]);
    } catch (e) { /* silent */ }
    finally { loading = false; }
  });

  onDestroy(() => { if (interval) clearInterval(interval); });

  function startTimer(session) {
    const start = new Date(session.started_at).getTime();
    const elapsed = session.elapsed_seconds || 0;
    const duration = session.duration_minutes * 60 * 1000;
    const adjustedStart = start - (elapsed * 1000);
    if (interval) clearInterval(interval);
    interval = setInterval(() => {
      const now = Date.now();
      const remaining = Math.max(0, duration - (now - adjustedStart));
      const mins = Math.floor(remaining / 60000);
      const secs = Math.floor((remaining % 60000) / 1000);
      timer = `${String(mins).padStart(2,'0')}:${String(secs).padStart(2,'0')}`;
      if (remaining <= 0) { clearInterval(interval); timer = '00:00'; }
    }, 1000);
  }

  async function start() {
    try {
      const s = await api.pomodoro.start({ session_type: 'focus', duration_minutes: 25 });
      sessions = [s, ...sessions];
      startTimer(s);
    } catch (e) { console.error(e); }
  }

  async function stopSession(session) {
    if (interval) clearInterval(interval);
    try {
      const elapsed = session.elapsed_seconds || Math.floor((Date.now() - new Date(session.started_at).getTime()) / 1000);
      await api.pomodoro.stop(session.id, elapsed);
      sessions = sessions.filter(s => s.id !== session.id);
      timer = '00:00';
    } catch (e) { console.error(e); }
  }
</script>

{#if !loading}
  <div class="pomo-section">
    {#each sessions as session (session.id)}
      <div class="pomo-timer active" aria-live="polite" aria-label={timer}>
        <span class="pomo-icon">⏱</span>
        <span class="pomo-time" class:dim={session.id !== sessions[0]?.id}>{timer}</span>
        <button class="pomo-btn stop" onclick={() => stopSession(session)} title="Stop">■</button>
      </div>
    {/each}
    {#if sessions.length === 0}
      <div class="pomo-timer">
        <span class="pomo-icon">⏱</span>
        <span class="pomo-time">00:00</span>
        <button class="pomo-btn start" onclick={start} title="Start (25 min)">▶</button>
      </div>
    {/if}
  </div>
{/if}

<style>
  .pomo-section { display: flex; flex-direction: column; gap: 4px; }
  .pomo-timer {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    border-radius: var(--radius);
    background: var(--bg-hover);
    font-size: 13px;
    transition: all 0.2s;
  }
  .pomo-timer.active { background: #1a3a1a; border: 1px solid var(--green); }
  .pomo-icon { font-size: 14px; }
  .pomo-time {
    font-variant-numeric: tabular-nums;
    font-weight: 600;
    font-size: 14px;
    min-width: 40px;
    color: var(--accent);
  }
  .pomo-time.dim { opacity: 0.6; }
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