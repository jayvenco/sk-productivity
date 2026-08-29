<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';

  let { itemType = 'task', itemId = null } = $props();

  let allTags = $state([]);
  let attached = $state([]);
  let showPicker = $state(false);
  let newTagName = $state('');
  let newTagColor = $state('#4f8cff');

  const colors = ['#4f8cff','#4caf50','#ff9800','#f44336','#9c27b0','#00bcd4','#e91e63','#607d8b','#ff5722','#8bc34a'];

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

  async function createAndAttach() {
    if (!newTagName.trim()) return;
    try {
      const tag = await api.tags.create({ name: newTagName.trim(), color: newTagColor });
      allTags = [...allTags, tag];
      if (itemId) {
        await api.tags.attach(tag.id, itemType, itemId);
        await loadAttached();
      }
      newTagName = '';
      showPicker = false;
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
            style="background: {tag.color}22; color: {tag.color}; border: 1px solid {tag.color}44;"
            onclick={() => toggleAttach(tag)}
          >
            {tag.name}
          </button>
        {/each}
      </div>
      <div class="flex gap-2" style="margin-top: 8px;">
        <input bind:value={newTagName} placeholder="Nieuwe tag..." aria-label="Nieuwe tag naam" />
        <div class="color-options" role="radiogroup" aria-label="Kleur">
          {#each colors as c}
            <button
              class="color-dot"
              class:selected={newTagColor === c}
              style="background: {c};"
              onclick={() => newTagColor = c}
              aria-label={c}
            ></button>
          {/each}
        </div>
        <button class="primary" onclick={createAndAttach}>Maak</button>
      </div>
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
  .color-options { display: flex; gap: 4px; align-items: center; }
  .color-dot {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    border: 2px solid transparent;
    cursor: pointer;
    padding: 0;
  }
  .color-dot.selected { border-color: white; }
</style>