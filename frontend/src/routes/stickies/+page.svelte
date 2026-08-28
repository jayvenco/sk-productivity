<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import TagSelector from '$lib/components/TagSelector.svelte';

  let notes = $state([]);
  let selected = $state(new Set());
  let lastClicked = $state(null);
  let loading = $state(true);
  let error = $state('');
  let dragging = $state(null);
  let dragOffX = $state(0);
  let dragOffY = $state(0);
  let editing = $state(null);
  let editText = $state('');
  let nextZ = $state(0);
  let showColors = $state(null);

  const COLORS = [
    { name: 'Geel', hex: '#fef08a' },
    { name: 'Groen', hex: '#86efac' },
    { name: 'Blauw', hex: '#93c5fd' },
    { name: 'Roze', hex: '#f9a8d4' },
    { name: 'Oranje', hex: '#fdba74' },
    { name: 'Paars', hex: '#c4b5fd' },
    { name: 'Rood', hex: '#fca5a5' },
    { name: 'Mint', hex: '#6ee7b7' },
    { name: 'Wit', hex: '#ffffff' },
  ];

  onMount(async () => {
    try {
      const res = await api.stickies.list();
      notes = res.items || [];
      nextZ = notes.length;
    } catch (e) { error = e.message; }
    finally { loading = false; }
  });

  async function createNote() {
    error = '';
    try {
      const s = await api.stickies.create({
        title: '', content: 'Nieuwe notitie...',
        color: '#fef08a', width: 220, height: 200,
      });
      notes = [s, ...notes];
      nextZ = notes.length;
    } catch (e) { error = e.message; }
  }

  function toggleSelect(id, event) {
    if (event.shiftKey && lastClicked !== null) {
      // Range select
      const all = notes.map(n => n.id);
      const start = all.indexOf(lastClicked);
      const end = all.indexOf(id);
      if (start !== -1 && end !== -1) {
        const [from, to] = start < end ? [start, end] : [end, start];
        for (let i = from; i <= to; i++) selected.add(all[i]);
        selected = new Set(selected);
      }
    } else if (event.ctrlKey || event.metaKey) {
      if (selected.has(id)) selected.delete(id);
      else selected.add(id);
      selected = new Set(selected);
    } else {
      selected = new Set([id]);
    }
    lastClicked = id;
  }

  function deselectAll(e) {
    if (e.target === e.currentTarget) {
      selected = new Set();
      editing = null;
    }
  }

  async function deleteSelected() {
    if (selected.size === 0) return;
    if (!confirm(`${selected.size} notitie(s) verwijderen?`)) return;
    try {
      await api.stickies.bulkDelete([...selected]);
      notes = notes.filter(n => !selected.has(n.id));
      selected = new Set();
    } catch (e) { error = e.message; }
  }

  function startDrag(note, e) {
    if (selected.has(note.id)) {
      // Drag all selected
      dragging = 'all';
    } else {
      dragging = note.id;
      selected = new Set([note.id]);
    }
    dragOffX = e.clientX - note.pos_x;
    dragOffY = e.clientY - note.pos_y;
    window.addEventListener('mousemove', onDrag);
    window.addEventListener('mouseup', endDrag);
  }

  async function onDrag(e) {
    const x = Math.max(0, e.clientX - dragOffX);
    const y = Math.max(0, e.clientY - dragOffY);
    if (dragging === 'all') {
      notes = notes.map(n => selected.has(n.id) ? { ...n, pos_x: x + (n.pos_x - (notes.find(nn => nn.id === [...selected][0])?.pos_x || 0)), pos_y: y + (n.pos_y - (notes.find(nn => nn.id === [...selected][0])?.pos_y || 0)) } : n);
    } else {
      notes = notes.map(n => n.id === dragging ? { ...n, pos_x: x, pos_y: y } : n);
    }
  }

  async function endDrag(e) {
    window.removeEventListener('mousemove', onDrag);
    window.removeEventListener('mouseup', endDrag);
    // Save positions
    for (const id of selected) {
      const note = notes.find(n => n.id === id);
      if (note) {
        await api.stickies.update(id, { pos_x: note.pos_x, pos_y: note.pos_y });
      }
    }
    dragging = null;
  }

  function startEdit(note) {
    editing = note.id;
    editText = note.content;
  }

  async function saveEdit(noteId) {
    await api.stickies.update(noteId, { content: editText });
    notes = notes.map(n => n.id === noteId ? { ...n, content: editText } : n);
    editing = null;
  }

  async function changeColor(noteId, color) {
    await api.stickies.update(noteId, { color });
    notes = notes.map(n => n.id === noteId ? { ...n, color } : n);
    showColors = null;
  }

  function bringToFront(note) {
    nextZ++;
    api.stickies.update(note.id, { z_index: nextZ });
    notes = notes.map(n => n.id === note.id ? { ...n, z_index: nextZ } : n);
  }
</script>

<div class="header">
  <h1>📌 Stickies</h1>
  <div class="flex gap-2">
    {#if selected.size > 0}
      <span class="sel-count">{selected.size} geselecteerd</span>
      <button class="danger" onclick={deleteSelected}>🗑️ Verwijder</button>
    {/if}
    <button class="primary" onclick={createNote}>+ Nieuwe sticky</button>
  </div>
</div>

{#if error}
  <div class="error-msg">{error}</div>
{/if}

<div class="canvas" onclick={deselectAll} role="application" aria-label="Sticky notes canvas">
  {#if loading}
    <p class="muted">Laden...</p>
  {:else if notes.length === 0}
    <p class="muted" style="text-align:center;padding:60px 20px;">Klik "+ Nieuwe sticky" om te beginnen 📌</p>
  {:else}
    {#each notes as note (note.id)}
      <div
        class="sticky"
        class:selected={selected.has(note.id)}
        style="left: {note.pos_x}px; top: {note.pos_y}px; width: {note.width}px; height: {note.height}px; background: {note.color}; z-index: {note.z_index};"
        onclick={(e) => { e.stopPropagation(); toggleSelect(note.id, e); }}
        onmousedown={(e) => { if (e.target.closest('.sticky-actions') || e.target.closest('.sticky-editor')) return; startDrag(note, e); }}
        ondblclick={() => { bringToFront(note); startEdit(note); }}
        role="button"
        tabindex="0"
        aria-label={note.title || 'Sticky note'}
      >
        <div class="sticky-actions">
          <button class="action-btn" onclick={(e) => { e.stopPropagation(); showColors = showColors === note.id ? null : note.id; }} title="Kleur">🎨</button>
          <button class="action-btn" onclick={(e) => { e.stopPropagation(); bringToFront(note); }} title="Naar voren">⬆</button>
          <button class="action-btn" onclick={async (e) => { e.stopPropagation(); await api.stickies.delete(note.id); notes = notes.filter(n => n.id !== note.id); selected.delete(note.id); selected = new Set(selected); }} title="Verwijder">✕</button>
        </div>

        {#if showColors === note.id}
          <div class="color-picker" onclick={(e) => e.stopPropagation()}>
            {#each COLORS as c}
              <button class="color-swatch" style="background:{c.hex}" onclick={() => changeColor(note.id, c.hex)} title={c.name}></button>
            {/each}
          </div>
        {/if}

        {#if editing === note.id}
          <div class="sticky-editor" onclick={(e) => e.stopPropagation()}>
            <textarea bind:value={editText} class="sticky-textarea" autofocus></textarea>
            <div class="flex gap-2" style="margin-top: 6px;">
              <button class="primary small" onclick={() => saveEdit(note.id)}>Opslaan</button>
              <button class="secondary small" onclick={() => editing = null}>Annuleren</button>
            </div>
          </div>
        {:else}
          <div class="sticky-content">
            {note.content}
            <div class="sticky-tags">
              <TagSelector itemType="stickie" itemId={note.id} />
            </div>
          </div>
        {/if}
      </div>
    {/each}
  {/if}
</div>

<style>
  .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
  .sel-count { font-size: 13px; color: var(--text-muted); align-self: center; }
  .error-msg { background: #3a1a1a; border: 1px solid var(--red); padding: 10px 14px; border-radius: var(--radius); margin-bottom: 16px; font-size: 14px; color: #ff8a80; }
  .muted { color: var(--text-muted); font-size: 14px; }

  .canvas {
    position: relative;
    min-height: calc(100vh - 120px);
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    cursor: default;
  }

  .sticky {
    position: absolute;
    border-radius: 8px;
    padding: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25), 0 1px 3px rgba(0,0,0,0.15);
    cursor: grab;
    transition: box-shadow 0.15s;
    font-size: 13px;
    line-height: 1.5;
    color: #1a1a1a;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .sticky:hover { box-shadow: 0 6px 16px rgba(0,0,0,0.35); }
  .sticky.selected { outline: 3px solid var(--accent); box-shadow: 0 0 0 3px var(--accent), 0 4px 12px rgba(0,0,0,0.3); }
  .sticky:active { cursor: grabbing; }

  .sticky-actions {
    display: flex;
    gap: 4px;
    justify-content: flex-end;
    opacity: 0;
    transition: opacity 0.15s;
    margin-bottom: 4px;
  }
  .sticky:hover .sticky-actions { opacity: 1; }

  .action-btn {
    background: rgba(0,0,0,0.15);
    border: none;
    border-radius: 4px;
    width: 24px; height: 24px;
    font-size: 12px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.15s;
    padding: 0;
  }
  .action-btn:hover { background: rgba(0,0,0,0.3); }

  .color-picker {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    padding: 8px;
    background: rgba(0,0,0,0.08);
    border-radius: 6px;
    margin-bottom: 6px;
  }
  .color-swatch {
    width: 22px; height: 22px;
    border-radius: 50%;
    border: 2px solid transparent;
    cursor: pointer;
    transition: border-color 0.1s;
    padding: 0;
  }
  .color-swatch:hover { border-color: #333; }

  .sticky-content {
    flex: 1;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
    cursor: text;
  }

  .sticky-editor {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  .sticky-textarea {
    flex: 1;
    background: rgba(255,255,255,0.5);
    border: 1px solid rgba(0,0,0,0.15);
    border-radius: 4px;
    padding: 6px;
    font-size: 13px;
    resize: none;
    min-height: 100px;
    color: #1a1a1a;
  }
  button.small { padding: 4px 8px; font-size: 12px; }
</style>