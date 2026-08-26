<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import TagSelector from '$lib/components/TagSelector.svelte';

  let items = $state([]);
  let editing = $state(null);
  let form = $state({ title: '', description: '' });
  let error = $state('');
  let loading = $state(true);

  onMount(async () => {
    try { items = (await api.tasks.list()).items; }
    catch (e) { error = e.message; }
    finally { loading = false; }
  });

  async function save() {
    error = '';
    try {
      if (editing) await api.tasks.update(editing, form);
      else await api.tasks.create(form);
      editing = null;
      form = { title: '', description: '' };
      items = (await api.tasks.list()).items;
    } catch (e) { error = e.message; }
  }

  function edit(item) {
    editing = item.id;
    form = { title: item.title, description: item.description };
  }

  async function toggleStatus(item) {
    error = '';
    try {
      const next = item.status === 'pending' ? 'in_progress' : item.status === 'in_progress' ? 'completed' : 'pending';
      await api.tasks.update(item.id, { status: next });
      items = (await api.tasks.list()).items;
    } catch (e) { error = e.message; }
  }

  async function remove(id) {
    if (!confirm('Verwijder deze taak?')) return;
    error = '';
    try {
      await api.tasks.delete(id);
      items = (await api.tasks.list()).items;
    } catch (e) { error = e.message; }
  }

  async function pomodoroForTask(task) {
    error = '';
    try {
      const data = { session_type: 'focus', duration_minutes: 25, item_type: 'task', item_id: task.id };
      await api.pomodoro.start(data);
    } catch (e) { error = e.message; }
  }

  function cancel() {
    editing = null;
    form = { title: '', description: '' };
  }

  function statusClass(s) {
    return s === 'completed' ? 'badge-completed' : s === 'in_progress' ? 'badge-progress' : 'badge-pending';
  }
</script>

<div class="header">
  <h1>Taken</h1>
</div>

{#if error}
  <div class="error-msg" role="alert">{error}</div>
{/if}

{#if loading}
  <p class="muted">Laden...</p>
{:else}
  <div class="card form-card">
    <h3>{editing ? 'Bewerk taak' : 'Nieuwe taak'}</h3>
    <div class="flex-col gap-2">
      <input bind:value={form.title} placeholder="Titel" aria-label="Titel" />
      <textarea bind:value={form.description} placeholder="Beschrijving..." rows="3" aria-label="Beschrijving"></textarea>
      <div class="flex gap-2">
        <button class="primary" onclick={save}>{editing ? 'Opslaan' : 'Toevoegen'}</button>
        {#if editing}<button class="secondary" onclick={cancel}>Annuleren</button>{/if}
      </div>
    </div>
  </div>

  <div class="items-list">
    {#if items.length === 0}
      <p class="muted">Geen taken — maak er een aan.</p>
    {:else}
      {#each items as item (item.id)}
        <div class="card item-card">
          <div class="flex justify-between items-center">
                      <div class="flex items-center gap-2">
                        <span class={`badge ${statusClass(item.status)}`}>{item.status.replace('_', ' ')}</span>
                        <h3 class={item.status === 'completed' ? 'done' : ''}>{item.title}</h3>
                      </div>
                      <div class="flex gap-2">
                        <button class="secondary" onclick={() => toggleStatus(item)}>Volgende</button>
                        <button class="secondary" onclick={() => edit(item)}>Bewerk</button>
                        <button class="secondary pomo-btn" onclick={() => pomodoroForTask(item)} title="Pomodoro starten">⏱</button>
                        <button class="danger" onclick={() => remove(item.id)}>Verwijder</button>
                      </div>
                    </div>
                    {#if item.description}<p class="description">{item.description}</p>{/if}
                    <div class="item-tags">
                      <TagSelector itemType="task" itemId={item.id} />
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
  .items-list { display: flex; flex-direction: column; gap: 8px; }
  .done { text-decoration: line-through; opacity: 0.6; }
  .description { color: var(--text-muted); margin-top: 8px; font-size: 14px; }
  .error-msg { background: #3a1a1a; border: 1px solid var(--red); padding: 12px; border-radius: var(--radius); margin-bottom: 16px; font-size: 14px; }
  .muted { color: var(--text-muted); font-style: italic; }
  :global(.pomo-btn) { font-size: 16px; padding: 4px 8px; }
  .item-tags { margin-top: 6px; }
</style>