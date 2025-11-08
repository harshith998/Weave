import { motion } from 'framer-motion';
import { useStore } from '../../store/useStore';

export function NodeDetails() {
  const { selectedNodeId, nodes } = useStore();

  if (!selectedNodeId) return null;

  const node = nodes.find((n) => n.id === selectedNodeId);
  if (!node) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="mt-6 p-5 glass-card rounded-xl"
      style={{ background: 'rgba(37, 37, 40, 0.8)', backdropFilter: 'blur(16px)' }}
    >
      <div className="flex items-center gap-3 mb-4">
        <span className="text-xl">🎬</span>
        <h3 className="text-lg font-semibold">
          {node.name === 'Scene 1 Agent' ? 'Scene 1: Cafe Interior' : node.name}
        </h3>
      </div>

      {node.metadata?.workingOn && (
        <div className="mb-3">
          <div className="text-xs text-text-tertiary uppercase tracking-wide mb-1">Working:</div>
          <div className="text-sm text-text-primary">{node.metadata.workingOn}</div>
        </div>
      )}

      {node.progress !== undefined && (
        <div className="mb-4">
          <div className="h-2 bg-status-active/20 rounded-full overflow-hidden mb-2">
            <motion.div
              className="h-full bg-gradient-to-r from-status-active to-status-pending rounded-full relative"
              initial={{ width: 0 }}
              animate={{ width: `${node.progress}%` }}
              transition={{ duration: 0.5 }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
            </motion.div>
          </div>

          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-status-active">{node.progress}%</span>
            {node.metadata?.lastUpdate && (
              <span className="text-text-secondary">Last update: {node.metadata.lastUpdate}</span>
            )}
          </div>
        </div>
      )}

      <div className="w-full h-48 bg-bg-primary rounded-lg border border-border-subtle flex flex-col items-center justify-center gap-3">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none" className="text-text-tertiary">
          <rect x="8" y="14" width="32" height="20" rx="2" stroke="currentColor" strokeWidth="2"/>
          <path d="M20 22L28 26L20 30V22Z" fill="currentColor"/>
        </svg>
        <span className="text-sm text-text-secondary">Generating preview...</span>
      </div>
    </motion.div>
  );
}
