import './App.css'
// import Logo from './assets/ecoride-logo-2.svg'
import Navbar from './components/Navbar'
import { useThemeStore } from './state/themeStore'

if (!localStorage.theme) {
  localStorage.theme = 'light';
}

function App() {
  const { dark, toggleTheme } = useThemeStore();

  return (
    <div className="bg-[var(--color-base)] min-h-screen text-[var(--color-contrast)] font-sans">
      <Navbar />

      <main className="p-8">
        <h1 className="text-3xl mb-4">Hello, ecoRide :)</h1>
        <p>this is homepage. toggle navbar and see !</p>
      </main>
    </div >
  )
}

export default App
