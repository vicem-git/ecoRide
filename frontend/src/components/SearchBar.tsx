import circleDotEnd from '../assets/icons/circle-dot-end.svg';
import circleDotStart from '../assets/icons/circle-dot-start.svg';

function SearchBar() {
  return (
    <div className='sticky top-28 flex w-[100%] justify-center'>
      <div className="flex flex-row p-6 rounded-xs bg-[var(--color-base2)] h-[72px] gap-3 items-center"
      >
        <div className="flex flex-row rounded-sm bg-[var(--color-base)] h-[48px] gap-2">
          <img src={circleDotStart} width={48} height={48} />
          <input type="text" id="start-point-search"
            className="p-2 rounded-sm focus:ring-2 focus:ring-lime-400 focus:outline-none"
          />
        </div>
        <div className="flex flex-row rounded-sm bg-[var(--color-base)] h-[48px] gap-2">
          <img src={circleDotEnd} width={48} height={48} />
          <input type="text" id="end-point-search"
            className="p-2 rounded-sm focus:ring-2 focus:ring-lime-400 focus:outline-none"
          />
        </div>
        <div className="flex flex-row rounded-sm bg-[var(--color-base)] h-[48px]"
        >
          <input type="date" id="start-date" className="w-full h-full rounded-sm bg-[var(--color-base)] text-[var(--color-contrast)] p-2 rounded-sm focus:ring-2 focus:ring-lime-400 focus:outline-none" />
        </div>
        <div className="flex flex-row rounded-sm bg-[var(--color-base)] h-[48px]"
        >
          <input type="date" id="end-date" className="w-full h-full rounded-sm bg-[var(--color-base)] text-[var(--color-contrast)] p-2 rounded-sm focus:ring-2 focus:ring-lime-400 focus:outline-none" />
        </div>
      </div>
    </div>
  );
};

export default SearchBar
