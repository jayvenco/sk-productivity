<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let items = $state([]);
  let search = $state('');
  let editing = $state(null);
  let form = $state({ title: '', slug: '', content: '' });

  onMount(async () => { items = (await api.wiki.list()).items; });

  async function searchWiki() {
    items = (await api.wiki.list(search || undefined)).items;
  }

  async function save() {
    if (editing) {
      await api.wiki.update(editing, form);
    } else {
      await api.wiki.create(form);
    }
    editing = null;
    form = { title: '', slug: '', content: '' };
    items = (await api.wiki.list()).items;
  }

  function edit(item) {
    editing = item.id;
    form = { title: item.title, slug: item.slug, content: item.content };
  }

  async function remove(id) {
    if (confirm('Verwijder deze wiki pagina?')) {
      await api.wiki.delete(id);
      items = (await api.wiki.list()).items;
    }
  }

  function cancel() {
    editing = null;
    form = { title: '', slug: '', content: '' };
  }
</script>

<div class="header">
  <h1>Wiki</h1>
</div>

<div class="flex gap-2" style="margin-bottom: 16px;">
  <input bind:value={search} placeholder="Zoeken..." oninput={searchWiki} />
</div>

<div class="card form-card">
  <h3>{editing ? 'Bewerk pagina' : 'Nieuwe pagina'}</h3>
  <div class="flex-col gap-2">
    <input bind:value={form.title} placeholder="Titel" />
    <input bind:value={form.slug} placeholder="slug-van-pagina" />
    <textarea bind:value={form.content} placeholder="Markdown content..." rows="6"></textarea>
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
        <div>
          <h3>{item.title}</h3>
          <span class="slug">/{item.slug}</span>
        </div>
        <div class="flex gap-2">
          <button class="secondary" onclick={() => edit(item)}>Bewerk</button>
          <button class="danger" onclick={() => remove(item.id)}>Verwijder</button>
        </div>
      </div>
    </div>
  {/each}
</div>

<style>
  .header { margin-bottom: 16px; }
  .form-card { margin-bottom: 16px; }
  .form-card h3 { margin-bottom: 12px; }
  .items-list { display: flex; flex-direction: column; gap: 8px; }
  .slug { font-size: 12px; color: var(--text-muted); }
</style>