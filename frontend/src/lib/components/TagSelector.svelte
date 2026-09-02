<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let { itemType = 'task', itemId = null } = $props();

  let allTags = $state([]);
  let attached = $state([]);
  let open = $state(false);

  onMount(async () => {
    try { allTags = (await api.tags.list()).items; } catch {}
    if (itemId) await loadAttached();
  });

  async function loadAttached() {
    if (!itemId) return;
    try { attached = await api.tags.getForItem(itemType, itemId); } catch {}
  }

  async function toggleAttach(tag) {
    try {
      if (attached.find(t => t.id === tag.id)) {
        await api.tags.detach(tag.id, itemType, itemId);
      } else {
        await api.tags.attach(tag.id, itemType, itemId);
      }
      await loadAttached();
    } catch (e) { console.error(e); }
  }

  function close(e) {
    if (!e.target.closest('.td-wrap')) open = false;
  }
</script>

<svelte:window onclick={close} />

<div class="td-wrap">
  <div class="td-tags">
    {#each attached as tag (tag.id)}
      <span class="td-badge" style="background:{tag.color}22; color:{tag.color}; border:1px solid {tag.color}44;">
        {tag.name}
        {#if itemId}
          <button class="td-rm" onclick={() => toggleAttach(tag)} aria-label="Verwijder {tag.name}">✕</button>
        {/if}
      </span>
    {/each}
    {#if itemId}
      <button class="td-btn" onclick={() => open = !open}>
        ⌄
      </button>
    {/if}
  </div>

  {#if open && itemId}
    <div class="td-drop card">
      {#each allTags as tag (tag.id)}
        <button
          class="td-opt"
          class:sel={attached.find(t => t.id === tag.id)}
          onclick={() => toggleAttach(tag)}
        >
          <span class="td-dot" style="background:{tag.color};"></span>
          <span class="td-lbl">{tag.name}</span>
          <span class="td-check">{attached.find(t => t.id === tag.id) ? '✓' : ''}</span>
        </button>
      {/each}
      {#if allTags.length === 0}
        <p class="muted">Maak tags aan op de Tags pagina 🏷️</p>
      {/if}
    </div>
  {/if}
</div>

<style>
  .td-wrap { position: relative; display: inline-block; }
  .td-tags { display: inline-flex; flex-wrap: wrap; gap: 4px; align-items: center; }
  .td-badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 500;
  }
  .td-rm { background: none; border: none; color: inherit; cursor: pointer; font-size: 10px; padding: 0 2px; opacity: 0.6; }
  .td-rm:hover { opacity: 1; }
  .td-btn {
    background: var(--bg-hover); border: 1px solid var(--border);
    border-radius: 6px; padding: 2px 10px; font-size: 11px;
    cursor: pointer; color: var(--text-muted); font-family: inherit; line-height: 1.4;
  }
  .td-btn:hover { color: var(--text); background: var(--bg-card); }
  .td-drop {
    position: absolute; top: 100%; left: 0; z-index: 50; margin-top: 4px;
    padding: 6px; min-width: 180px; max-height: 240px; overflow-y: auto;
    display: flex; flex-direction: column; gap: 2px;
  }
  .td-opt {
    display: flex; align-items: center; gap: 8px; padding: 6px 8px;
    border-radius: 4px; cursor: pointer; transition: all 0.1s;
    background: none; border: none; color: var(--text); font-size: 12px; font-family: inherit; text-align: left; width: 100%;
  }
  .td-opt:hover { background: var(--bg-hover); }
  .td-opt.sel { background: var(--bg-hover); font-weight: 600; }
  .td-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
  .td-lbl { flex: 1; }
  .td-check { font-size: 11px; color: var(--accent); font-weight: 700; }
  .muted { color: var(--text-muted); font-size: 11px; font-style: italic; padding: 6px; }
</style>