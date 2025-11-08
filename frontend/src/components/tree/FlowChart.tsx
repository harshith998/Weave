import { useCallback } from 'react';
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
  const horizontalSpacing = 250;
  const verticalSpacing = 100;

  // Build flow nodes with positioning
  const layoutNode = (node: TreeNode, level: number, index: number, parentIndex: number = 0) => {
    const x = level * horizontalSpacing;
    const y = (index - parentIndex) * verticalSpacing + parentIndex * verticalSpacing;

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

    if (node.children) {
      node.children.forEach((child, childIndex) => {
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

        layoutNode(child, level + 1, flowNodes.length, index);
      });
    }
  };

  // Process root nodes
  const rootNodes = nodes.filter((n) => !n.parent);
  rootNodes.forEach((node, index) => {
    layoutNode(node, 0, index);
  });

  return { nodes: flowNodes, edges: flowEdges };
}

export function FlowChart() {
  const { nodes: treeNodes, setSelectedNode } = useStore();
  const { nodes: flowNodesData, edges: flowEdgesData } = treeToFlow(treeNodes);

  const [nodes, setNodes, onNodesChange] = useNodesState(flowNodesData);
  const [edges, setEdges, onEdgesChange] = useEdgesState(flowEdgesData);

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
