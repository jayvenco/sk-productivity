<script>
  let { value = $bindable(''), placeholder = 'Schrijf hier...', rows = 8 } = $props();

  let textareaEl;
  let linkUrl = $state('');
  let showLinkInput = $state(false);

  function wrap(prefix, suffix = '') {
    const ta = textareaEl;
    if (!ta) return;
    const start = ta.selectionStart;
    const end = ta.selectionEnd;
    const sel = value.slice(start, end) || '';
    const before = value.slice(0, start);
    const after = value.slice(end);
    value = before + prefix + sel + (suffix || prefix) + after;
    // Restore cursor after the wrapped content
    requestAnimationFrame(() => {
      ta.focus();
      const pos = start + prefix.length + sel.length + (suffix || prefix).length;
      ta.setSelectionRange(pos, pos);
    });
  }

  function insert(type) {
    switch (type) {
      case 'h1': wrap('# ', ''); break;
      case 'h2': wrap('## ', ''); break;
      case 'h3': wrap('### ', ''); break;
      case 'bold': wrap('**', '**'); break;
      case 'italic': wrap('*', '*'); break;
      case 'strike': wrap('~~', '~~'); break;
      case 'bullet': wrap('- ', ''); break;
      case 'code': wrap('```\n', '\n```'); break;
      case 'quote': wrap('> ', ''); break;
      case 'link':
        if (!showLinkInput) { showLinkInput = true; return; }
        const url = linkUrl || 'https://';
        wrap('[', `](${url})`);
        linkUrl = '';
        showLinkInput = false;
        break;
    }
  }
</script>

<div class="editor-wrap">
  <div class="toolbar">
    <button class="tb-btn" onclick={() => insert('h1')} title="Kop 1" aria-label="Kop 1"><b>H1</b></button>
    <button class="tb-btn" onclick={() => insert('h2')} title="Kop 2" aria-label="Kop 2"><b>H2</b></button>
    <button class="tb-btn" onclick={() => insert('h3')} title="Kop 3" aria-label="Kop 3"><b>H3</b></button>
    <span class="tb-sep"></span>
    <button class="tb-btn" onclick={() => insert('bold')} title="Vetgedrukt" aria-label="Vet"><b>B</b></button>
    <button class="tb-btn" onclick={() => insert('italic')} title="Cursief" aria-label="Cursief"><i>I</i></button>
    <button class="tb-btn" onclick={() => insert('strike')} title="Doorgestreept" aria-label="Doorgestreept"><s>S</s></button>
    <span class="tb-sep"></span>
    <button class="tb-btn" onclick={() => insert('bullet')} title="Lijst" aria-label="Lijst">•</button>
    <button class="tb-btn" onclick={() => insert('link')} title="Link" aria-label="Link">🔗</button>
    <button class="tb-btn" onclick={() => insert('quote')} title="Citaat" aria-label="Citaat">❝</button>
    <button class="tb-btn" onclick={() => insert('code')} title="Codeblok" aria-label="Codeblok">&lt;/&gt;</button>
  </div>
  {#if showLinkInput}
    <div class="link-input">
      <input bind:value={linkUrl} placeholder="https://..." onkeydown={(e) => { if (e.key === 'Enter') insert('link'); if (e.key === 'Escape') showLinkInput = false; }} autofocus />
      <button class="primary small" onclick={() => insert('link')}>Toevoegen</button>
      <button class="secondary small" onclick={() => showLinkInput = false}>✕</button>
    </div>
  {/if}
  <textarea
    bind:this={textareaEl}
    bind:value
    {placeholder}
    {rows}
    aria-label="Inhoud"
  ></textarea>
</div>

<style>
  .editor-wrap {
    display: flex;
    flex-direction: column;
    gap: 0;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
  }

  .toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 2px;
    padding: 6px 8px;
    background: var(--bg-hover);
    border-bottom: 1px solid var(--border);
    align-items: center;
  }

  .tb-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 30px;
    height: 28px;
    padding: 0 6px;
    background: none;
    border: none;
    border-radius: 4px;
    color: var(--text-muted);
    cursor: pointer;
    font-size: 13px;
    font-family: inherit;
    transition: all 0.1s;
  }

  .tb-btn:hover {
    background: var(--bg-card);
    color: var(--text);
  }

  .tb-btn i { font-style: italic; }
  .tb-btn s { text-decoration: line-through; }
  .tb-btn b { font-weight: 700; }

  .tb-sep {
    width: 1px;
    height: 20px;
    background: var(--border);
    margin: 0 4px;
    flex-shrink: 0;
  }

  .link-input {
    display: flex;
    gap: 6px;
    padding: 6px 8px;
    background: var(--bg);
    border-bottom: 1px solid var(--border);
    align-items: center;
  }

  .link-input input {
    flex: 1;
    padding: 4px 8px;
    font-size: 12px;
    height: 28px;
  }

  .editor-wrap textarea {
    border: none;
    border-radius: 0;
    background: var(--bg-card);
    font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
    font-size: 13px;
    line-height: 1.5;
    resize: vertical;
  }

  .editor-wrap textarea:focus {
    border: none;
    box-shadow: inset 0 0 0 1px var(--accent);
  }

  button.small { padding: 4px 8px; font-size: 11px; }
</style>