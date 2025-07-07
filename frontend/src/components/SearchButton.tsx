import { useState } from 'react';
import { Milestone, Search, CirclePlus } from 'lucide-react';
import { useNavigate } from 'react-router';


function SearchButton() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  return (
    <div className="relative inline-block">
      <button onClick={() => setOpen(!open)}
        className="flex items-center justify-center p-2 rounded-full bg-[var(--color-base2)] hover:bg-[var(--color-base3)] transition-colors duration-200">
        <Milestone strokeWidth={1.75} size={32} />
      </button>
      {open && (
        <div className="p-2 absolute flex flex-col rounded-sm gap-2 bg-[var(--color-base2)]">
          <button
            onClick={() => {
              navigate('/search');
              setOpen(false);
            }}
            className="p-2 flex flex-row rounded-xs gap-2 bg-[var(--color-base2)] hover:bg-[var(--color-base3)] transition-colors duration-200"
          >
            <Search strokeWidth={1.75} size={24} />
            <label className='text-sm'>Search Trips</label>
          </button>

          <button
            onClick={() => {
              navigate('/create-trip');
              setOpen(false);
            }}
            className="p-2 flex flex-row rounded-xs gap-2 bg-[var(--color-base2)] hover:bg-[var(--color-contrast)] transition-colors duration-200"
          >
            <CirclePlus strokeWidth={1.75} size={24} />
            <label className='text-sm'>Create Trip</label>
          </button>
        </div>
      )}
    </div>
  );
};

export default SearchButton;
