<script>
  import { onMount, onDestroy } from 'svelte';
  import { api } from '$lib/api';

  let status = $state({ active: false, session: null });
  let timer = $state('00:00');
  let progress = $state(100);
  let elapsed = $state(0);
  let duration = $state(0);
  let interval = null;
  let error = $state('');
  let loading = $state(true);

  onMount(async () => {
    try {
      status = await api.pomodoro.status();
      if (status.active) startTimer(status.session);
    } catch (e) { error = e.message; }
    finally { loading = false; }
  });

  onDestroy(() => { if (interval) clearInterval(interval); });

  function startTimer(session) {
    const start = new Date(session.started_at).getTime();
    duration = session.duration_minutes * 60 * 1000;
    interval = setInterval(() => {
      const now = Date.now();
      const remaining = Math.max(0, duration - (now - start));
      elapsed = duration - remaining;
      progress = (remaining / duration) * 100;
      const mins = Math.floor(remaining / 60000);
      const secs = Math.floor((remaining % 60000) / 1000);
      timer = `${String(mins).padStart(2,'0')}:${String(secs).padStart(2,'0')}`;
      if (remaining <= 0) { clearInterval(interval); timer = '00:00'; progress = 0; }
    }, 200);
  }

  async function start() {
    error = '';
    try {
      status = await api.pomodoro.start({ session_type: 'focus', duration_minutes: 25 });
      startTimer(status);
    } catch (e) { error = e.message; }
  }

  async function stop() {
    error = '';
    try {
      clearInterval(interval);
      status = await api.pomodoro.stop();
      timer = '00:00';
      progress = 100;
    } catch (e) { error = e.message; }
  }

  const SIZE = 200;
  const STROKE = 12;
  const R = (SIZE - STROKE) / 2;
  const CIRC = 2 * Math.PI * R;
</script>

<h1>Pomodoro</h1>

{#if error}
  <div class="error-msg" role="alert">{error}</div>
{/if}

{#if loading}
  <p class="muted center">Laden...</p>
{:else}
  <div class="pomo-card card" aria-live="polite" aria-label={status.active ? `Timer: ${timer}` : 'Pomodoro timer klaar'}>
    <svg width={SIZE} height={SIZE} viewBox="0 0 {SIZE} {SIZE}" class="progress-ring">
      <!-- Background circle -->
      <circle cx={SIZE/2} cy={SIZE/2} r={R} fill="none" stroke="var(--bg-hover)" stroke-width={STROKE} />
      <!-- Progress arc: drains from full to empty -->
      <circle
        cx={SIZE/2} cy={SIZE/2} r={R}
        fill="none"
        stroke="var(--accent)"
        stroke-width={STROKE}
        stroke-linecap="round"
        stroke-dasharray={CIRC}
        stroke-dashoffset={CIRC * (1 - Math.max(0, progress) / 100)}
        transform="rotate(-90 {SIZE/2} {SIZE/2})"
        style="transition: stroke-dashoffset 0.2s linear;"
      />
      <text x={SIZE/2} y={SIZE/2 - 8} text-anchor="middle" dominant-baseline="middle" class="ring-timer">{timer}</text>
      <text x={SIZE/2} y={SIZE/2 + 16} text-anchor="middle" dominant-baseline="middle" class="ring-label">
        {status.active ? status.session.session_type : 'klaar'}
      </text>
    </svg>

    <!-- Linear progress bar underneath -->
    <div class="progress-track">
      <div class="progress-fill" style="width: {Math.max(0, progress)}%;"></div>
    </div>

    <div class="flex gap-2 justify-center" style="margin-top: 16px;">
      {#if status.active}
        <button class="danger" onclick={stop}>Stop</button>
      {:else}
        <button class="primary" onclick={start}>Start (25 min)</button>
      {/if}
    </div>
  </div>
{/if}

<style>
  .pomo-card { text-align: center; padding: 40px; max-width: 400px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; }
  .progress-ring { display: block; }
  .ring-timer { font-size: 36px; font-weight: 700; fill: var(--accent); font-variant-numeric: tabular-nums; }
  .ring-label { font-size: 14px; fill: var(--text-muted); text-transform: capitalize; }
  .progress-track {
    width: 200px; height: 6px; background: var(--bg-hover);
    border-radius: 3px; overflow: hidden; margin-top: 16px;
  }
  .progress-fill {
    height: 100%; background: var(--accent); border-radius: 3px;
    transition: width 0.2s linear;
  }
  .error-msg { background: #3a1a1a; border: 1px solid var(--red); padding: 12px; border-radius: var(--radius); margin-bottom: 16px; font-size: 14px; }
  .muted { color: var(--text-muted); font-style: italic; }
  .center { text-align: center; margin-top: 48px; }
</style>