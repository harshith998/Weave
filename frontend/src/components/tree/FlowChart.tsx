import { useCallback, useEffect } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  type Node,
  type Edge,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useStore } from '../../store/useStore';
import type { TreeNode } from '../../types';

// Custom node component for our tree nodes
function CustomNode({ data }: { data: any }) {
  const status = data.status;

  let bgColor = '#252528';
  let borderColor = '#6B7280';
  let textColor = '#EEEFF1';

  switch (status) {
    case 'completed':
      borderColor = '#10B981';
      break;
    case 'progress':
      borderColor = '#F59E0B';
      break;
    case 'active':
      borderColor = '#8B5CF6';
      bgColor = '#8B5CF6';
      textColor = '#FFFFFF';
      break;
    case 'pending':
      borderColor = '#3B82F6';
      bgColor = '#1A1A1D';
      break;
  }

  return (
    <div
      style={{
        padding: '12px 16px',
        borderRadius: '6px',
        border: `2px solid ${borderColor}`,
        background: bgColor,
        color: textColor,
        minWidth: '160px',
        fontSize: '14px',
        fontWeight: 500,
      }}
    >
      <div>{data.label}</div>
      {data.progress !== undefined && data.progress > 0 && (
        <div
          style={{
            marginTop: '6px',
            height: '4px',
            background: 'rgba(255,255,255,0.1)',
            borderRadius: '2px',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${data.progress}%`,
              height: '100%',
              background: borderColor,
              borderRadius: '2px',
            }}
          />
        </div>
      )}
    </div>
  );
}

const nodeTypes = {
  custom: CustomNode,
};

// Convert tree structure to ReactFlow nodes and edges
function treeToFlow(nodes: TreeNode[]): { nodes: Node[]; edges: Edge[] } {
  const flowNodes: Node[] = [];
  const flowEdges: Edge[] = [];

  // Layout configuration
  const horizontalSpacing = 280;
  const verticalSpacing = 120;

  // Build a map of children by parent ID
  const childrenMap = new Map<string, TreeNode[]>();
  nodes.forEach((node) => {
    if (node.parent) {
      if (!childrenMap.has(node.parent)) {
        childrenMap.set(node.parent, []);
      }
      childrenMap.get(node.parent)!.push(node);
    }
  });

  // Track vertical position for each level
  let nodeCounter = 0;

  // Build flow nodes with positioning
  const layoutNode = (node: TreeNode, level: number, yOffset: number = 0): number => {
    const x = level * horizontalSpacing;
    const y = nodeCounter * verticalSpacing;

    flowNodes.push({
      id: node.id,
      type: 'custom',
      position: { x, y },
      data: {
        label: node.name,
        status: node.status,
        progress: node.progress,
      },
    });

    nodeCounter++;

    // Process children (both from children array and from parent relationships)
    let children: TreeNode[] = [];

    // First check if node has children array
    if (node.children && node.children.length > 0) {
      children = node.children;
    } else if (childrenMap.has(node.id)) {
      // Otherwise check the children map
      children = childrenMap.get(node.id)!;
    }

    let maxY = y;
    children.forEach((child) => {
      flowEdges.push({
        id: `${node.id}-${child.id}`,
        source: node.id,
        target: child.id,
        type: 'smoothstep',
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: '#6B7280',
        },
        style: { stroke: '#6B7280', strokeWidth: 2 },
      });

      const childMaxY = layoutNode(child, level + 1, maxY);
      maxY = Math.max(maxY, childMaxY);
    });

    return maxY;
  };

  // Process root nodes
  const rootNodes = nodes.filter((n) => !n.parent);
  rootNodes.forEach((node) => {
    layoutNode(node, 0, 0);
  });

  return { nodes: flowNodes, edges: flowEdges };
}

export function FlowChart() {
  const { nodes: treeNodes, setSelectedNode } = useStore();
  const { nodes: flowNodesData, edges: flowEdgesData } = treeToFlow(treeNodes);

  const [nodes, setNodes, onNodesChange] = useNodesState(flowNodesData);
  const [edges, setEdges, onEdgesChange] = useEdgesState(flowEdgesData);

  // Update nodes and edges when tree data changes
  useEffect(() => {
    const { nodes: newNodes, edges: newEdges } = treeToFlow(treeNodes);
    setNodes(newNodes);
    setEdges(newEdges);
  }, [treeNodes, setNodes, setEdges]);

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      setSelectedNode(node.id);
    },
    [setSelectedNode]
  );

  return (
    <div className="w-full h-full bg-bg-primary">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
        className="bg-bg-primary"
      >
        <Background color="#2D2D32" gap={16} />
        <Controls className="bg-bg-secondary border-border-subtle" />
        <MiniMap
          nodeColor={(node) => {
            const status = node.data.status;
            switch (status) {
              case 'completed':
                return '#10B981';
              case 'progress':
                return '#F59E0B';
              case 'active':
                return '#8B5CF6';
              case 'pending':
                return '#3B82F6';
              default:
                return '#6B7280';
            }
          }}
          className="bg-bg-secondary border border-border-subtle"
        />
      </ReactFlow>
    </div>
  );
}
