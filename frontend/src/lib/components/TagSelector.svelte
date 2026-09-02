<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let { itemType = 'task', itemId = null } = $props();

  let allTags = $state([]);
  let attached = $state([]);
  let showPicker = $state(false);

  onMount(async () => {
    try { allTags = (await api.tags.list()).items; } catch (e) {}
    if (itemId) await loadAttached();
  });

  async function loadAttached() {
    if (!itemId) return;
    try { attached = await api.tags.getForItem(itemType, itemId); } catch (e) {}
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
</script>

<div class="tag-area">
  <div class="tag-list">
    {#each attached as tag (tag.id)}
      <span class="tag-badge" style="background: {tag.color}22; color: {tag.color}; border: 1px solid {tag.color}44;">
        {tag.name}
        {#if itemId}
          <button class="tag-remove" onclick={() => toggleAttach(tag)} aria-label="Verwijder tag {tag.name}">✕</button>
        {/if}
      </span>
    {/each}
    {#if itemId}
      <button class="tag-add-btn" onclick={() => showPicker = !showPicker}>+</button>
    {/if}
  </div>

  {#if showPicker && itemId}
    <div class="tag-picker card">
      <div class="flex gap-2" style="flex-wrap: wrap;">
        {#each allTags as tag (tag.id)}
          <button
            class="tag-option"
            class:selected={attached.find(t => t.id === tag.id)}
            style="background: {tag.color}22; color: {tag.color}; border: 1px solid {attached.find(t => t.id === tag.id) ? tag.color : tag.color}44;"
            onclick={() => toggleAttach(tag)}
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
  .tag-area { display: flex; flex-direction: column; gap: 6px; }
  .tag-list { display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }
  .tag-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 500;
  }
  .tag-remove {
    background: none;
    border: none;
    color: inherit;
    cursor: pointer;
    font-size: 10px;
    padding: 0 2px;
    opacity: 0.6;
  }
  .tag-remove:hover { opacity: 1; }
  .tag-add-btn {
    background: var(--bg-hover);
    border: 1px dashed var(--border);
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 12px;
    cursor: pointer;
    color: var(--text-muted);
  }
  .tag-picker {
    padding: 12px;
    margin-top: 4px;
  }
  .tag-option {
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
    cursor: pointer;
    font-weight: 500;
  }
  .tag-option.selected { transform: scale(1.05); }
  .muted { color: var(--text-muted); font-size: 12px; font-style: italic; }
</style>