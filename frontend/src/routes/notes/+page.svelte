<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import TagSelector from '$lib/components/TagSelector.svelte';

  let items = $state([]);
  let editing = $state(null);
  let form = $state({ title: '', content: '' });
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
    form = { title: item.title, content: item.content };
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
      <div class="flex gap-2">
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
        <div class="card item-card">
          <div class="flex justify-between items-center">
            <h3>{item.title}</h3>
            <div class="flex gap-2">
              <button class="secondary" onclick={() => edit(item)}>Bewerk</button>
              <button class="danger" onclick={() => remove(item.id)}>Verwijder</button>
            </div>
          </div>
          <p class="content">{item.content}</p>
          <TagSelector itemType="note" itemId={item.id} />
          <span class="date">{new Date(item.created_at).toLocaleDateString('nl-NL')}</span>
        </div>
      {/each}
    {/if}
  </div>
{/if}

<style>
  .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
  .form-card { margin-bottom: 16px; }
  .form-card h3 { margin-bottom: 12px; }
  .items-list { display: flex; flex-direction: column; gap: 8px; }
  .item-card h3 { margin-bottom: 8px; }
  .content { color: var(--text-muted); white-space: pre-wrap; margin-bottom: 8px; }
  .date { font-size: 12px; color: var(--text-muted); }
  .error-msg { background: #3a1a1a; border: 1px solid var(--red); padding: 12px; border-radius: var(--radius); margin-bottom: 16px; font-size: 14px; }
  .muted { color: var(--text-muted); font-style: italic; }
</style>