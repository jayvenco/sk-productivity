<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let { tagIds = $bindable([]) } = $props();

  let allTags = $state([]);
  let open = $state(false);

  onMount(async () => {
    try { allTags = (await api.tags.list()).items; } catch {}
  });

  function toggle(tag) {
    if (tagIds.includes(tag.id)) {
      tagIds = tagIds.filter(id => id !== tag.id);
    } else {
      tagIds = [...tagIds, tag.id];
    }
  }

  function close(e) {
    if (!e.target.closest('.tp-wrap')) open = false;
  }
</script>

<svelte:window onclick={close} />

<div class="tp-wrap">
  <div class="tp-tags">
    {#each allTags.filter(t => tagIds.includes(t.id)) as tag}
      <span class="tp-badge" style="background:{tag.color}22; color:{tag.color}; border:1px solid {tag.color}44;">
        {tag.name}
        <button class="tp-rm" onclick={() => toggle(tag)} aria-label="Verwijder {tag.name}">✕</button>
      </span>
    {/each}
    <button class="tp-btn" onclick={() => open = !open}>
      {tagIds.length > 0 ? `+ ${tagIds.length}` : '+ Tags'} ⌄
    </button>
  </div>

  {#if open}
    <div class="tp-drop card">
      {#each allTags as tag}
        <button
          class="tp-opt"
          class:sel={tagIds.includes(tag.id)}
          onclick={() => toggle(tag)}
        >
          <span class="tp-dot" style="background:{tag.color};"></span>
          <span class="tp-lbl">{tag.name}</span>
          <span class="tp-check">{tagIds.includes(tag.id) ? '✓' : ''}</span>
        </button>
      {/each}
      {#if allTags.length === 0}
        <p class="muted">Maak eerst tags aan op de Tags pagina 🏷️</p>
      {/if}
    </div>
  {/if}
</div>

<style>
  .tp-wrap { position: relative; display: inline-block; }
  .tp-tags { display: inline-flex; flex-wrap: wrap; gap: 4px; align-items: center; }
  .tp-badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 500;
  }
  .tp-rm { background: none; border: none; color: inherit; cursor: pointer; font-size: 10px; padding: 0 2px; opacity: 0.6; }
  .tp-rm:hover { opacity: 1; }
  .tp-btn {
    background: var(--bg-hover); border: 1px solid var(--border);
    border-radius: 6px; padding: 3px 10px; font-size: 12px;
    cursor: pointer; color: var(--text-muted); font-family: inherit;
  }
  .tp-btn:hover { color: var(--text); background: var(--bg-card); }
  .tp-drop {
    position: absolute; top: 100%; left: 0; z-index: 50; margin-top: 4px;
    padding: 6px; min-width: 200px; max-height: 240px; overflow-y: auto;
    display: flex; flex-direction: column; gap: 2px;
  }
  .tp-opt {
    display: flex; align-items: center; gap: 8px; padding: 6px 8px;
    border-radius: 4px; cursor: pointer; transition: all 0.1s;
    background: none; border: none; color: var(--text); font-size: 12px; font-family: inherit; text-align: left; width: 100%;
  }
  .tp-opt:hover { background: var(--bg-hover); }
  .tp-opt.sel { background: var(--bg-hover); font-weight: 600; }
  .tp-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
  .tp-lbl { flex: 1; }
  .tp-check { font-size: 11px; color: var(--accent); font-weight: 700; }
  .muted { color: var(--text-muted); font-size: 11px; font-style: italic; padding: 6px; }
</style>