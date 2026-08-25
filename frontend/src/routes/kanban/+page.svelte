<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let todo = $state([]);
  let doing = $state([]);
  let done = $state([]);
  let form = $state({ title: '', description: '' });
  let error = $state('');
  let loading = $state(true);

  onMount(async () => {
    try { await load(); }
    catch (e) { error = e.message; }
    finally { loading = false; }
  });

  async function load() {
    const all = (await api.kanban.list()).items;
    todo = all.filter(c => c.status === 'todo').sort((a,b) => a.position - b.position);
    doing = all.filter(c => c.status === 'doing').sort((a,b) => a.position - b.position);
    done = all.filter(c => c.status === 'done').sort((a,b) => a.position - b.position);
  }

  async function create() {
    error = '';
    if (!form.title) return;
    try {
      await api.kanban.create({ title: form.title, description: form.description, status: 'todo', position: todo.length });
      form = { title: '', description: '' };
      await load();
    } catch (e) { error = e.message; }
  }

  async function move(id, status, pos) {
    error = '';
    try {
      await api.kanban.update(id, { status, position: pos });
      await load();
    } catch (e) { error = e.message; }
  }

  async function remove(id) {
    if (!confirm('Verwijder deze kaart?')) return;
    error = '';
    try {
      await api.kanban.delete(id);
      await load();
    } catch (e) { error = e.message; }
  }
</script>

<div class="header">
  <h1>Kanban</h1>
</div>

{#if error}
  <div class="error-msg" role="alert">{error}</div>
{/if}

{#if loading}
  <p class="muted">Laden...</p>
{:else}
  <div class="card form-card">
    <div class="flex gap-2">
      <input bind:value={form.title} placeholder="Kaart titel" class="flex-1" aria-label="Titel" />
      <button class="primary" onclick={create}>Toevoegen</button>
    </div>
  </div>

  <div class="board">
    <div class="column">
      <h3 class="col-title">📋 Te doen</h3>
      {#each todo as card (card.id)}
        <div class="card kanban-card">
          <h4>{card.title}</h4>
          {#if card.description}<p>{card.description}</p>{/if}
          <div class="flex gap-2" style="margin-top: 8px;">
            <button class="secondary" onclick={() => move(card.id, 'doing', doing.length)}>→ Doing</button>
            <button class="danger" onclick={() => remove(card.id)}>✕</button>
          </div>
        </div>
      {/each}
      {#if todo.length === 0}<p class="muted">Geen</p>{/if}
    </div>
    <div class="column">
      <h3 class="col-title">⚡ Bezig</h3>
      {#each doing as card (card.id)}
        <div class="card kanban-card">
          <h4>{card.title}</h4>
          {#if card.description}<p>{card.description}</p>{/if}
          <div class="flex gap-2" style="margin-top: 8px;">
            <button class="secondary" onclick={() => move(card.id, 'todo', todo.length)}>← Todo</button>
            <button class="secondary" onclick={() => move(card.id, 'done', done.length)}>→ Done</button>
            <button class="danger" onclick={() => remove(card.id)}>✕</button>
          </div>
        </div>
      {/each}
      {#if doing.length === 0}<p class="muted">Geen</p>{/if}
    </div>
    <div class="column">
      <h3 class="col-title">✅ Klaar</h3>
      {#each done as card (card.id)}
        <div class="card kanban-card">
          <h4>{card.title}</h4>
          {#if card.description}<p>{card.description}</p>{/if}
          <div class="flex gap-2" style="margin-top: 8px;">
            <button class="secondary" onclick={() => move(card.id, 'doing', doing.length)}>← Doing</button>
            <button class="danger" onclick={() => remove(card.id)}>✕</button>
          </div>
        </div>
      {/each}
      {#if done.length === 0}<p class="muted">Geen</p>{/if}
    </div>
  </div>
{/if}

<style>
  .header { margin-bottom: 16px; }
  .form-card { margin-bottom: 16px; }
  .flex-1 { flex: 1; }
  .board { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
  .column { display: flex; flex-direction: column; gap: 8px; }
  .col-title { font-size: 16px; font-weight: 600; margin-bottom: 8px; padding: 8px; background: var(--bg-card); border-radius: var(--radius); border: 1px solid var(--border); }
  .kanban-card h4 { margin-bottom: 4px; }
  .kanban-card p { font-size: 13px; color: var(--text-muted); margin-bottom: 4px; }
  .muted { color: var(--text-muted); font-size: 13px; font-style: italic; }
  .error-msg { background: #3a1a1a; border: 1px solid var(--red); padding: 12px; border-radius: var(--radius); margin-bottom: 16px; font-size: 14px; }
</style>