<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import TagSelector from '$lib/components/TagSelector.svelte';
  import TagPicker from '$lib/components/TagPicker.svelte';
  import TextEditor from '$lib/components/TextEditor.svelte';

  let items = $state([]);
  let editing = $state(null);
  let form = $state({ title: '', slug: '', content: '', tagIds: [] });
  let search = $state('');
  let error = $state('');
  let loading = $state(true);

  function renderMarkdown(text) {
    if (!text) return '';
    let h = text
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/^### (.+)$/gm, '<h3>$1</h3>')
      .replace(/^## (.+)$/gm, '<h2>$1</h2>')
      .replace(/^# (.+)$/gm, '<h1>$1</h1>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/~~(.+?)~~/g, '<del>$1</del>')
      .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
      .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
      .replace(/```(.+?)```/gs, '<pre><code>$1</code></pre>')
      .replace(/`(.+?)`/g, '<code>$1</code>')
      .replace(/^[-*] (.+)$/gm, '<span class="bullet">• $1</span><br>')
      .replace(/\n/g, '<br>');
    return h;
  }

  onMount(async () => {
    try { items = (await api.wiki.list()).items; }
    catch (e) { error = e.message; }
    finally { loading = false; }
  });

  async function searchWiki() {
    error = '';
    try { items = (await api.wiki.list(search || undefined)).items; }
    catch (e) { error = e.message; }
  }

  async function save() {
    error = '';
    try {
      if (editing) await api.wiki.update(editing, form);
      else {
        const item = await api.wiki.create(form);
        for (const tid of form.tagIds) {
          await api.tags.attach(tid, 'wiki', item.id).catch(() => {});
        }
      }
      editing = null;
      form = { title: '', slug: '', content: '', tagIds: [] };
      items = (await api.wiki.list()).items;
    } catch (e) { error = e.message; }
  }

  function edit(item) {
    editing = item.id;
    form = { title: item.title, slug: item.slug, content: item.content, tagIds: [] };
  }

  async function remove(id) {
    if (!confirm('Verwijder deze wiki pagina?')) return;
    error = '';
    try {
      await api.wiki.delete(id);
      items = (await api.wiki.list()).items;
    } catch (e) { error = e.message; }
  }

  function cancel() {
    editing = null;
    form = { title: '', slug: '', content: '', tagIds: [] };
  }
</script>

<div class="header">
  <h1>Wiki</h1>
</div>

{#if error}
  <div class="error-msg" role="alert">{error}</div>
{/if}

{#if loading}
  <p class="muted">Laden...</p>
{:else}
  <div class="flex gap-2" style="margin-bottom: 16px;">
    <input bind:value={search} placeholder="Zoeken..." oninput={searchWiki} aria-label="Zoeken" />
  </div>

  <div class="card form-card">
    <h3>{editing ? 'Bewerk pagina' : 'Nieuwe pagina'}</h3>
    <div class="flex-col gap-2">
      <input bind:value={form.title} placeholder="Titel" aria-label="Titel" />
      <input bind:value={form.slug} placeholder="slug-van-pagina" aria-label="Slug" />
      <TextEditor bind:value={form.content} placeholder="Markdown content..." rows={8} />
      <TagPicker bind:tagIds={form.tagIds} />
      <div class="flex gap-2">
        <button class="primary" onclick={save}>{editing ? 'Opslaan' : 'Toevoegen'}</button>
        {#if editing}<button class="secondary" onclick={cancel}>Annuleren</button>{/if}
      </div>
    </div>
  </div>

  <div class="items-list">
    {#if items.length === 0}
      <p class="muted">Geen wiki pagina's{search ? ' voor deze zoekopdracht' : ''}.</p>
    {:else}
      {#each items as item (item.id)}
        <div class="card item-card" onclick={() => edit(item)} role="button" tabindex="0" onkeydown={(e) => e.key === 'Enter' && edit(item)}>
          <div class="flex justify-between items-start" style="gap: 8px;">
            <div>
              <h3>{item.title}</h3>
              <span class="slug">/{item.slug}</span>
              <div class="preview">{@html renderMarkdown(item.content)}</div>
            </div>
            <div class="card-actions" onclick={(e) => e.stopPropagation()}>
              <button class="danger small" onclick={() => remove(item.id)} title="Verwijder">✕</button>
            </div>
          </div>
          <div class="card-footer">
            <TagSelector itemType="wiki" itemId={item.id} />
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
  .items-list { display: flex; flex-direction: column; gap: 8px; }
  .item-card { cursor: pointer; transition: all 0.15s; }
  .item-card:hover { border-color: var(--accent); }
  .slug { font-size: 12px; color: var(--text-muted); display: block; margin-bottom: 6px; }
  .preview {
    color: var(--text-muted);
    font-size: 12px;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
    margin-bottom: 8px;
  }
  .preview :global(h1),
  .preview :global(h2),
  .preview :global(h3) { font-size: inherit; font-weight: 600; margin: 4px 0 2px; color: var(--text); }
  .preview :global(blockquote) { border-left: 2px solid var(--accent); padding-left: 8px; margin: 4px 0; opacity: 0.8; }
  .preview :global(pre) { background: #111; border-radius: 4px; padding: 6px 8px; margin: 4px 0; font-size: 11px; overflow-x: auto; }
  .preview :global(code) { background: #111; padding: 1px 4px; border-radius: 3px; font-size: 11px; }
  .preview :global(a) { color: var(--accent); }
  .preview :global(.bullet) { display: block; padding-left: 4px; }
  .card-actions { flex-shrink: 0; }
  .card-footer { margin-top: 8px; }
  .error-msg { background: #3a1a1a; border: 1px solid var(--red); padding: 12px; border-radius: var(--radius); margin-bottom: 16px; font-size: 14px; }
  .muted { color: var(--text-muted); font-style: italic; }
  button.small { padding: 4px 8px; font-size: 11px; }
</style>