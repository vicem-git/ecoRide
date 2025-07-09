import './App.css'
import Navbar from '@/components/Navbar'
import SearchBar from '@/components/SearchBar'
import HomeBanner from '@/assets/images/pexels-darshan394-1173777.jpg'
import { useState, useEffect } from 'react';

if (!localStorage.theme) {
  localStorage.theme = 'light';
}

function App() {
  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    fetch('/api/time').then(res => res.json()).then(data => {
      setCurrentTime(data.time);
    });
  }, []);

  return (
    <div className='flex flex-col bg-[var(--color-base)] justify-center items-center'>
      <img src={HomeBanner} alt="EcoRide Banner" className="w-full h-[500px] object-cover mb-4" />
      <div className="flex flex-col bg-[var(--color-base)] min-h-screen w-[60%] text-[var(--color-contrast)] font-sans  items-center">
        <Navbar />
        <SearchBar />

        <main className="p-8 h-[1512px]">
          <h1 className="text-3xl mb-4">Hello, ecoRide :)</h1>
          <p>this is homepage. toggle navbar and see !</p>
          <p> you landed here at {new Date(currentTime * 1000).toLocaleString()}</p>
        </main>
      </div >
    </div>
  )
}

export default App
