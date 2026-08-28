<script>
  let { value = $bindable(''), placeholder = 'Code...', rows = 6 } = $props();

  let lineCount = $derived(value.split('\n').length);
  let textareaEl;
  let gutterEl;

  function syncScroll() {
    if (gutterEl && textareaEl) {
      gutterEl.scrollTop = textareaEl.scrollTop;
    }
  }
</script>

<div class="editor-wrapper">
  <div class="gutter" bind:this={gutterEl}>
    {#each Array(lineCount) as _, i}
      <span class="line-nr">{i + 1}</span>
    {/each}
  </div>
  <textarea
    bind:this={textareaEl}
    {placeholder}
    {rows}
    bind:value
    onscroll={syncScroll}
    class="code-area"
    spellcheck="false"
    aria-label="Code editor"
  ></textarea>
</div>

<style>
  .editor-wrapper {
    display: flex;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    background: #111;
    font-family: 'SF Mono', 'Fira Code', 'Cascadia Code', 'JetBrains Mono', monospace;
    font-size: 13px;
    line-height: 1.5;
  }

  .gutter {
    flex-shrink: 0;
    padding: 7px 0;
    min-width: 36px;
    text-align: right;
    background: #161616;
    border-right: 1px solid var(--border);
    user-select: none;
    overflow: hidden;
  }

  .line-nr {
    display: block;
    padding: 0 8px 0 4px;
    color: #555;
    font-size: 12px;
    line-height: 1.5;
  }

  .code-area {
    flex: 1;
    padding: 7px 10px;
    background: transparent;
    border: none;
    color: var(--text);
    font-family: inherit;
    font-size: inherit;
    line-height: inherit;
    resize: vertical;
    min-height: 120px;
    outline: none;
    tab-size: 2;
    white-space: pre;
    overflow-wrap: normal;
    overflow-x: auto;
  }

  .code-area::placeholder {
    color: var(--text-muted);
    opacity: 0.5;
  }
</style>