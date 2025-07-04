import ThemeToggle from './ThemeToggle';

export default function Navbar() {
  return (
    <nav
      className="
        bg-color-base text-color-contrast
        p-4
      "
    >
      <div className="container mx-auto flex justify-between items-center">
        <span className="text-lg font-semibold">EcoCarpool</span>
        <ThemeToggle />
      </div>
    </nav>
  );
}

