import { GlassCard } from '../common/GlassCard';
import { TreeNode } from './TreeNode';
import { NodeDetails } from './NodeDetails';
import { useStore } from '../../store/useStore';

export function TreeView() {
  const { nodes } = useStore();

  // Get root level nodes (no parent)
  const rootNodes = nodes.filter((n) => !n.parent);

  // Calculate overall progress
  const totalProgress = Math.round(
    nodes.reduce((sum, n) => sum + (n.progress || 0), 0) / nodes.length
  );

  return (
    <GlassCard className="p-6 min-h-[calc(100vh-180px)]">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold">🌳 South Park Episode: "AI Takes Over"</h2>
        <div className="text-sm font-medium text-status-progress">◐ {totalProgress}%</div>
      </div>

      <div className="space-y-2 mb-4">
        {rootNodes.map((node) => (
          <TreeNode key={node.id} node={node} level={0} />
        ))}
      </div>

      <NodeDetails />
    </GlassCard>
  );
}
