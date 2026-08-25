<script>
  import { onMount, onDestroy } from 'svelte';
  import { api } from '$lib/api';

  let status = $state({ active: false, session: null });
  let timer = $state('00:00');
  let elapsed = $state(0);
  let interval = null;

  onMount(async () => {
    status = await api.pomodoro.status();
    if (status.active) startTimer(status.session);
  });

  onDestroy(() => { if (interval) clearInterval(interval); });

  function startTimer(session) {
    const start = new Date(session.started_at).getTime();
    const duration = session.duration_minutes * 60 * 1000;
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
    status = await api.pomodoro.start({ session_type: 'focus', duration_minutes: 25 });
    startTimer(status);
  }

  async function stop() {
    clearInterval(interval);
    status = await api.pomodoro.stop();
    timer = '00:00';
  }
</script>

<h1>Pomodoro</h1>

<div class="pomodoro-card card">
  <div class="timer">{timer}</div>
  <div class="type">{status.active ? status.session.session_type : 'klaar om te starten'}</div>
  <div class="flex gap-2 justify-center" style="margin-top: 16px;">
    {#if status.active}
      <button class="danger" onclick={stop}>Stop</button>
    {:else}
      <button class="primary" onclick={start}>Start (25 min)</button>
    {/if}
  </div>
</div>

<style>
  .pomodoro-card { text-align: center; padding: 48px; max-width: 400px; margin: 0 auto; }
  .timer { font-size: 72px; font-weight: 700; font-variant-numeric: tabular-nums; color: var(--accent); }
  .type { font-size: 18px; color: var(--text-muted); margin-top: 8px; text-transform: capitalize; }
</style>