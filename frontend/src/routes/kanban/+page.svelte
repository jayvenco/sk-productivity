<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import TagSelector from '$lib/components/TagSelector.svelte';

  let columns = $state([]);
  let swimlanes = $state([]);
  let cardsByCell = $state({});
  let form = $state({ title: '', description: '' });
  let colForm = $state({ name: '', color: '#6b7280' });
  let swForm = $state({ name: '', color: '#444466' });
  let editingCol = $state(null);
  let editingSw = $state(null);
  let error = $state('');
  let loading = $state(true);

  onMount(async () => {
    try { await load(); }
    catch (e) { error = e.message; }
    finally { loading = false; }
  });

  async function load() {
    const [cols, sws, cards] = await Promise.all([
      api.kanban.columns.list(),
      api.kanban.swimlanes.list(),
      api.kanban.list(),
    ]);
    columns = cols;
    swimlanes = sws;
    const grouped = {};
    for (const c of cols) {
      for (const s of (sws.length ? sws : [{ id: null }])) {
        grouped[`${c.id}-${s.id}`] = [];
      }
    }
    for (const card of cards.items) {
      const key = `${card.column_id}-${card.swimlane_id}`;
      if (grouped[key]) grouped[key].push(card);
      else if (columns.length > 0) {
        const fallback = `${columns[0].id}-${card.swimlane_id || null}`;
        if (grouped[fallback]) grouped[fallback].push(card);
      }
    }
    for (const key of Object.keys(grouped)) {
      grouped[key].sort((a, b) => a.position - b.position);
    }
    cardsByCell = grouped;
  }

  async function createCard() {
    error = '';
    if (!form.title) return;
    try {
      const target = columns[0];
      if (!target) { error = 'Maak eerst een kolom aan'; return; }
      const firstSw = swimlanes.length ? swimlanes[0] : null;
      const key = `${target.id}-${firstSw?.id || null}`;
      const cards = cardsByCell[key] || [];
      await api.kanban.create({ title: form.title, description: form.description, column_id: target.id, swimlane_id: firstSw?.id || null, position: cards.length });
      form = { title: '', description: '' };
      await load();
    } catch (e) { error = e.message; }
  }

  async function moveCard(id, targetColId, targetSwId) {
    error = '';
    try {
      const key = `${targetColId}-${targetSwId}`;
      const targetCards = cardsByCell[key] || [];
      await api.kanban.update(id, { column_id: targetColId, swimlane_id: targetSwId, position: targetCards.length });
      await load();
    } catch (e) { error = e.message; }
  }

  async function deleteCard(id) {
    if (!confirm('Verwijder deze kaart?')) return;
    error = '';
    try { await api.kanban.delete(id); await load(); }
    catch (e) { error = e.message; }
  }

  async function createColumn() {
    error = ''; if (!colForm.name) return;
    try { await api.kanban.columns.create({ name: colForm.name, color: colForm.color, position: columns.length }); colForm = { name: '', color: '#6b7280' }; await load(); }
    catch (e) { error = e.message; }
  }

  async function renameColumn(id) {
    const n = prompt('Nieuwe naam:', columns.find(c => c.id === id)?.name || '');
    if (!n) return;
    try { await api.kanban.columns.rename(id, n); await load(); }
    catch (e) { error = e.message; }
  }

  async function deleteColumn(id) {
    const col = columns.find(c => c.id === id);
    if (!col || !confirm(`Verwijder kolom "${col.name}"?`)) return;
    try { await api.kanban.columns.delete(id); await load(); }
    catch (e) { error = e.message; }
  }

  async function createSwimlane() {
    error = ''; if (!swForm.name) return;
    try { await api.kanban.swimlanes.create({ name: swForm.name, color: swForm.color, position: swimlanes.length }); swForm = { name: '', color: '#444466' }; await load(); }
    catch (e) { error = e.message; }
  }

  async function renameSwimlane(id) {
    const n = prompt('Nieuwe naam:', swimlanes.find(s => s.id === id)?.name || '');
    if (!n) return;
    try { await api.kanban.swimlanes.rename(id, n); await load(); }
    catch (e) { error = e.message; }
  }

  async function deleteSwimlane(id) {
    const sw = swimlanes.find(s => s.id === id);
    if (!sw || !confirm(`Verwijder swimlane "${sw.name}"?`)) return;
    try { await api.kanban.swimlanes.delete(id); await load(); }
    catch (e) { error = e.message; }
  }

  function colColor(col) { return col.color || '#6b7280'; }
  function swColor(sw) { return sw.color || '#444466'; }
  function cellKey(colId, swId) { return `${colId}-${swId}`; }

  function cellCards(colId, swId) {
    return cardsByCell[cellKey(colId, swId)] || [];
  }
</script>

<div class="header">
  <h1>Kanban</h1>
  <div class="flex gap-2">
    <button class="secondary" onclick={() => editingCol = editingCol ? null : true}>+ Kolom</button>
    <button class="secondary" onclick={() => editingSw = editingSw ? null : true}>+ Swimlane</button>
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

{#if editingSw}
  <div class="card form-card col-form">
    <h3>Nieuwe swimlane</h3>
    <div class="flex gap-2">
      <input bind:value={swForm.name} placeholder="Swimlane naam" class="flex-1" aria-label="Naam" />
      <input type="color" bind:value={swForm.color} class="color-picker" title="Kleur" />
      <button class="primary" onclick={createSwimlane}>Maak</button>
      <button class="secondary" onclick={() => editingSw = null}>Annuleren</button>
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

  {#if swimlanes.length > 0}
    <div class="swimlane-board">
      <!-- Header row: column names -->
      <div class="sw-header-row">
        <div class="sw-corner"></div>
        {#each columns as col (col.id)}
          <div class="sw-header" style="border-color: {colColor(col)};">
            <span>{col.name}</span>
            <span class="col-actions">
              <button class="icon-btn" title="Hernoem" onclick={() => renameColumn(col.id)}>✏️</button>
              <button class="icon-btn" title="Verwijder" onclick={() => deleteColumn(col.id)}>🗑️</button>
            </span>
          </div>
        {/each}
      </div>
      <!-- Swimlane rows -->
      {#each swimlanes as sw (sw.id)}
        <div class="sw-row">
          <div class="sw-label" style="border-left: 4px solid {swColor(sw)}; background: {swColor(sw)}15;">
            <span class="sw-name">{sw.name}</span>
            <span class="col-actions">
              <button class="icon-btn" title="Hernoem" onclick={() => renameSwimlane(sw.id)}>✏️</button>
              <button class="icon-btn" title="Verwijder" onclick={() => deleteSwimlane(sw.id)}>🗑️</button>
            </span>
          </div>
          {#each columns as col (col.id)}
            <div class="sw-cell">
              {#each cellCards(col.id, sw.id) as card (card.id)}
                <div class="card kanban-card">
                  <h4>{card.title}</h4>
                  {#if card.description}<p>{card.description}</p>{/if}
                  <TagSelector itemType="kanban" itemId={card.id} />
                  <div class="flex gap-2" style="margin-top: 6px;">
                    {#each columns as target (target.id)}
                      {#if target.id !== col.id}
                        <button class="secondary small" onclick={() => moveCard(card.id, target.id, sw.id)}>→ {target.name}</button>
                      {/if}
                    {/each}
                    {#each swimlanes as target (target.id)}
                      {#if target.id !== sw.id}
                        <button class="secondary small" onclick={() => moveCard(card.id, col.id, target.id)}>↓ {target.name}</button>
                      {/if}
                    {/each}
                    <button class="danger small" onclick={() => deleteCard(card.id)}>✕</button>
                  </div>
                </div>
              {/each}
              {#if cellCards(col.id, sw.id).length === 0}
                <p class="muted">—</p>
              {/if}
            </div>
          {/each}
        </div>
      {/each}
    </div>
  {:else}
    <!-- Geen swimlanes: toon kolommen zoals voorheen -->
    <div class="board">
      {#each columns as col (col.id)}
        <div class="column">
          <h3 class="col-title" style="border-left: 4px solid {colColor(col)};">
            <span>{col.name}</span>
            <span class="col-actions">
              <button class="icon-btn" title="Hernoem" onclick={() => renameColumn(col.id)}>✏️</button>
              <button class="icon-btn" title="Verwijder" onclick={() => deleteColumn(col.id)}>🗑️</button>
            </span>
          </h3>
          {#each cellCards(col.id, null) as card (card.id)}
            <div class="card kanban-card">
              <h4>{card.title}</h4>
              {#if card.description}<p>{card.description}</p>{/if}
              <TagSelector itemType="kanban" itemId={card.id} />
              <div class="flex gap-2" style="margin-top: 8px;">
                {#each columns as target (target.id)}
                  {#if target.id !== col.id}
                    <button class="secondary small" onclick={() => moveCard(card.id, target.id, null)}>→ {target.name}</button>
                  {/if}
                {/each}
                <button class="danger small" onclick={() => deleteCard(card.id)}>✕</button>
              </div>
            </div>
          {/each}
          {#if cellCards(col.id, null).length === 0}
            <p class="muted">Geen kaarten</p>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
{/if}

<style>
  .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
  .form-card { margin-bottom: 16px; }
  .col-form { margin-bottom: 16px; }
  .flex-1 { flex: 1; }
  .color-picker { width: 40px; height: 36px; padding: 2px; border: 1px solid var(--border); border-radius: var(--radius); background: transparent; cursor: pointer; }
  .muted { color: var(--text-muted); font-size: 13px; font-style: italic; }
  .error-msg { background: #3a1a1a; border: 1px solid var(--red); padding: 12px; border-radius: var(--radius); margin-bottom: 16px; font-size: 14px; }
  button.small { padding: 4px 8px; font-size: 12px; }
  .icon-btn { background: none; border: none; cursor: pointer; padding: 2px 4px; font-size: 14px; opacity: 0.6; transition: opacity 0.15s; }
  .icon-btn:hover { opacity: 1; }
  .col-actions { display: flex; gap: 4px; }

  /* Grid layout (zonder swimlanes) */
  .board { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
  .column { display: flex; flex-direction: column; gap: 8px; }
  .col-title { font-size: 16px; font-weight: 600; margin-bottom: 8px; padding: 8px 10px; background: var(--bg-card); border-radius: var(--radius); border: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
  .kanban-card h4 { margin-bottom: 4px; }
  .kanban-card p { font-size: 13px; color: var(--text-muted); margin-bottom: 4px; }

  /* Swimlane layout */
  .swimlane-board {
    display: flex;
    flex-direction: column;
    gap: 0;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
  }
  .sw-header-row {
    display: flex;
    background: var(--bg-card);
    border-bottom: 2px solid var(--border);
  }
  .sw-corner {
    width: 140px;
    min-width: 140px;
    flex-shrink: 0;
  }
  .sw-header {
    flex: 1;
    padding: 10px 12px;
    font-weight: 600;
    font-size: 14px;
    border-left: 4px solid;
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-width: 200px;
  }
  .sw-row {
    display: flex;
    border-bottom: 1px solid var(--border);
  }
  .sw-row:last-child { border-bottom: none; }
  .sw-label {
    width: 140px;
    min-width: 140px;
    flex-shrink: 0;
    padding: 10px;
    font-weight: 600;
    font-size: 13px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    border-right: 1px solid var(--border);
  }
  .sw-name { font-size: 13px; }
  .sw-cell {
    flex: 1;
    padding: 8px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    min-width: 200px;
    border-right: 1px solid var(--border);
    min-height: 60px;
  }
  .sw-cell:last-child { border-right: none; }
</style>