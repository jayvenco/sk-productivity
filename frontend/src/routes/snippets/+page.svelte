<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let items = $state([]);
  let editing = $state(null);
  let form = $state({ title: '', language: 'text', code: '' });

  onMount(async () => { items = (await api.snippets.list()).items; });

  async function save() {
    if (editing) {
      await api.snippets.update(editing, form);
    } else {
      await api.snippets.create(form);
    }
    editing = null;
    form = { title: '', language: 'text', code: '' };
    items = (await api.snippets.list()).items;
  }

  function edit(item) {
    editing = item.id;
    form = { title: item.title, language: item.language, code: item.code };
  }

  async function remove(id) {
    if (confirm('Verwijder deze snippet?')) {
      await api.snippets.delete(id);
      items = (await api.snippets.list()).items;
    }
  }

  function cancel() {
    editing = null;
    form = { title: '', language: 'text', code: '' };
  }
</script>

<div class="header">
  <h1>Snippets</h1>
</div>

<div class="card form-card">
  <h3>{editing ? 'Bewerk snippet' : 'Nieuwe snippet'}</h3>
  <div class="flex-col gap-2">
    <input bind:value={form.title} placeholder="Titel" />
    <select bind:value={form.language}>
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
    <textarea bind:value={form.code} placeholder="Code..." rows="6" class="code-input"></textarea>
    <div class="flex gap-2">
      <button class="primary" onclick={save}>{editing ? 'Opslaan' : 'Toevoegen'}</button>
      {#if editing}<button class="secondary" onclick={cancel}>Annuleren</button>{/if}
    </div>
  </div>
</div>

<div class="items-list">
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
</div>

<style>
  .header { margin-bottom: 16px; }
  .form-card { margin-bottom: 16px; }
  .form-card h3 { margin-bottom: 12px; }
  .code-input { font-family: 'SF Mono', 'Fira Code', monospace; }
  .items-list { display: flex; flex-direction: column; gap: 8px; }
  .item-card pre { margin-top: 8px; }
</style>