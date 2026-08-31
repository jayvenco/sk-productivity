const THEME_KEY = 'skp_theme';
const GRADIENT_KEY = 'skp_gradient';
const BG_IMAGE_KEY = 'skp_bg_image';
const BG_MODE_KEY = 'skp_bg_mode';

export const themes = {
  default: {
    name: 'Deep Ocean',
    icon: '🌅',
    colors: {
      '--bg': '#1c1e26',
      '--bg-card': '#262a36',
      '--bg-hover': '#2d3142',
      '--border': '#3a3f4b',
      '--text': '#eaeaea',
      '--text-muted': '#9ca8b8',
      '--accent': '#ef8354',
      '--accent-hover': '#f09b6e',
      '--green': '#4caf50',
      '--red': '#fc8181',
      '--blue': '#6b7a8f',
    },
  },
  one_dark_pro: {
    name: 'One Dark Pro',
    icon: '🔵',
    colors: {
      '--bg': '#282c34',
      '--bg-card': '#2c313a',
      '--bg-hover': '#353b45',
      '--border': '#3e4452',
      '--text': '#abb2bf',
      '--text-muted': '#7f848e',
      '--accent': '#61afef',
      '--accent-hover': '#528bff',
      '--green': '#98c379',
      '--red': '#e06c75',
      '--blue': '#56b6c2',
    },
  },
  dracula: {
    name: 'Dracula',
    icon: '🧛',
    colors: {
      '--bg': '#282a36',
      '--bg-card': '#2d2f3e',
      '--bg-hover': '#363849',
      '--border': '#414458',
      '--text': '#f8f8f2',
      '--text-muted': '#9898b4',
      '--accent': '#ff79c6',
      '--accent-hover': '#ff92d0',
      '--green': '#50fa7b',
      '--red': '#ff5555',
      '--blue': '#8be9fd',
    },
  },
  github: {
    name: 'GitHub Dark',
    icon: '🐙',
    colors: {
      '--bg': '#0d1117',
      '--bg-card': '#161b22',
      '--bg-hover': '#1c2128',
      '--border': '#30363d',
      '--text': '#e6edf3',
      '--text-muted': '#8b949e',
      '--accent': '#58a6ff',
      '--accent-hover': '#79c0ff',
      '--green': '#3fb950',
      '--red': '#f85149',
      '--blue': '#58a6ff',
    },
  },
  tokyo_night: {
    name: 'Tokyo Night',
    icon: '🌃',
    colors: {
      '--bg': '#1a1b26',
      '--bg-card': '#1f2133',
      '--bg-hover': '#252741',
      '--border': '#32344d',
      '--text': '#a9b1d6',
      '--text-muted': '#787c99',
      '--accent': '#7dcfff',
      '--accent-hover': '#b4f9f8',
      '--green': '#9ece6a',
      '--red': '#f7768e',
      '--blue': '#7aa2f7',
    },
  },
  catppuccin: {
    name: 'Catppuccin',
    icon: '🐱',
    colors: {
      '--bg': '#1e1e2e',
      '--bg-card': '#252537',
      '--bg-hover': '#2e2e44',
      '--border': '#3b3b52',
      '--text': '#cdd6f4',
      '--text-muted': '#9399b2',
      '--accent': '#f5c2e7',
      '--accent-hover': '#f8d5ef',
      '--green': '#a6e3a1',
      '--red': '#f38ba8',
      '--blue': '#89b4fa',
    },
  },
  night_owl: {
    name: 'Night Owl',
    icon: '🦉',
    colors: {
      '--bg': '#011627',
      '--bg-card': '#0b1f33',
      '--bg-hover': '#122d42',
      '--border': '#1d3b53',
      '--text': '#d6deeb',
      '--text-muted': '#7e9cb8',
      '--accent': '#7fdbca',
      '--accent-hover': '#a1e8d9',
      '--green': '#addb67',
      '--red': '#ef5350',
      '--blue': '#82aaff',
    },
  },
  material: {
    name: 'Material',
    icon: '🎨',
    colors: {
      '--bg': '#263238',
      '--bg-card': '#2c3a41',
      '--bg-hover': '#34464d',
      '--border': '#40515a',
      '--text': '#eeffff',
      '--text-muted': '#9aa9b3',
      '--accent': '#80cbc4',
      '--accent-hover': '#a1ddd6',
      '--green': '#c3e88d',
      '--red': '#f07178',
      '--blue': '#82aaff',
    },
  },
  nord: {
    name: 'Nord',
    icon: '❄️',
    colors: {
      '--bg': '#2e3440',
      '--bg-card': '#353b4a',
      '--bg-hover': '#3d4456',
      '--border': '#484f63',
      '--text': '#d8dee9',
      '--text-muted': '#9ca3b8',
      '--accent': '#88c0d0',
      '--accent-hover': '#a7d5e0',
      '--green': '#a3be8c',
      '--red': '#bf616a',
      '--blue': '#81a1c1',
    },
  },
  gruvbox: {
    name: 'Gruvbox',
    icon: '🪵',
    colors: {
      '--bg': '#282828',
      '--bg-card': '#2f2f2f',
      '--bg-hover': '#3a3a3a',
      '--border': '#464646',
      '--text': '#ebdbb2',
      '--text-muted': '#a89984',
      '--accent': '#d79921',
      '--accent-hover': '#e0b03a',
      '--green': '#98971a',
      '--red': '#cc241d',
      '--blue': '#458588',
    },
  },
  ayu: {
    name: 'Ayu Mirage',
    icon: '🌅',
    colors: {
      '--bg': '#1f2430',
      '--bg-card': '#262b38',
      '--bg-hover': '#303545',
      '--border': '#3a4052',
      '--text': '#cbccc6',
      '--text-muted': '#8a9199',
      '--accent': '#ffcc66',
      '--accent-hover': '#ffd580',
      '--green': '#a6cc70',
      '--red': '#f28779',
      '--blue': '#73d0ff',
    },
  },
  todoist: {
    name: 'Todoist',
    icon: '🔴',
    colors: {
      '--bg': '#f5f5f5',
      '--bg-card': '#ffffff',
      '--bg-hover': '#f0f0f0',
      '--border': '#e0e0e0',
      '--text': '#202020',
      '--text-muted': '#808080',
      '--accent': '#E44332',
      '--accent-hover': '#cc3c2d',
      '--green': '#20a87a',
      '--red': '#E44332',
      '--blue': '#246fe0',
    },
  },
};

export const gradients = [
  { name: 'Geen', value: '' },
  { name: 'Eigen afbeelding', value: '__custom__' },
  { name: 'Oranje Vuur', value: 'linear-gradient(135deg, #ef8354 0%, #1c1e26 50%, #1c1e26 100%)' },
  { name: 'Oceaan Blauw', value: 'linear-gradient(135deg, #0ea5e9 0%, #1c1e26 50%, #1c1e26 100%)' },
  { name: 'Zwart', value: 'linear-gradient(135deg, #000000 0%, #1a1a1a 50%, #2a2a2a 100%)' },
  { name: 'Antraciet', value: 'linear-gradient(135deg, #2d2d2d 0%, #1c1e26 50%, #1c1e26 100%)' },
  { name: 'Oranje Zonsondergang', value: 'linear-gradient(135deg, #ff6b35 0%, #1c1e26 50%, #1c1e26 100%)' },
  { name: 'Paars Diep', value: 'linear-gradient(135deg, #a78bfa 0%, #1c1e26 50%, #1c1e26 100%)' },
  { name: 'Azure', value: 'linear-gradient(135deg, #007fff 0%, #1c1e26 50%, #1c1e26 100%)' },
  { name: 'Marine Blauw', value: 'linear-gradient(135deg, #000080 0%, #0a0a2e 50%, #1c1e26 100%)' },
];

export function getTheme() {
  if (typeof localStorage === 'undefined') return 'default';
  return localStorage.getItem(THEME_KEY) || 'default';
}

export function setTheme(name) {
  localStorage.setItem(THEME_KEY, name);
  applyTheme(name);
}

export function applyTheme(name) {
  const theme = themes[name];
  if (!theme) return;
  const root = document.documentElement;
  for (const [key, value] of Object.entries(theme.colors)) {
    root.style.setProperty(key, value);
  }
  applyGradient(getActiveGradient());
}

export function getActiveGradient() {
  if (typeof localStorage === 'undefined') return '';
  const idx = parseInt(localStorage.getItem(GRADIENT_KEY) || '0', 10);
  return idx < gradients.length ? idx : 0;
}

export function setActiveGradient(index) {
  localStorage.setItem(GRADIENT_KEY, String(index));
  applyGradient(index);
}

export function applyGradient(index) {
  const g = gradients[index];
  if (!g || !g.value) {
    document.body.style.background = '';
    document.body.style.backgroundSize = '';
    document.body.style.backgroundAttachment = '';
    return;
  }
  if (g.value === '__custom__') {
    const imgUrl = localStorage.getItem(BG_IMAGE_KEY);
    if (imgUrl) {
      document.body.style.background = `url(${imgUrl}) center/cover fixed`;
    }
    return;
  }
  document.body.style.background = g.value;
  document.body.style.backgroundAttachment = 'fixed';
  document.body.style.backgroundSize = '';
}

export function hasCustomBgImage() {
  return !!localStorage.getItem(BG_IMAGE_KEY);
}

export function setCustomBgImage(url) {
  if (url) {
    localStorage.setItem(BG_IMAGE_KEY, url);
  } else {
    localStorage.removeItem(BG_IMAGE_KEY);
  }
  // Re-apply current gradient to show/hide the image
  applyGradient(getActiveGradient());
}

export function getCustomBgImage() {
  return localStorage.getItem(BG_IMAGE_KEY) || '';
}

// ── Font ───────────────────────────────────────────────────────────

const FONT_KEY = 'skp_font';

export const fonts = [
  { name: 'Standaard', family: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif" },
  { name: 'Inter', family: "'Inter', sans-serif" },
  { name: 'Roboto', family: "'Roboto', sans-serif" },
  { name: 'SF Pro', family: "-apple-system, BlinkMacSystemFont, 'SF Pro', 'SF Pro Text', 'Helvetica Neue', sans-serif" },
  { name: 'IBM Plex Sans', family: "'IBM Plex Sans', sans-serif" },
  { name: 'Manrope', family: "'Manrope', sans-serif" },
  { name: 'Consolas', family: "'Consolas', 'Courier New', monospace" },
];

export function getFont() {
  if (typeof localStorage === 'undefined') return 0;
  const idx = parseInt(localStorage.getItem(FONT_KEY) || '0', 10);
  return idx < fonts.length ? idx : 0;
}

export function setFont(index) {
  localStorage.setItem(FONT_KEY, String(index));
  applyFont(index);
}

export function applyFont(index) {
  const font = fonts[index];
  if (!font) return;
  document.documentElement.style.setProperty('--font-ui', font.family);
  document.body.style.fontFamily = font.family;
}