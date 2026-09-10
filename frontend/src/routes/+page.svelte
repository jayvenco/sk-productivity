<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let stats = $state({
    notes: 0, tasks: 0, kanban: 0, pomodoro: 0, wiki: 0, snippets: 0,
  });
  let recentTasks = $state([]);
  let recentNotes = $state([]);
  let loading = $state(true);

  onMount(async () => {
    try {
      const [notes, tasks, kanban, sessions, wiki, snippets] = await Promise.all([
        api.notes.list(), api.tasks.list(), api.kanban.list(),
        api.pomodoro.list(), api.wiki.list(), api.snippets.list(),
      ]);
      stats = {
        notes: notes.total, tasks: tasks.total, kanban: kanban.total,
        pomodoro: sessions.length, wiki: wiki.total, snippets: snippets.total,
      };
      recentTasks = (tasks.items || []).filter(t => t.status !== 'completed').slice(0, 5);
      recentNotes = (notes.items || []).slice(0, 3);
    } catch (e) { console.error('Failed to load stats', e); }
    finally { loading = false; }
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

{#if loading}
  <p class="muted loader">Laden...</p>
{:else}
  {#if recentTasks.length > 0}
    <h2 class="section-title">📋 Openstaande taken</h2>
    <div class="compact-list">
      {#each recentTasks as task (task.id)}
        <a href="/tasks" class="compact-item" class:overdue={task.due_date && new Date(task.due_date) < new Date()}>
          <span class="compact-dot" class:done={task.status === 'in_progress'}></span>
          <span class="compact-title">{task.title}</span>
          {#if task.due_date}
            <span class="compact-due">🔴</span>
          {/if}
        </a>
      {/each}
    </div>
  {/if}

  {#if recentNotes.length > 0}
    <h2 class="section-title">📝 Recente notities</h2>
    <div class="compact-list">
      {#each recentNotes as note (note.id)}
        <a href="/notes" class="compact-item">
          <span class="compact-title">{note.title}</span>
        </a>
      {/each}
    </div>
  {/if}
{/if}

<style>
  .subtitle { color: var(--text-muted); margin-bottom: 20px; }

  .stat-card {
    display: flex; flex-direction: column; align-items: center;
    gap: 4px; padding: 20px; transition: all 0.15s;
  }
  .stat-card:hover { background: var(--bg-hover); border-color: var(--accent); }
  .stat-icon { font-size: 28px; }
  .stat-value { font-size: 28px; font-weight: 700; color: var(--accent); }
  .stat-label { font-size: 13px; color: var(--text-muted); }

  .section-title { font-size: 15px; font-weight: 600; margin: 20px 0 8px; }
  .loader { margin-top: 16px; }

  .compact-list { display: flex; flex-direction: column; gap: 2px; }
  .compact-item {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 12px; border-radius: var(--radius);
    color: var(--text); text-decoration: none; font-size: 13px;
    transition: background 0.1s;
  }
  .compact-item:hover { background: var(--bg-hover); }
  .compact-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--border); flex-shrink: 0;
  }
  .compact-dot.done { background: var(--accent); }
  .compact-item.overdue .compact-title { color: var(--red); }
  .compact-title { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .compact-due { font-size: 10px; }
</style>