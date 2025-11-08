import { motion } from 'framer-motion';
import { useState } from 'react';
import type { TreeNode as TreeNodeType } from '../../types';
import { useStore } from '../../store/useStore';

interface TreeNodeProps {
  node: TreeNodeType;
  level?: number;
}

export function TreeNode({ node, level = 0 }: TreeNodeProps) {
  const { selectedNodeId, setSelectedNode } = useStore();
  const [showTooltip, setShowTooltip] = useState(false);

  const isSelected = selectedNodeId === node.id;

  const getStatusConfig = (status: TreeNodeType['status']) => {
    switch (status) {
      case 'completed':
        return {
          dotClass: 'bg-status-completed',
          bgClass: 'bg-status-completed/10 border-status-completed/30',
          badge: '✓ 100%',
          badgeClass: 'bg-status-completed/20 text-status-completed',
        };
      case 'progress':
        return {
          dotClass: 'bg-status-progress animate-pulse-slow',
          bgClass: 'bg-status-progress/10 border-status-progress/30',
          badge: `◐ ${node.progress || 0}%`,
          badgeClass: 'bg-status-progress/20 text-status-progress',
        };
      case 'active':
        return {
          dotClass: 'bg-status-active animate-glow',
          bgClass: 'bg-status-active/15 border-status-active/50 shadow-glow-purple',
          badge: '← SELECTED',
          badgeClass: 'bg-status-active/30 text-status-active uppercase text-xs tracking-wide',
        };
      case 'pending':
        return {
          dotClass: 'border-2 border-status-pending bg-transparent',
          bgClass: 'bg-status-pending/5 border-status-pending/20 opacity-70 hover:opacity-100',
          badge: null,
          badgeClass: '',
        };
    }
  };

  const config = getStatusConfig(node.status);
  const marginLeft = level * 24;

  return (
    <>
      <motion.div
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
        style={{ marginLeft: `${marginLeft}px` }}
        className="relative"
      >
        <button
          onClick={() => setSelectedNode(isSelected ? null : node.id)}
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
          className={`w-full mb-2 px-4 py-3 rounded-lg flex items-center gap-3 border transition-all duration-200 hover:translate-x-0.5 ${config.bgClass} ${
            isSelected ? 'ring-2 ring-status-active/20' : ''
          }`}
        >
          <div className={`w-3 h-3 rounded-full flex-shrink-0 ${config.dotClass}`}></div>

          <div className="flex-1 flex items-center gap-2 min-w-0">
            <span className="text-sm font-medium text-text-primary truncate">{node.name}</span>
            {node.status !== 'completed' && node.status !== 'pending' && (
              <span className="text-xs text-text-secondary">{node.status === 'active' ? 'Working...' : 'In Progress'}</span>
            )}
          </div>

          {config.badge && (
            <div className={`px-2 py-0.5 rounded text-xs font-medium ${config.badgeClass}`}>
              {config.badge}
            </div>
          )}
        </button>

        {/* Tooltip */}
        {showTooltip && node.metadata && (node.status === 'progress' || node.status === 'active') && (
          <motion.div
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            className="absolute left-full top-0 ml-4 p-3 min-w-[200px] glass-card rounded-lg z-50 pointer-events-none"
            style={{ backdropFilter: 'blur(16px)', background: 'rgba(37, 37, 40, 0.95)' }}
          >
            <div className="text-xs text-text-tertiary mb-1">Working on:</div>
            <div className="text-sm text-text-primary mb-2">{node.metadata.workingOn}</div>
            <div className="flex gap-4 text-xs text-text-secondary">
              <span>Progress: {node.progress}%</span>
              {node.metadata.estimatedTime && <span>Est: {node.metadata.estimatedTime}</span>}
              {node.metadata.lastUpdate && <span>{node.metadata.lastUpdate}</span>}
            </div>
          </motion.div>
        )}
      </motion.div>

      {/* Children nodes */}
      {node.children?.map((child) => (
        <div key={child.id} className="relative">
          {level > 0 && (
            <div
              className="absolute left-0 top-0 bottom-0 w-px bg-border-subtle"
              style={{ marginLeft: `${marginLeft + 12}px` }}
            />
          )}
          <div style={{ marginLeft: `${marginLeft + 24}px` }} className="relative">
            <span className="absolute left-0 top-4 text-text-tertiary text-xs" style={{ marginLeft: '-16px' }}>
              {node.children?.indexOf(child) === node.children.length - 1 ? '└─' : '├─'}
            </span>
            {child.progress !== undefined && child.progress > 0 ? (
              <div className="mb-2 px-4 py-2 rounded-lg bg-bg-secondary/40 flex items-center gap-3">
                <div className="w-2 h-2 rounded-full border-2 border-status-pending"></div>
                <span className="text-sm text-text-primary flex-1">{child.name}</span>
                <div className="w-16 h-1 bg-status-pending/20 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-status-pending to-status-active rounded-full relative"
                    initial={{ width: 0 }}
                    animate={{ width: `${child.progress}%` }}
                    transition={{ duration: 0.5 }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
                  </motion.div>
                </div>
              </div>
            ) : (
              <div className="mb-2 px-4 py-2 rounded-lg hover:bg-bg-secondary/20 flex items-center gap-3 transition-colors cursor-pointer">
                <div className="w-2 h-2 rounded-full border-2 border-status-pending"></div>
                <span className="text-sm text-text-primary">{child.name}</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </>
  );
}
