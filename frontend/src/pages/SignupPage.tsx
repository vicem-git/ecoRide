import Logo from '../assets/logos/ecoride-logo-2.svg'
import Logo2 from '../assets/logos/ecoride.svg';
import ThemeToggle from '../components/ThemeToggle';
import SignupForm from '../components/SignupForm';
import toast from 'react-hot-toast';

function SignupPage() {
  return (
    <div className='flex flex-col min-h-screen bg-[var(--color-base)] justify-center items-center'>
      <div className='fixed top-4 flex w-[60%]'>
        <nav
          className="flex flex-row p-8 rounded-xs bg-[var(--color-base2)] text-[var(--color-contrast)] h-[92px] w-[100%] justify-between items-center">
          <div className="flex flex-row items-center">
            <img src={Logo} alt="EcoCarpool Logo" className="h-16 w-16 mr-2" />
            <img src={Logo2} alt="EcoCarpool Logo" className="h-16 mr-2" />
          </div>
          <div className="flex flex-row items-center gap-4">
            <ThemeToggle />
          </div>
        </nav >
      </div>
      <div>
        <SignupForm />
      </div>
    </div>
  )
}

export default SignupPage
