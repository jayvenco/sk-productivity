<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let { show = $bindable(true) } = $props();
  let deadlines = $state([]);
  let currentMonth = $state(new Date().getMonth());
  let currentYear = $state(new Date().getFullYear());
  let monthNames = ['Jan','Feb','Maa','Apr','Mei','Jun','Jul','Aug','Sep','Okt','Nov','Dec'];
  let dayNames = ['Ma','Di','Wo','Do','Vr','Za','Zo'];

  onMount(async () => {
    try {
      const res = await api.calendar.deadlines(90);
      deadlines = res.deadlines || [];
    } catch {}
  });

  function daysInMonth(m, y) { return new Date(y, m + 1, 0).getDate(); }
  function firstDay(m, y) { return (new Date(y, m, 1).getDay() + 6) % 7; } // Monday=0

  function getDeadlinesForDay(day) {
    const ds = `${currentYear}-${String(currentMonth + 1).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
    return deadlines.filter(d => d.due_date === ds);
  }

  function countByType(items) {
    let tasks = 0, kanban = 0;
    for (const i of items) {
      if (i.item_type === 'task') tasks++;
      else kanban++;
    }
    return { tasks, kanban };
  }

  function prevMonth() { if (currentMonth === 0) { currentMonth = 11; currentYear--; } else currentMonth--; }
  function nextMonth() { if (currentMonth === 11) { currentMonth = 0; currentYear++; } else currentMonth++; }
</script>

<div class="cal-widget" class:collapsed={!show}>
  <div class="cal-header" onclick={() => show = !show}>
    <span class="cal-title">📅 {monthNames[currentMonth]} {currentYear}</span>
    <span class="cal-toggle">{show ? '▲' : '▼'}</span>
  </div>

  {#if show}
    <div class="cal-nav">
      <button class="cal-nav-btn" onclick={prevMonth}>◀</button>
      <button class="cal-nav-btn" onclick={nextMonth}>▶</button>
    </div>

    <div class="cal-grid">
      {#each dayNames as d}
        <span class="cal-day-name">{d}</span>
      {/each}
      {#each Array(firstDay(currentMonth, currentYear)) as _}
        <span class="cal-day empty"></span>
      {/each}
      {#each Array(daysInMonth(currentMonth, currentYear)) as _, i}
        {@const day = i + 1}
        {@const items = getDeadlinesForDay(day)}
        {@const counts = countByType(items)}
        <span class="cal-day" class:has-deadline={items.length > 0} title={items.length > 0 ? `${items.length} deadline(s)` : ''}>
          {day}
          {#if items.length > 0}
            <span class="cal-dots">
              {#if counts.tasks > 0}<span class="dot task-dot"></span>{/if}
              {#if counts.kanban > 0}<span class="dot kanban-dot"></span>{/if}
            </span>
          {/if}
        </span>
      {/each}
    </div>
  {/if}
</div>

<style>
  .cal-widget {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 10px;
    font-size: 12px;
    user-select: none;
  }

  .cal-widget.collapsed {
    padding: 6px 10px;
  }

  .cal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
  }

  .cal-title {
    font-weight: 600;
    font-size: 13px;
  }

  .cal-toggle {
    font-size: 10px;
    color: var(--text-muted);
  }

  .cal-nav {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin: 6px 0;
  }

  .cal-nav-btn {
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    padding: 2px 6px;
    font-size: 12px;
    font-family: inherit;
  }

  .cal-nav-btn:hover { color: var(--text); }

  .cal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 2px;
    text-align: center;
  }

  .cal-day-name {
    font-size: 10px;
    color: var(--text-muted);
    padding: 3px 0;
    font-weight: 500;
  }

  .cal-day {
    padding: 4px 2px;
    border-radius: 4px;
    font-size: 11px;
    color: var(--text);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    min-height: 28px;
  }

  .cal-day.empty {
    visibility: hidden;
  }

  .cal-day.has-deadline {
    background: var(--bg-hover);
  }

  .cal-dots {
    display: flex;
    gap: 2px;
  }

  .dot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
  }

  .task-dot { background: var(--accent); }
  .kanban-dot { background: var(--blue); }
</style>