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
</script>

<div class="tp-wrap">
  <div class="tp-tags">
    {#each allTags.filter(t => tagIds.includes(t.id)) as tag}
      <span class="tp-badge" style="background: {tag.color}22; color: {tag.color}; border: 1px solid {tag.color}44;">
        {tag.name}
        <button class="tp-remove" onclick={() => toggle(tag)} aria-label="Verwijder {tag.name}">✕</button>
      </span>
    {/each}
    <button class="tp-add" onclick={() => open = !open} aria-label="Tags toevoegen">
      {tagIds.length > 0 ? '+ Tag' : '+ Tags'}
    </button>
  </div>
  {#if open}
    <div class="tp-picker card">
      <div class="flex gap-2" style="flex-wrap: wrap;">
        {#each allTags as tag}
          <button
            class="tp-opt"
            class:selected={tagIds.includes(tag.id)}
            style="background: {tag.color}22; color: {tag.color}; border: 1px solid {tagIds.includes(tag.id) ? tag.color : tag.color}44;"
            onclick={() => toggle(tag)}
          >
            {tag.name}
          </button>
        {/each}
      </div>
      {#if allTags.length === 0}
        <p class="muted">Maak eerst tags aan op de Tags pagina 🏷️</p>
      {/if}
    </div>
  {/if}
</div>

<style>
  .tp-wrap { display: flex; flex-direction: column; gap: 6px; }
  .tp-tags { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }
  .tp-badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 2px 8px; border-radius: 6px; font-size: 11px; font-weight: 500;
  }
  .tp-remove { background: none; border: none; color: inherit; cursor: pointer; font-size: 10px; padding: 0 2px; opacity: 0.6; }
  .tp-remove:hover { opacity: 1; }
  .tp-add {
    background: var(--bg-hover); border: 1px dashed var(--border);
    border-radius: 6px; padding: 2px 10px; font-size: 12px;
    cursor: pointer; color: var(--text-muted); font-family: inherit;
  }
  .tp-add:hover { color: var(--text); }
  .tp-picker { padding: 12px; margin-top: 4px; }
  .tp-opt {
    padding: 4px 10px; border-radius: 6px; font-size: 11px;
    cursor: pointer; font-weight: 500; transition: all 0.1s;
  }
  .tp-opt.selected { transform: scale(1.05); }
  .muted { color: var(--text-muted); font-size: 12px; font-style: italic; }
</style>