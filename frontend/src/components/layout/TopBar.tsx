export function TopBar() {
  return (
    <header className="h-[60px] px-6 border-b border-border-subtle flex items-center justify-between">
      <div className="flex items-center gap-2">
        <span className="text-2xl font-semibold tracking-tight">✱ WEAVE</span>
      </div>

      <div className="flex items-center gap-2">
        <button className="w-9 h-9 rounded-lg hover:bg-bg-tertiary transition-colors flex items-center justify-center text-text-secondary hover:text-text-primary">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <circle cx="10" cy="10" r="9" stroke="currentColor" strokeWidth="2"/>
            <circle cx="10" cy="8" r="3" stroke="currentColor" strokeWidth="2"/>
            <path d="M5 16c0-2.5 2-4 5-4s5 1.5 5 4" stroke="currentColor" strokeWidth="2"/>
          </svg>
        </button>

        <button className="w-9 h-9 rounded-lg hover:bg-bg-tertiary transition-colors flex items-center justify-center text-text-secondary hover:text-text-primary">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <circle cx="10" cy="10" r="2" fill="currentColor"/>
            <circle cx="10" cy="4" r="2" fill="currentColor"/>
            <circle cx="10" cy="16" r="2" fill="currentColor"/>
          </svg>
        </button>

        <button className="px-3 h-9 rounded-lg hover:bg-bg-tertiary transition-colors text-sm font-medium text-text-secondary hover:text-text-primary">
          Sign Out
        </button>
      </div>
    </header>
  );
}
