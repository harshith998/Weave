import { useStore } from '../../store/useStore';

export function ConversationList() {
  const { conversations } = useStore();

  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-text-tertiary uppercase tracking-wide">
          Past Conversations
        </span>
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" className="text-text-tertiary">
          <path d="M3 5L6 8L9 5" stroke="currentColor" strokeWidth="1.5"/>
        </svg>
      </div>

      <button className="w-full h-8 px-2 mb-2 rounded-md hover:bg-status-active/10 transition-colors flex items-center gap-2 text-sm font-medium text-text-secondary hover:text-text-primary">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path d="M7 1V13M1 7H13" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        </svg>
        New Project
      </button>

      <div className="space-y-1">
        {conversations.map((conv) => (
          <button
            key={conv.id}
            className={`w-full h-8 px-2 rounded-md flex items-center gap-2 text-sm transition-colors ${
              conv.active
                ? 'bg-status-active/20 border-l-2 border-status-active'
                : 'hover:bg-status-active/10'
            }`}
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className="text-text-secondary flex-shrink-0">
              <rect x="2" y="2" width="10" height="10" rx="2" stroke="currentColor" strokeWidth="1.5"/>
              <line x1="4" y1="5" x2="10" y2="5" stroke="currentColor" strokeWidth="1.5"/>
            </svg>
            <span className="truncate text-text-primary">{conv.name}</span>
            <span className="ml-auto text-xs text-text-tertiary flex-shrink-0">{conv.lastActivity}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
