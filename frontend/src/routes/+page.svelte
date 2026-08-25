<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let stats = $state({
    notes: 0,
    tasks: 0,
    kanban: 0,
    pomodoro: 0,
    wiki: 0,
    snippets: 0,
  });

  onMount(async () => {
    try {
      const [notes, tasks, kanban, sessions, wiki, snippets] = await Promise.all([
        api.notes.list(),
        api.tasks.list(),
        api.kanban.list(),
        api.pomodoro.list(),
        api.wiki.list(),
        api.snippets.list(),
      ]);
      stats = {
        notes: notes.total,
        tasks: tasks.total,
        kanban: kanban.total,
        pomodoro: sessions.length,
        wiki: wiki.total,
        snippets: snippets.total,
      };
    } catch (e) {
      console.error('Failed to load stats', e);
    }
  });
</script>

<h1>Dashboard</h1>
<p class="subtitle">Welkom bij swissknife-productivity — alles-in-één voor jouw dagelijkse workflow.</p>

<div class="grid grid-3">
  <a href="/notes" class="card stat-card">
    <span class="stat-icon">📝</span>
    <span class="stat-value">{stats.notes}</span>
    <span class="stat-label">Notities</span>
  </a>
  <a href="/tasks" class="card stat-card">
    <span class="stat-icon">✓</span>
    <span class="stat-value">{stats.tasks}</span>
    <span class="stat-label">Taken</span>
  </a>
  <a href="/kanban" class="card stat-card">
    <span class="stat-icon">☰</span>
    <span class="stat-value">{stats.kanban}</span>
    <span class="stat-label">Kanban</span>
  </a>
  <a href="/pomodoro" class="card stat-card">
    <span class="stat-icon">⏱</span>
    <span class="stat-value">{stats.pomodoro}</span>
    <span class="stat-label">Pomodoro</span>
  </a>
  <a href="/wiki" class="card stat-card">
    <span class="stat-icon">📖</span>
    <span class="stat-value">{stats.wiki}</span>
    <span class="stat-label">Wiki</span>
  </a>
  <a href="/snippets" class="card stat-card">
    <span class="stat-icon">💻</span>
    <span class="stat-value">{stats.snippets}</span>
    <span class="stat-label">Snippets</span>
  </a>
</div>

<style>
  .subtitle {
    color: var(--text-muted);
    margin-bottom: 24px;
  }

  .stat-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 24px;
    transition: background 0.2s, border-color 0.2s;
  }

  .stat-card:hover {
    background: var(--bg-hover);
    border-color: var(--accent);
  }

  .stat-icon { font-size: 32px; }
  .stat-value { font-size: 32px; font-weight: 700; color: var(--accent); }
  .stat-label { font-size: 14px; color: var(--text-muted); }
</style>