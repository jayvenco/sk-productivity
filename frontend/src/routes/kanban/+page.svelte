<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let columns = $state([]);
  let cardsByColumn = $state({});
  let form = $state({ title: '', description: '' });
  let colForm = $state({ name: '', color: '#6b7280' });
  let editingCol = $state(null);
  let error = $state('');
  let loading = $state(true);

  onMount(async () => {
    try { await load(); }
    catch (e) { error = e.message; }
    finally { loading = false; }
  });

  async function load() {
    const [cols, cards] = await Promise.all([
      api.kanban.columns.list(),
      api.kanban.list(),
    ]);
    columns = cols;
    const grouped = {};
    for (const c of cols) grouped[c.id] = [];
    for (const card of cards.items) {
      if (grouped[card.column_id]) grouped[card.column_id].push(card);
      else if (columns.length > 0) grouped[columns[0].id].push(card);
    }
    // Sort within each column by position
    for (const key of Object.keys(grouped)) {
      grouped[key].sort((a, b) => a.position - b.position);
    }
    cardsByColumn = grouped;
  }

  async function createCard() {
    error = '';
    if (!form.title) return;
    try {
      const target = columns[0];
      if (!target) { error = 'Maak eerst een kolom aan'; return; }
      const cards = cardsByColumn[target.id] || [];
      await api.kanban.create({ title: form.title, description: form.description, column_id: target.id, position: cards.length });
      form = { title: '', description: '' };
      await load();
    } catch (e) { error = e.message; }
  }

  async function moveCard(id, targetColId) {
    error = '';
    try {
      const targetCards = cardsByColumn[targetColId] || [];
      await api.kanban.update(id, { column_id: targetColId, position: targetCards.length });
      await load();
    } catch (e) { error = e.message; }
  }

  async function deleteCard(id) {
    if (!confirm('Verwijder deze kaart?')) return;
    error = '';
    try {
      await api.kanban.delete(id);
      await load();
    } catch (e) { error = e.message; }
  }

  async function createColumn() {
    error = '';
    if (!colForm.name) return;
    try {
      await api.kanban.columns.create({ name: colForm.name, color: colForm.color, position: columns.length });
      colForm = { name: '', color: '#6b7280' };
      await load();
    } catch (e) { error = e.message; }
  }

  async function renameColumn(id) {
    const newName = prompt('Nieuwe naam:', columns.find(c => c.id === id)?.name || '');
    if (!newName) return;
    try {
      await api.kanban.columns.rename(id, newName);
      await load();
    } catch (e) { error = e.message; }
  }

  async function deleteColumn(id) {
    const col = columns.find(c => c.id === id);
    if (!col || !confirm(`Verwijder kolom "${col.name}"? Kaarten worden verplaatst.`)) return;
    try {
      await api.kanban.columns.delete(id);
      await load();
    } catch (e) { error = e.message; }
  }

  function columnColor(col) {
    return col.color || '#6b7280';
  }
</script>

<div class="header">
  <h1>Kanban</h1>
  <div class="flex gap-2">
    <button class="secondary" onclick={() => editingCol = editingCol ? null : true}>+ Kolom</button>
  </div>
</div>

{#if error}
  <div class="error-msg" role="alert">{error}</div>
{/if}

{#if editingCol}
  <div class="card form-card col-form">
    <h3>Nieuwe kolom</h3>
    <div class="flex gap-2">
      <input bind:value={colForm.name} placeholder="Kolom naam" class="flex-1" aria-label="Naam" />
      <input type="color" bind:value={colForm.color} class="color-picker" title="Kleur" />
      <button class="primary" onclick={createColumn}>Maak</button>
      <button class="secondary" onclick={() => editingCol = null}>Annuleren</button>
    </div>
  </div>
{/if}

{#if loading}
  <p class="muted">Laden...</p>
{:else}
  <div class="card form-card">
    <div class="flex gap-2">
      <input bind:value={form.title} placeholder="Kaart titel" class="flex-1" aria-label="Titel" />
      <button class="primary" onclick={createCard}>Toevoegen</button>
    </div>
  </div>

  <div class="board">
    {#each columns as col (col.id)}
      <div class="column">
        <h3 class="col-title" style="border-left: 4px solid {columnColor(col)};">
          <span>{col.name}</span>
          <span class="col-actions">
            <button class="icon-btn" title="Hernoem" onclick={() => renameColumn(col.id)}>✏️</button>
            <button class="icon-btn" title="Verwijder" onclick={() => deleteColumn(col.id)}>🗑️</button>
          </span>
        </h3>
        {#each (cardsByColumn[col.id] || []) as card (card.id)}
          <div class="card kanban-card">
            <h4>{card.title}</h4>
            {#if card.description}<p>{card.description}</p>{/if}
            <div class="flex gap-2" style="margin-top: 8px;">
              {#each columns as target (target.id)}
                {#if target.id !== col.id}
                  <button class="secondary small" onclick={() => moveCard(card.id, target.id)}>
                    → {target.name}
                  </button>
                {/if}
              {/each}
              <button class="danger small" onclick={() => deleteCard(card.id)}>✕</button>
            </div>
          </div>
        {/each}
        {#if (cardsByColumn[col.id] || []).length === 0}
          <p class="muted">Geen kaarten</p>
        {/if}
      </div>
    {/each}
  </div>
{/if}

<style>
  .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
  .form-card { margin-bottom: 16px; }
  .col-form { margin-bottom: 16px; }
  .flex-1 { flex: 1; }
  .color-picker { width: 40px; height: 36px; padding: 2px; border: 1px solid var(--border); border-radius: var(--radius); background: transparent; cursor: pointer; }
  .board { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
  .column { display: flex; flex-direction: column; gap: 8px; }
  .col-title { font-size: 16px; font-weight: 600; margin-bottom: 8px; padding: 8px 10px; background: var(--bg-card); border-radius: var(--radius); border: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
  .col-actions { display: flex; gap: 4px; }
  .icon-btn { background: none; border: none; cursor: pointer; padding: 2px 4px; font-size: 14px; opacity: 0.6; transition: opacity 0.15s; }
  .icon-btn:hover { opacity: 1; }
  .kanban-card h4 { margin-bottom: 4px; }
  .kanban-card p { font-size: 13px; color: var(--text-muted); margin-bottom: 4px; }
  .muted { color: var(--text-muted); font-size: 13px; font-style: italic; }
  .error-msg { background: #3a1a1a; border: 1px solid var(--red); padding: 12px; border-radius: var(--radius); margin-bottom: 16px; font-size: 14px; }
  button.small { padding: 4px 8px; font-size: 12px; }
</style>