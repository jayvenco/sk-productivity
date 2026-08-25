<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let items = $state([]);
  let editing = $state(null);
  let form = $state({ title: '', language: 'text', code: '' });
  let error = $state('');
  let loading = $state(true);

  onMount(async () => {
    try { items = (await api.snippets.list()).items; }
    catch (e) { error = e.message; }
    finally { loading = false; }
  });

  async function save() {
    error = '';
    try {
      if (editing) await api.snippets.update(editing, form);
      else await api.snippets.create(form);
      editing = null;
      form = { title: '', language: 'text', code: '' };
      items = (await api.snippets.list()).items;
    } catch (e) { error = e.message; }
  }

  function edit(item) {
    editing = item.id;
    form = { title: item.title, language: item.language, code: item.code };
  }

  async function remove(id) {
    if (!confirm('Verwijder deze snippet?')) return;
    error = '';
    try {
      await api.snippets.delete(id);
      items = (await api.snippets.list()).items;
    } catch (e) { error = e.message; }
  }

  function cancel() {
    editing = null;
    form = { title: '', language: 'text', code: '' };
  }
</script>

<div class="header">
  <h1>Snippets</h1>
</div>

{#if error}
  <div class="error-msg" role="alert">{error}</div>
{/if}

{#if loading}
  <p class="muted">Laden...</p>
{:else}
  <div class="card form-card">
    <h3>{editing ? 'Bewerk snippet' : 'Nieuwe snippet'}</h3>
    <div class="flex-col gap-2">
      <input bind:value={form.title} placeholder="Titel" aria-label="Titel" />
      <select bind:value={form.language} aria-label="Taal">
        <option value="text">Text</option>
        <option value="python">Python</option>
        <option value="javascript">JavaScript</option>
        <option value="typescript">TypeScript</option>
        <option value="html">HTML</option>
        <option value="css">CSS</option>
        <option value="bash">Bash</option>
        <option value="sql">SQL</option>
        <option value="json">JSON</option>
        <option value="yaml">YAML</option>
        <option value="markdown">Markdown</option>
      </select>
      <textarea bind:value={form.code} placeholder="Code..." rows="6" class="code-input" aria-label="Code"></textarea>
      <div class="flex gap-2">
        <button class="primary" onclick={save}>{editing ? 'Opslaan' : 'Toevoegen'}</button>
        {#if editing}<button class="secondary" onclick={cancel}>Annuleren</button>{/if}
      </div>
    </div>
  </div>

  <div class="items-list">
    {#if items.length === 0}
      <p class="muted">Geen snippets — maak er een aan.</p>
    {:else}
      {#each items as item (item.id)}
        <div class="card item-card">
          <div class="flex justify-between items-center" style="margin-bottom: 8px;">
            <div class="flex items-center gap-2">
              <h3>{item.title}</h3>
              <span class="badge" style="background: #333; color: #aaa;">{item.language}</span>
            </div>
            <div class="flex gap-2">
              <button class="secondary" onclick={() => edit(item)}>Bewerk</button>
              <button class="danger" onclick={() => remove(item.id)}>Verwijder</button>
            </div>
          </div>
          <pre><code>{item.code}</code></pre>
        </div>
      {/each}
    {/if}
  </div>
{/if}

<style>
  .header { margin-bottom: 16px; }
  .form-card { margin-bottom: 16px; }
  .form-card h3 { margin-bottom: 12px; }
  .code-input { font-family: 'SF Mono', 'Fira Code', monospace; }
  .items-list { display: flex; flex-direction: column; gap: 8px; }
  .item-card pre { margin-top: 8px; }
  .error-msg { background: #3a1a1a; border: 1px solid var(--red); padding: 12px; border-radius: var(--radius); margin-bottom: 16px; font-size: 14px; }
  .muted { color: var(--text-muted); font-style: italic; }
</style>