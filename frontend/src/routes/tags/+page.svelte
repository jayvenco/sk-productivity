<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let tags = $state([]);
  let editing = $state(null);
  let form = $state({ name: '', color: '#4f8cff' });
  let error = $state('');
  let loading = $state(true);

  const colors = ['#4f8cff','#4caf50','#ff9800','#f44336','#9c27b0','#00bcd4','#e91e63','#607d8b','#ff5722','#8bc34a'];

  onMount(async () => { await load(); });

  async function load() {
    try { tags = (await api.tags.list()).items; }
    catch (e) { error = e.message; }
    finally { loading = false; }
  }

  async function save() {
    error = '';
    if (!form.name.trim()) return;
    try {
      if (editing) { await api.tags.update(editing, form); }
      else { await api.tags.create(form); }
      editing = null;
      form = { name: '', color: '#4f8cff' };
      await load();
    } catch (e) { error = e.message; }
  }

  function edit(tag) {
    editing = tag.id;
    form = { name: tag.name, color: tag.color };
  }

  async function remove(id) {
    if (!confirm('Verwijder deze tag? Hij wordt van alle items losgekoppeld.')) return;
    error = '';
    try { await api.tags.delete(id); await load(); }
    catch (e) { error = e.message; }
  }

  function cancel() {
    editing = null;
    form = { name: '', color: '#4f8cff' };
  }
</script>

<div class="header">
  <h1>🏷️ Tags</h1>
</div>

{#if error}
  <div class="error-msg" role="alert">{error}</div>
{/if}

{#if loading}
  <p class="muted">Laden...</p>
{:else}
  <div class="card form-card">
    <h3>{editing ? 'Bewerk tag' : 'Nieuwe tag'}</h3>
    <div class="flex-col gap-2">
      <input bind:value={form.name} placeholder="Tag naam" aria-label="Tag naam" />
      <div class="color-picker" role="radiogroup" aria-label="Kleur kiezen">
        {#each colors as c}
          <button
            class="color-dot" class:selected={form.color === c}
            style="background: {c};"
            onclick={() => form.color = c}
            aria-label={c}
          ></button>
        {/each}
      </div>
      <div class="flex gap-2">
        <button class="primary" onclick={save}>{editing ? 'Opslaan' : 'Toevoegen'}</button>
        {#if editing}<button class="secondary" onclick={cancel}>Annuleren</button>{/if}
      </div>
    </div>
  </div>

  <div class="items-list">
    {#if tags.length === 0}
      <p class="muted">Geen tags — maak er een aan.</p>
    {:else}
      {#each tags as tag (tag.id)}
        <div class="card tag-item">
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-2">
              <span class="color-swatch" style="background: {tag.color};"></span>
              <span class="tag-name">{tag.name}</span>
            </div>
            <div class="flex gap-2">
              <button class="secondary" onclick={() => edit(tag)}>Bewerk</button>
              <button class="danger" onclick={() => remove(tag.id)}>Verwijder</button>
            </div>
          </div>
        </div>
      {/each}
    {/if}
  </div>
{/if}

<style>
  .header { margin-bottom: 16px; }
  .form-card { margin-bottom: 16px; }
  .form-card h3 { margin-bottom: 12px; }
  .items-list { display: flex; flex-direction: column; gap: 6px; }
  .tag-item { padding: 12px 16px; }
  .color-swatch { width: 24px; height: 24px; border-radius: 50%; border: 2px solid var(--border); }
  .tag-name { font-size: 15px; font-weight: 500; }
  .color-picker { display: flex; gap: 6px; flex-wrap: wrap; }
  .color-dot { width: 28px; height: 28px; border-radius: 50%; border: 2px solid transparent; cursor: pointer; padding: 0; }
  .color-dot.selected { border-color: white; }
  .error-msg { background: #3a1a1a; border: 1px solid var(--red); padding: 12px; border-radius: var(--radius); margin-bottom: 16px; font-size: 14px; }
  .muted { color: var(--text-muted); font-style: italic; }
</style>