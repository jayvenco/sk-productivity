<script>
  let { value = '#262a36', onchange = () => {} } = $props();
  let open = $state(false);

  const COLORS = [
    { name: 'Standaard', hex: '#262a36' },
    { name: 'Oranje', hex: '#ef8354' },
    { name: 'Blauw', hex: '#3b82f6' },
    { name: 'Groen', hex: '#22c55e' },
    { name: 'Rood', hex: '#ef4444' },
    { name: 'Paars', hex: '#a78bfa' },
    { name: 'Roze', hex: '#f472b6' },
    { name: 'Geel', hex: '#eab308' },
    { name: 'Cyaan', hex: '#06b6d4' },
    { name: 'Mint', hex: '#34d399' },
    { name: 'Zalm', hex: '#fb923c' },
    { name: 'Indigo', hex: '#6366f1' },
  ];
</script>

<div class="cp-wrap">
  <button class="cp-swatch" style="background: {value};" onclick={() => open = !open} aria-label="Kleur kiezen" title="Kleur">
    🎨
  </button>
  {#if open}
    <div class="cp-popup" onclick={(e) => e.stopPropagation()}>
      {#each COLORS as c}
        <button
          class="cp-dot"
          class:active={value === c.hex}
          style="background: {c.hex};"
          onclick={() => { value = c.hex; onchange(c.hex); open = false; }}
          title={c.name}
        ></button>
      {/each}
    </div>
  {/if}
</div>

<style>
  .cp-wrap { position: relative; display: inline-block; }
  .cp-swatch {
    width: 28px; height: 28px; border-radius: var(--radius);
    border: 2px solid var(--border); cursor: pointer; padding: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; transition: all 0.15s;
  }
  .cp-swatch:hover { border-color: var(--accent); }
  .cp-popup {
    position: absolute; top: 34px; left: 0; z-index: 50;
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px;
    padding: 8px; background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius); box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  }
  .cp-dot {
    width: 24px; height: 24px; border-radius: 6px; border: 2px solid transparent;
    cursor: pointer; padding: 0; transition: all 0.1s;
  }
  .cp-dot:hover { transform: scale(1.2); }
  .cp-dot.active { border-color: white; }
</style>