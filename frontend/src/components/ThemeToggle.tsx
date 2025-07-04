import { Moon, Sun } from 'lucide-react';
import { useThemeStore } from '../state/themeStore';

export default function ThemeToggle() {
  const dark = useThemeStore((state) => state.dark);
  const toggleTheme = useThemeStore((state) => state.toggleTheme);

  return (
    <button
      onClick={toggleTheme}
      className="p2 bg-color-base text-color-contrast hover:bg-color-base2 focus:outline-none"
      aria-label="Toggle theme"
    >
      {dark ?
        <Sun size={24} strokeWidth={1.5} /> :
        <Moon size={24} strokeWidth={1.5} />
      }
    </button>
  );
}
