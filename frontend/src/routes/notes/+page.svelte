<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import TagSelector from '$lib/components/TagSelector.svelte';
  import ColorPicker from '$lib/components/ColorPicker.svelte';

  let items = $state([]);
  let editing = $state(null);
  let form = $state({ title: '', content: '', color: '#262a36' });
  let error = $state('');
  let loading = $state(true);

  onMount(async () => {
    try { items = (await api.notes.list()).items; }
    catch (e) { error = e.message; }
    finally { loading = false; }
  });

  async function save() {
    error = '';
    try {
      if (editing) await api.notes.update(editing, form);
      else await api.notes.create(form);
      editing = null;
      form = { title: '', content: '' };
      items = (await api.notes.list()).items;
    } catch (e) { error = e.message; }
  }

  function edit(item) {
    editing = item.id;
    form = { title: item.title, content: item.content, color: item.color || '#262a36' };
  }

  async function remove(id) {
    if (!confirm('Verwijder deze notitie?')) return;
    error = '';
    try {
      await api.notes.delete(id);
      items = (await api.notes.list()).items;
    } catch (e) { error = e.message; }
  }

  function cancel() {
    editing = null;
    form = { title: '', content: '' };
  }
</script>

<div class="header">
  <h1>Notities</h1>
</div>

{#if error}
  <div class="error-msg" role="alert">{error}</div>
{/if}

{#if loading}
  <p class="muted">Laden...</p>
{:else}
  <div class="card form-card">
    <h3>{editing ? 'Bewerk notitie' : 'Nieuwe notitie'}</h3>
    <div class="flex-col gap-2">
      <input bind:value={form.title} placeholder="Titel" aria-label="Titel" />
      <textarea bind:value={form.content} placeholder="Schrijf hier..." rows="4" aria-label="Inhoud"></textarea>
      <div class="flex gap-2 items-center">
        <ColorPicker bind:value={form.color} />
        <button class="primary" onclick={save}>{editing ? 'Opslaan' : 'Toevoegen'}</button>
        {#if editing}<button class="secondary" onclick={cancel}>Annuleren</button>{/if}
      </div>
    </div>
  </div>

  <div class="items-list">
    {#if items.length === 0}
      <p class="muted">Geen notities — maak er een aan.</p>
    {:else}
      {#each items as item (item.id)}
        <div class="card item-card" class:has-color={item.color && item.color !== '#262a36'} style="border-left-color: {item.color || '#262a36'};" onclick={() => edit(item)} role="button" tabindex="0" onkeydown={(e) => e.key === 'Enter' && edit(item)}>
          <div class="flex justify-between items-start" style="gap: 8px;">
            <div class="card-content">
              <h3>{item.title}</h3>
              <p class="preview">{item.content}</p>
            </div>
            <div class="card-actions" onclick={(e) => e.stopPropagation()}>
              <button class="danger small" onclick={() => remove(item.id)} title="Verwijder">✕</button>
            </div>
          </div>
          <div class="card-footer">
            <TagSelector itemType="note" itemId={item.id} />
            <span class="date">{new Date(item.created_at).toLocaleDateString('nl-NL')}</span>
          </div>
        </div>
      {/each}
    {/if}
  </div>
{/if}

<style>
  .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
  .form-card { margin-bottom: 16px; }
  .form-card h3 { margin-bottom: 12px; }
  .items-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 10px; }
  .item-card {
    cursor: pointer;
    transition: all 0.15s;
    display: flex;
    flex-direction: column;
    gap: 0;
    padding: 14px;
    border-left: 3px solid var(--border);
  }
  .item-card.has-color {
    border-left-width: 4px;
  }
  .item-card:hover {
    border-color: var(--accent);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
  }
  .item-card h3 {
    font-size: 14px;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .card-content { flex: 1; min-width: 0; }
  .card-actions { flex-shrink: 0; }
  .preview {
    color: var(--text-muted);
    font-size: 12px;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin-bottom: 8px;
  }
  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    margin-top: auto;
  }
  .date { font-size: 11px; color: var(--text-muted); white-space: nowrap; }
  .error-msg { background: #3a1a1a; border: 1px solid var(--red); padding: 12px; border-radius: var(--radius); margin-bottom: 16px; font-size: 14px; }
  .muted { color: var(--text-muted); font-style: italic; }
  button.small { padding: 4px 8px; font-size: 11px; }
</style>