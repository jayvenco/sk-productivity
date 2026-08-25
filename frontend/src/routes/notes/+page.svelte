<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let items = $state([]);
  let editing = $state(null);
  let form = $state({ title: '', content: '' });

  onMount(async () => {
    items = (await api.notes.list()).items;
  });

  async function save() {
    if (editing) {
      await api.notes.update(editing, form);
    } else {
      await api.notes.create(form);
    }
    editing = null;
    form = { title: '', content: '' };
    items = (await api.notes.list()).items;
  }

  function edit(item) {
    editing = item.id;
    form = { title: item.title, content: item.content };
  }

  async function remove(id) {
    if (confirm('Verwijder deze notitie?')) {
      await api.notes.delete(id);
      items = (await api.notes.list()).items;
    }
  }

  function cancel() {
    editing = null;
    form = { title: '', content: '' };
  }
</script>

<div class="header">
  <h1>Notities</h1>
</div>

<div class="card form-card">
  <h3>{editing ? 'Bewerk notitie' : 'Nieuwe notitie'}</h3>
  <div class="flex-col gap-2">
    <input bind:value={form.title} placeholder="Titel" />
    <textarea bind:value={form.content} placeholder="Schrijf hier..." rows="4"></textarea>
    <div class="flex gap-2">
      <button class="primary" onclick={save}>{editing ? 'Opslaan' : 'Toevoegen'}</button>
      {#if editing}<button class="secondary" onclick={cancel}>Annuleren</button>{/if}
    </div>
  </div>
</div>

<div class="items-list">
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
      <span class="date">{new Date(item.created_at).toLocaleDateString('nl-NL')}</span>
    </div>
  {/each}
</div>

<style>
  .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
  .form-card { margin-bottom: 16px; }
  .form-card h3 { margin-bottom: 12px; }
  .items-list { display: flex; flex-direction: column; gap: 8px; }
  .item-card h3 { margin-bottom: 8px; }
  .content { color: var(--text-muted); white-space: pre-wrap; margin-bottom: 8px; }
  .date { font-size: 12px; color: var(--text-muted); }
</style>