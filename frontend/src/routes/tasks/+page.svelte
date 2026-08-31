<script>
  import { onMount } from 'svelte';
  import { api } from '$lib/api';
  import TagSelector from '$lib/components/TagSelector.svelte';
  import ColorPicker from '$lib/components/ColorPicker.svelte';
  import TagPicker from '$lib/components/TagPicker.svelte';

  let items = $state([]);
  let projects = $state([]);
  let activeProject = $state(null);
  let editing = $state(null);
  let form = $state({ title: '', description: '', due_date: '', color: '#262a36', tagIds: [] });
  let projForm = $state({ name: '', color: '#E44332' });
  let showProjForm = $state(false);
  let error = $state('');
  let loading = $state(true);

  onMount(async () => {
    try {
      const [allItems, allProjs] = await Promise.all([
        api.tasks.list(),
        api.projects.list(),
      ]);
      items = allItems.items;
      projects = allProjs;
    } catch (e) { error = e.message; }
    finally { loading = false; }
  });

  let filtered = $derived(activeProject ? items.filter(i => i.project_id === activeProject) : items);
  let pending = $derived(filtered.filter(i => i.status !== 'completed'));
  let done = $derived(filtered.filter(i => i.status === 'completed'));

  async function save() {
    error = '';
    try {
      const payload = { ...form, project_id: activeProject };
      if (form.due_date) payload.due_date = new Date(form.due_date).toISOString();
      else payload.due_date = null;
      if (editing) await api.tasks.update(editing, payload);
      else {
        const item = await api.tasks.create(payload);
        for (const tid of form.tagIds) {
          await api.tags.attach(tid, 'task', item.id).catch(() => {});
        }
      }
      editing = null;
      form = { title: '', description: '', due_date: '', color: '#262a36', tagIds: [] };
      items = (await api.tasks.list()).items;
    } catch (e) { error = e.message; }
  }

  function edit(item) {
    editing = item.id;
    form = {
      title: item.title, description: item.description,
      due_date: item.due_date ? item.due_date.slice(0, 10) : '',
      color: item.color || '#262a36', tagIds: [],
    };
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
    try { await api.tasks.delete(id); items = (await api.tasks.list()).items; }
    catch (e) { error = e.message; }
  }

  function cancel() {
    editing = null;
    form = { title: '', description: '', due_date: '', color: '#262a36', tagIds: [] };
  }

  async function createProj() {
    if (!projForm.name) return;
    try {
      await api.projects.create(projForm);
      projForm = { name: '', color: '#E44332' };
      showProjForm = false;
      projects = await api.projects.list();
    } catch (e) { error = e.message; }
  }

  async function deleteProj(id) {
    if (!confirm('Verwijder dit project? Taken blijven behouden.')) return;
    try {
      await api.projects.delete(id);
      projects = await api.projects.list();
      if (activeProject === id) activeProject = null;
    } catch (e) { error = e.message; }
  }
</script>

<div class="td-layout">
  <!-- Project Sidebar -->
  <aside class="td-sidebar">
    <div class="td-sidebar-header">
      <h2>📋 Projecten</h2>
      <button class="td-add-proj" onclick={() => showProjForm = !showProjForm} title="Nieuw project">+</button>
    </div>
    {#if showProjForm}
      <div class="td-proj-form">
        <input bind:value={projForm.name} placeholder="Project naam" />
        <div class="flex gap-2" style="margin-top: 4px;">
          <input type="color" bind:value={projForm.color} style="width: 36px; height: 30px; padding: 2px;" />
          <button class="primary small" onclick={createProj}>Maak</button>
        </div>
      </div>
    {/if}
    <div class="td-proj-list">
      <button class="td-proj-item" class:active={activeProject === null} onclick={() => activeProject = null}>
        <span class="td-proj-dot" style="background: #666;"></span>
        <span class="td-proj-name">Alle taken</span>
        <span class="td-proj-count">{items.length}</span>
      </button>
      {#each projects as p}
        <button class="td-proj-item" class:active={activeProject === p.id} onclick={() => activeProject = p.id}>
          <span class="td-proj-dot" style="background: {p.color};"></span>
          <span class="td-proj-name">{p.name}</span>
          <span class="td-proj-count">{items.filter(i => i.project_id === p.id).length}</span>
          <span class="td-proj-del" onclick={(e) => { e.stopPropagation(); deleteProj(p.id); }} title="Verwijder">✕</span>
        </button>
      {/each}
    </div>
    <div class="td-sidebar-footer">
      <span class="muted">Taak: voeg toe met Enter</span>
    </div>
  </aside>

  <!-- Main -->
  <div class="td-main">
    {#if error}
      <div class="error-msg" role="alert">{error}</div>
    {/if}

    {#if loading}
      <p class="muted">Laden...</p>
    {:else}
      <!-- Quick add -->
      <div class="td-quick-add">
        <input
          bind:value={form.title}
          placeholder="Voeg een taak toe..."
          onkeydown={(e) => { if (e.key === 'Enter') save(); }}
          aria-label="Nieuwe taak"
        />
        <button class="td-add-btn" onclick={save}>Toevoegen</button>
      </div>

      <!-- Pending items -->
      <div class="td-section">
        <h3 class="td-section-title">Te doen <span class="td-count">{pending.length}</span></h3>
        {#each pending as item (item.id)}
          <div class="td-item" class:editing-item={editing === item.id} style="border-left-color: {item.color || '#262a36'};">
            {#if editing === item.id}
              <div class="td-edit-form">
                <input bind:value={form.title} placeholder="Titel" />
                <input type="date" bind:value={form.due_date} />
                <textarea bind:value={form.description} placeholder="Beschrijving..." rows="2"></textarea>
                <TagPicker bind:tagIds={form.tagIds} />
                <div class="flex gap-2" style="margin-top: 6px;">
                  <ColorPicker bind:value={form.color} />
                  <button class="primary small" onclick={save}>Opslaan</button>
                  <button class="secondary small" onclick={cancel}>Annuleren</button>
                </div>
              </div>
            {:else}
              <div class="td-item-row" onclick={() => edit(item)}>
                <button class="td-check" onclick={(e) => { e.stopPropagation(); toggleStatus(item); }} aria-label="Voltooien">
                  <span class="td-check-circle"></span>
                </button>
                <div class="td-item-content">
                  <span class="td-item-title">{item.title}</span>
                  {#if item.description}
                    <span class="td-item-desc">{item.description}</span>
                  {/if}
                  <div class="td-item-meta">
                    {#if item.due_date}
                      {@const d = new Date(item.due_date)}
                      {@const today = new Date()}
                      {@const overdue = d < today && item.status !== 'completed'}
                      <span class="td-due" class:overdue>📅 {d.toLocaleDateString('nl-NL', {day:'numeric',month:'short'})}</span>
                    {/if}
                    <TagSelector itemType="task" itemId={item.id} />
                  </div>
                </div>
                <button class="td-del" onclick={(e) => { e.stopPropagation(); remove(item.id); }} title="Verwijder">✕</button>
              </div>
            {/if}
          </div>
        {:else}
          <p class="muted">Geen taken — voeg er een toe!</p>
        {/each}
      </div>

      <!-- Completed -->
      {#if done.length > 0}
        <div class="td-section">
          <h3 class="td-section-title">Voltooid <span class="td-count">{done.length}</span></h3>
          {#each done as item (item.id)}
            <div class="td-item td-done-item" style="border-left-color: {item.color || '#262a36'};">
              <div class="td-item-row">
                <button class="td-check" onclick={() => toggleStatus(item)} aria-label="Heropenen">
                  <span class="td-check-circle td-checked">✓</span>
                </button>
                <div class="td-item-content">
                  <span class="td-item-title done">{item.title}</span>
                </div>
                <button class="td-del" onclick={() => remove(item.id)} title="Verwijder">✕</button>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    {/if}
  </div>
</div>

<style>
  .td-layout { display: flex; gap: 0; min-height: calc(100vh - 100px); margin: -20px; }
  .td-sidebar {
    width: 240px; min-width: 240px; background: var(--bg-card);
    border-right: 1px solid var(--border); padding: 16px 12px;
    display: flex; flex-direction: column; gap: 8px;
  }
  .td-sidebar-header { display: flex; justify-content: space-between; align-items: center; }
  .td-sidebar-header h2 { font-size: 16px; }
  .td-add-proj { background: none; border: none; color: var(--accent); font-size: 20px; cursor: pointer; padding: 0 4px; }
  .td-proj-form { padding: 8px; background: var(--bg); border-radius: var(--radius); }
  .td-proj-list { display: flex; flex-direction: column; gap: 2px; flex: 1; overflow-y: auto; }
  .td-proj-item {
    display: flex; align-items: center; gap: 8px; padding: 8px 10px;
    border-radius: var(--radius); cursor: pointer; transition: all 0.1s;
    background: none; border: none; color: var(--text); font-size: 13px; font-family: inherit; width: 100%; text-align: left;
  }
  .td-proj-item:hover { background: var(--bg-hover); }
  .td-proj-item.active { background: var(--bg-hover); color: var(--accent); font-weight: 600; }
  .td-proj-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
  .td-proj-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .td-proj-count { font-size: 11px; color: var(--text-muted); }
  .td-proj-del { background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 10px; padding: 0; opacity: 0; }
  .td-proj-item:hover .td-proj-del { opacity: 1; }
  .td-proj-del:hover { color: var(--red); }
  .td-sidebar-footer { font-size: 11px; padding-top: 8px; border-top: 1px solid var(--border); }

  .td-main { flex: 1; padding: 20px 24px; max-width: 700px; }

  .td-quick-add { display: flex; gap: 8px; margin-bottom: 20px; }
  .td-quick-add input { flex: 1; padding: 10px 14px; font-size: 14px; border-radius: 8px; }
  .td-add-btn { background: var(--accent); color: white; border: none; border-radius: 8px; padding: 10px 18px; font-size: 14px; cursor: pointer; }

  .td-section { margin-bottom: 20px; }
  .td-section-title { font-size: 13px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; display: flex; align-items: center; gap: 6px; }
  .td-count { font-size: 11px; color: var(--text-muted); font-weight: 400; }

  .td-item { border-left: 3px solid var(--border); margin-bottom: 2px; border-radius: 0 6px 6px 0; }
  .td-item-row { display: flex; align-items: flex-start; gap: 10px; padding: 8px 12px; cursor: pointer; border-radius: 0 6px 6px 0; }
  .td-item-row:hover { background: var(--bg-hover); }

  .td-check { background: none; border: none; cursor: pointer; padding: 2px; flex-shrink: 0; margin-top: 2px; }
  .td-check-circle { display: block; width: 18px; height: 18px; border-radius: 50%; border: 2px solid var(--border); transition: all 0.15s; }
  .td-check:hover .td-check-circle { border-color: var(--accent); }
  .td-checked { background: var(--green); border-color: var(--green); color: white; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; }

  .td-item-content { flex: 1; min-width: 0; }
  .td-item-title { display: block; font-size: 14px; font-weight: 500; color: var(--text); }
  .td-item-desc { display: block; font-size: 12px; color: var(--text-muted); margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .td-item-meta { display: flex; gap: 8px; align-items: center; margin-top: 4px; }
  .td-due { font-size: 11px; color: var(--text-muted); }
  .td-due.overdue { color: var(--red); font-weight: 600; }
  .td-del { background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 12px; padding: 4px; opacity: 0; flex-shrink: 0; }
  .td-item-row:hover .td-del { opacity: 1; }
  .td-del:hover { color: var(--red); }

  .td-edit-form { padding: 12px; display: flex; flex-direction: column; gap: 6px; }
  .editing-item { background: var(--bg-hover); }

  .done { text-decoration: line-through; opacity: 0.6; }
  .error-msg { background: #3a1a1a; border: 1px solid var(--red); padding: 12px; border-radius: var(--radius); margin-bottom: 16px; font-size: 14px; }
  .muted { color: var(--text-muted); font-style: italic; font-size: 13px; }
  button.small { padding: 4px 10px; font-size: 12px; }
</style>