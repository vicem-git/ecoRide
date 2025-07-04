import { create } from 'zustand';

interface ThemeState {
  dark: boolean;
  toggleTheme: () => void;
}

export const useThemeStore = create<ThemeState>((set) => ({
  dark: localStorage.theme === 'dark',
  toggleTheme: () =>
    set((state) => {
      const newDark = !state.dark;
      localStorage.theme = newDark ? 'dark' : 'light';
      document.documentElement.classList.toggle('dark', newDark);
      return { dark: newDark };
    }),
}));
