import { useState } from 'react';
import { useNavigate } from 'react-router';
import { CircleUser, UserRoundCog, LogIn, UserPlus } from 'lucide-react';


// if not logged in, show login and signup buttons
// if logged in, show profile and logout buttons

function UserButton() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <div className="relative inline-block">
      <button
        className="p-2 flex cursor-pointer rounded-full bg-[var(--color-base2)] hover:bg-[var(--color-base3)] justify-center items-center transition-colors duration-200"
        onClick={() => setOpen(!open)}>
        <CircleUser strokeWidth={1.75} size={32} />
      </button>
      {open && (
        <div className="p-2 absolute flex flex-col rounded-sm gap-2 bg-[var(--color-base2)]">
          <button
            className="p-2 flex flex-row rounded-xs gap-2 bg-[var(--color-base2)] hover:bg-[var(--color-contrast)] transition-colors duration-200"
            onClick={() => {
              navigate('/login');
              setOpen(false);
            }}>
            <LogIn size={24} strokeWidth={1.75} />
            <label className='text-sm'>Login</label>
          </button>
          <button
            className="p-2 flex flex-row rounded-xs gap-2 bg-[var(--color-base2)] hover:bg-[var(--color-contrast)] transition-colors duration-200"
            onClick={() => {
              navigate('/register');
              setOpen(false);
            }}>
            <UserPlus size={24} strokeWidth={1.75} />
            <label className='text-sm'>SignUp</label>
          </button>
        </div>
      )}
    </div>
  );
};

export default UserButton
