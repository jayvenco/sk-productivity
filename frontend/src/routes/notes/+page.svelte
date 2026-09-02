<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import TagSelector from '$lib/components/TagSelector.svelte';
  import ColorPicker from '$lib/components/ColorPicker.svelte';
  import TextEditor from '$lib/components/TextEditor.svelte';
  import TagPicker from '$lib/components/TagPicker.svelte';

  let items = $state([]);
  let editing = $state(null);
  let form = $state({ title: '', content: '', color: '#262a36', tagIds: [] });
  let showForm = $state(false);
  let error = $state('');
  let loading = $state(true);

  function openNew() {
    showForm = true;
    editing = null;
    form = { title: '', content: '', color: '#262a36', tagIds: [] };
  }

  function renderMarkdown(text) {
    if (!text) return '';
    let h = text
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      // Headers
      .replace(/^### (.+)$/gm, '<h3>$1</h3>')
      .replace(/^## (.+)$/gm, '<h2>$1</h2>')
      .replace(/^# (.+)$/gm, '<h1>$1</h1>')
      // Bold, italic, strikethrough
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/~~(.+?)~~/g, '<del>$1</del>')
      // Links
      .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
      // Quotes
      .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
      // Code blocks
      .replace(/```(.+?)```/gs, '<pre><code>$1</code></pre>')
      // Inline code
      .replace(/`(.+?)`/g, '<code>$1</code>')
      // Bullets
      .replace(/^[-*] (.+)$/gm, '<span class="bullet">• $1</span><br>')
      // Line breaks
      .replace(/\n/g, '<br>');
    return h;
  }

  onMount(async () => {
    try { items = (await api.notes.list()).items; }
    catch (e) { error = e.message; }
    finally { loading = false; }
  });

  async function save() {
    error = '';
    try {
      if (editing) await api.notes.update(editing, form);
      else {
        const item = await api.notes.create(form);
        for (const tid of form.tagIds) {
          await api.tags.attach(tid, 'note', item.id).catch(() => {});
        }
      }
      editing = null;
      form = { title: '', content: '', color: '#262a36', tagIds: [] };
      showForm = false;
      items = (await api.notes.list()).items;
    } catch (e) { error = e.message; }
  }

  function edit(item) {
    editing = item.id;
    form = { title: item.title, content: item.content, color: item.color || '#262a36', tagIds: [] };
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
    showForm = false;
    form = { title: '', content: '', color: '#262a36', tagIds: [] };
  }
</script>

<div class="header">
  <h1>Notities</h1>
  <button class="primary" onclick={openNew}>+ Nieuwe notitie</button>
</div>

{#if error}
  <div class="error-msg" role="alert">{error}</div>
{/if}

{#if loading}
  <p class="muted">Laden...</p>
{:else}
  {#if showForm || editing}
  <div class="card form-card">
    <h3>{editing ? 'Bewerk notitie' : 'Nieuwe notitie'}</h3>
    <div class="flex-col gap-2">
      <input bind:value={form.title} placeholder="Titel" aria-label="Titel" />
      <TextEditor bind:value={form.content} placeholder="Schrijf hier..." rows={6} />
      <TagPicker bind:tagIds={form.tagIds} />
      <div class="flex gap-2 items-center">
        <ColorPicker bind:value={form.color} />
        <button class="primary" onclick={save}>{editing ? 'Opslaan' : 'Toevoegen'}</button>
        <button class="secondary" onclick={cancel}>Annuleren</button>
      </div>
    </div>
  </div>
  {/if}

  <div class="items-list">
    {#if items.length === 0}
      <p class="muted">Geen notities — maak er een aan.</p>
    {:else}
      {#each items as item (item.id)}
        <div class="card item-card" class:has-color={item.color && item.color !== '#262a36'} style="border-left-color: {item.color || '#262a36'};" onclick={() => edit(item)} role="button" tabindex="0" onkeydown={(e) => e.key === 'Enter' && edit(item)}>
          <div class="flex justify-between items-start" style="gap: 8px;">
            <div class="card-content">
              <h3>{item.title}</h3>
              <p class="preview">{@html renderMarkdown(item.content)}</p>
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
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin-bottom: 8px;
  }
  .preview :global(h1),
  .preview :global(h2),
  .preview :global(h3) {
    font-size: inherit;
    font-weight: 600;
    margin: 4px 0 2px;
    color: var(--text);
  }
  .preview :global(blockquote) {
    border-left: 2px solid var(--accent);
    padding-left: 8px;
    margin: 4px 0;
    opacity: 0.8;
  }
  .preview :global(pre) {
    background: #111;
    border-radius: 4px;
    padding: 6px 8px;
    margin: 4px 0;
    font-size: 11px;
    overflow-x: auto;
  }
  .preview :global(code) {
    background: #111;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 11px;
  }
  .preview :global(a) {
    color: var(--accent);
  }
  .preview :global(.bullet) {
    display: block;
    padding-left: 4px;
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