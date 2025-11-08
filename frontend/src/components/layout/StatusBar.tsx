import { useStore } from '../../store/useStore';

export function StatusBar() {
  const { activeAgent, nodes, selectedNodeId } = useStore();

  const selectedNode = nodes.find((n) => n.id === selectedNodeId);
  const progressNodes = nodes.filter((n) => n.status === 'progress' || n.status === 'active');

  return (
    <div className="h-6 px-3 bg-bg-secondary border-t border-border-subtle flex items-center justify-between text-[11px] text-text-secondary">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5">
          <div className={`w-1.5 h-1.5 rounded-full ${progressNodes.length > 0 ? 'bg-status-progress animate-pulse' : 'bg-status-completed'}`} />
          <span>
            {progressNodes.length > 0
              ? `${progressNodes.length} ${progressNodes.length === 1 ? 'task' : 'tasks'} running`
              : 'Ready'}
          </span>
        </div>

        {selectedNode && (
          <>
            <div className="w-px h-3 bg-border-subtle" />
            <span className="text-text-tertiary">
              Selected: <span className="text-text-primary">{selectedNode.name}</span>
            </span>
          </>
        )}
      </div>

      <div className="flex items-center gap-4">
        <span className="text-text-tertiary">
          Agent: <span className="text-text-primary">{activeAgent}</span>
        </span>

        <div className="w-px h-3 bg-border-subtle" />

        <button className="hover:text-text-primary transition-colors flex items-center gap-1">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <circle cx="6" cy="6" r="5" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M6 3V6L8 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
          <span>0:23</span>
        </button>
      </div>
    </div>
  );
}
