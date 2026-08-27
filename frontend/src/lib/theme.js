const THEME_KEY = 'skp_theme';

export const themes = {
  default: {
    name: 'Default',
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
  ares: {
    name: 'Ares',
    icon: '🔥',
    colors: {
      '--bg': '#1c1e26',
      '--bg-card': '#262a36',
      '--bg-hover': '#2d3142',
      '--border': '#3a3f4b',
      '--text': '#eaeaea',
      '--text-muted': '#9ca8b8',
      '--accent': '#FF4444',
      '--accent-hover': '#CC3333',
      '--green': '#4caf50',
      '--red': '#FF4444',
      '--blue': '#6b7a8f',
    },
  },
  mono: {
    name: 'Mono',
    icon: '⚪',
    colors: {
      '--bg': '#1a1a1a',
      '--bg-card': '#222222',
      '--bg-hover': '#2a2a2a',
      '--border': '#333333',
      '--text': '#e0e0e0',
      '--text-muted': '#888888',
      '--accent': '#CCCCCC',
      '--accent-hover': '#999999',
      '--green': '#888888',
      '--red': '#CC6666',
      '--blue': '#888888',
    },
  },
  slate: {
    name: 'Slate',
    icon: '🌊',
    colors: {
      '--bg': '#1e2028',
      '--bg-card': '#262834',
      '--bg-hover': '#2e3040',
      '--border': '#383a48',
      '--text': '#e2e4f0',
      '--text-muted': '#9498b0',
      '--accent': '#94A3B8',
      '--accent-hover': '#7e8ca0',
      '--green': '#6b8f71',
      '--red': '#c77d7d',
      '--blue': '#7e8ca0',
    },
  },
  poseidon: {
    name: 'Poseidon',
    icon: '🌊',
    colors: {
      '--bg': '#0f1a24',
      '--bg-card': '#162230',
      '--bg-hover': '#1c2b3c',
      '--border': '#24384a',
      '--text': '#dce8f0',
      '--text-muted': '#7a9ab0',
      '--accent': '#0EA5E9',
      '--accent-hover': '#0c8ec9',
      '--green': '#4caf50',
      '--red': '#fc8181',
      '--blue': '#0EA5E9',
    },
  },
  sisyphus: {
    name: 'Sisyphus',
    icon: '💜',
    colors: {
      '--bg': '#1a1624',
      '--bg-card': '#222030',
      '--bg-hover': '#2a2638',
      '--border': '#343048',
      '--text': '#e2dcf0',
      '--text-muted': '#948ab0',
      '--accent': '#A78BFA',
      '--accent-hover': '#8b6ed9',
      '--green': '#6b8f71',
      '--red': '#c77d7d',
      '--blue': '#7e8ca0',
    },
  },
  charizard: {
    name: 'Charizard',
    icon: '🦎',
    colors: {
      '--bg': '#1c1610',
      '--bg-card': '#262018',
      '--bg-hover': '#302820',
      '--border': '#3a3028',
      '--text': '#eae0d6',
      '--text-muted': '#a89888',
      '--accent': '#FB923C',
      '--accent-hover': '#e07e2e',
      '--green': '#6b8f71',
      '--red': '#fc8181',
      '--blue': '#7e8ca0',
    },
  },
};

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
}