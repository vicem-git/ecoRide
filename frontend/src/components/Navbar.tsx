import ThemeToggle from '@/components/ThemeToggle';
import SearchButton from '@/components/SearchButton';
import UserButton from '@/components/UserButton';
import Logo from '@/assets/logos/ecoride-logo-2.svg'
import Logo2 from '@/assets/logos/ecoride.svg';

function Navbar() {
  return (
    <div className='fixed top-4 flex w-[60%]'>
      <nav
        className="flex flex-row p-8 rounded-xs bg-[var(--color-base2)] h-[92px] w-[100%] justify-between items-center">
        <div className="flex flex-row items-center">
          <img src={Logo} alt="EcoCarpool Logo" className="h-16 w-16 mr-2" />
          <img src={Logo2} alt="EcoCarpool Logo" className="h-16 mr-2" />
        </div>
        <div className="flex flex-row items-center gap-4">
          <SearchButton />
          <UserButton />
          <ThemeToggle />
        </div>
      </nav >
    </div>
  );
}

export default Navbar;
