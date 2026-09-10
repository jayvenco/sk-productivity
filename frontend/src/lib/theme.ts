const THEME_KEY = 'skp_theme';
const FONT_KEY = 'skp_font';

const themes = {
  '': { name: 'Deep Ocean', icon: '🌑' },
  'apple': { name: 'Apple Light', icon: '☀️' },
};

export function getTheme() {
  if (typeof localStorage === 'undefined') return '';
  return localStorage.getItem(THEME_KEY) || '';
}

export function setTheme(name) {
  if (typeof localStorage !== 'undefined') {
    if (name) localStorage.setItem(THEME_KEY, name);
    else localStorage.removeItem(THEME_KEY);
  }
  applyTheme(name);
}

export function applyTheme(name) {
  if (typeof document === 'undefined') return;
  document.documentElement.classList.remove('theme-apple');
  if (name) document.documentElement.classList.add(`theme-${name}`);
}

export function getFont() {
  if (typeof localStorage === 'undefined') return '';
  return localStorage.getItem(FONT_KEY) || '';
}

export function setFont(name) {
  if (typeof localStorage !== 'undefined') {
    if (name) localStorage.setItem(FONT_KEY, name);
    else localStorage.removeItem(FONT_KEY);
  }
  applyFont(name);
}

export function applyFont(name) {
  if (typeof document === 'undefined') return;
  document.documentElement.style.setProperty('--font-family', name || '');
}

export function getThemes() {
  return Object.entries(themes).map(([id, t]) => ({ id, ...t }));
}