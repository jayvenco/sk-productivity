<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let todo = $state([]);
  let doing = $state([]);
  let done = $state([]);
  let form = $state({ title: '', description: '' });

  onMount(async () => { await load(); });

  async function load() {
    const all = (await api.kanban.list()).items;
    todo = all.filter(c => c.status === 'todo').sort((a,b) => a.position - b.position);
    doing = all.filter(c => c.status === 'doing').sort((a,b) => a.position - b.position);
    done = all.filter(c => c.status === 'done').sort((a,b) => a.position - b.position);
  }

  async function create() {
    if (!form.title) return;
    await api.kanban.create({ title: form.title, description: form.description, status: 'todo', position: todo.length });
    form = { title: '', description: '' };
    await load();
  }

  async function move(id, status, pos) {
    await api.kanban.update(id, { status, position: pos });
    await load();
  }

  async function remove(id) {
    if (confirm('Verwijder deze kaart?')) {
      await api.kanban.delete(id);
      await load();
    }
  }
</script>

<div class="header">
  <h1>Kanban</h1>
</div>

<div class="card form-card">
  <div class="flex gap-2">
    <input bind:value={form.title} placeholder="Kaart titel" class="flex-1" />
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
  </div>
</div>

<style>
  .header { margin-bottom: 16px; }
  .form-card { margin-bottom: 16px; }
  .flex-1 { flex: 1; }
  .board { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
  .column { display: flex; flex-direction: column; gap: 8px; }
  .col-title { font-size: 16px; font-weight: 600; margin-bottom: 8px; padding: 8px; background: var(--bg-card); border-radius: var(--radius); border: 1px solid var(--border); }
  .kanban-card h4 { margin-bottom: 4px; }
  .kanban-card p { font-size: 13px; color: var(--text-muted); }
</style>