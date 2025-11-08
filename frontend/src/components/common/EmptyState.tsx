export function EmptyState() {
  return (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-center max-w-md px-6">
        <div className="mb-6">
          <svg
            width="80"
            height="80"
            viewBox="0 0 80 80"
            fill="none"
            className="mx-auto text-text-tertiary"
          >
            <rect x="15" y="20" width="50" height="40" rx="4" stroke="currentColor" strokeWidth="2" />
            <path d="M30 32L40 42L50 32" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>

        <h2 className="text-xl font-semibold text-text-primary mb-2">
          No project selected
        </h2>

        <p className="text-sm text-text-secondary mb-6">
          Create a new project or select an existing one to get started with AI video generation
        </p>

        <div className="flex flex-col gap-2">
          <button className="w-full h-10 px-4 bg-status-active hover:bg-status-active/90 text-white rounded-md text-sm font-medium transition-colors flex items-center justify-center gap-2">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 3V13M3 8H13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            </svg>
            New Project
          </button>

          <button className="w-full h-10 px-4 bg-bg-secondary hover:bg-bg-tertiary border border-border-subtle rounded-md text-sm font-medium text-text-primary transition-colors">
            Browse Examples
          </button>
        </div>

        <div className="mt-8 pt-6 border-t border-border-subtle">
          <p className="text-xs text-text-tertiary mb-3">Keyboard shortcuts</p>
          <div className="space-y-2 text-xs text-text-secondary">
            <div className="flex items-center justify-between">
              <span>Command palette</span>
              <kbd className="px-2 py-1 bg-bg-secondary border border-border-subtle rounded text-[10px] font-mono">
                ⌘K
              </kbd>
            </div>
            <div className="flex items-center justify-between">
              <span>New project</span>
              <kbd className="px-2 py-1 bg-bg-secondary border border-border-subtle rounded text-[10px] font-mono">
                ⌘N
              </kbd>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
