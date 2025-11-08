import { useCallback, useEffect } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  Position,
  Handle,
  type Node,
  type Edge,
} from 'reactflow';
import 'reactflow/dist/style.css';
import './FlowChart.css';
import { useStore } from '../../store/useStore';
import type { TreeNode } from '../../types';

// Custom node component for our tree nodes
function CustomNode({ data }: { data: any }) {
  const status = data.status;

  let bgColor = '#1A1A1D';
  let borderColor = '#6B7280';
  let glowColor = 'rgba(107, 114, 128, 0.3)';
  let accentColor = '#6B7280';
  let textColor = '#EEEFF1';

  switch (status) {
    case 'completed':
      borderColor = '#10B981';
      glowColor = 'rgba(16, 185, 129, 0.4)';
      accentColor = '#10B981';
      bgColor = 'linear-gradient(135deg, #1A1A1D 0%, rgba(16, 185, 129, 0.1) 100%)';
      break;
    case 'progress':
      borderColor = '#F59E0B';
      glowColor = 'rgba(245, 158, 11, 0.4)';
      accentColor = '#F59E0B';
      bgColor = 'linear-gradient(135deg, #1A1A1D 0%, rgba(245, 158, 11, 0.15) 100%)';
      break;
    case 'active':
      borderColor = '#8B5CF6';
      glowColor = 'rgba(139, 92, 246, 0.5)';
      accentColor = '#8B5CF6';
      bgColor = 'linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(139, 92, 246, 0.05) 100%)';
      break;
    case 'pending':
      borderColor = '#3B82F6';
      glowColor = 'rgba(59, 130, 246, 0.3)';
      accentColor = '#3B82F6';
      bgColor = 'linear-gradient(135deg, #1A1A1D 0%, rgba(59, 130, 246, 0.08) 100%)';
      break;
  }

  return (
    <div
      style={{
        padding: '8px 12px',
        borderRadius: '8px',
        border: `2px solid ${borderColor}`,
        background: bgColor,
        color: textColor,
        minWidth: '120px',
        maxWidth: '160px',
        fontSize: '11px',
        fontWeight: 600,
        boxShadow: `0 0 15px ${glowColor}, 0 3px 8px rgba(0,0,0,0.3)`,
        position: 'relative',
        transition: 'all 0.3s ease',
      }}
      className="custom-node"
    >
      {/* Connection handles */}
      <Handle
        type="target"
        position={Position.Top}
        style={{ background: borderColor, border: '2px solid #1A1A1D', width: 8, height: 8 }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        style={{ background: borderColor, border: '2px solid #1A1A1D', width: 8, height: 8 }}
      />
      
      {/* Top accent bar */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '2px',
          background: accentColor,
          borderRadius: '8px 8px 0 0',
        }}
      />
      
      <div style={{ lineHeight: '1.3', wordBreak: 'break-word' }}>{data.label}</div>
      
      {data.progress !== undefined && data.progress > 0 && (
        <div
          style={{
            marginTop: '6px',
            height: '4px',
            background: 'rgba(255,255,255,0.08)',
            borderRadius: '2px',
            overflow: 'hidden',
            border: '1px solid rgba(255,255,255,0.1)',
          }}
        >
          <div
            style={{
              width: `${data.progress}%`,
              height: '100%',
              background: `linear-gradient(90deg, ${accentColor} 0%, ${borderColor} 100%)`,
              borderRadius: '2px',
              boxShadow: `0 0 6px ${glowColor}`,
              transition: 'width 0.5s ease',
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

  // Layout configuration - very vertical layout (tight horizontal, tall vertical)
  const horizontalSpacing = 14;
  const verticalSpacing = 480;

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

  // Build flow nodes with positioning - top-down layout
  const layoutNode = (node: TreeNode, level: number, offsetX: number): number => {
    const y = level * verticalSpacing;
    const x = offsetX;

    flowNodes.push({
      id: node.id,
      type: 'custom',
      position: { x, y },
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
      data: {
        label: node.name,
        status: node.status,
        progress: node.progress,
      },
    });

    // Process children (both from children array and from parent relationships)
    let children: TreeNode[] = [];

    // First check if node has children array
    if (node.children && node.children.length > 0) {
      children = node.children;
    } else if (childrenMap.has(node.id)) {
      // Otherwise check the children map
      children = childrenMap.get(node.id)!;
    }

    if (children.length === 0) {
      return x + horizontalSpacing;
    }

    let currentX = offsetX;
    const childStartX = currentX;
    
    children.forEach((child, index) => {
      // Determine edge color based on child status
      let edgeColor = '#6B7280';
      let edgeGlow = 'rgba(107, 114, 128, 0.3)';
      
      switch (child.status) {
        case 'completed':
          edgeColor = '#10B981';
          edgeGlow = 'rgba(16, 185, 129, 0.5)';
          break;
        case 'progress':
          edgeColor = '#F59E0B';
          edgeGlow = 'rgba(245, 158, 11, 0.5)';
          break;
        case 'active':
          edgeColor = '#8B5CF6';
          edgeGlow = 'rgba(139, 92, 246, 0.6)';
          break;
        case 'pending':
          edgeColor = '#3B82F6';
          edgeGlow = 'rgba(59, 130, 246, 0.4)';
          break;
      }
      
      flowEdges.push({
        id: `${node.id}-${child.id}`,
        source: node.id,
        target: child.id,
        type: 'smoothstep',
        animated: child.status === 'progress' || child.status === 'active',
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: edgeColor,
        },
        style: { 
          stroke: edgeColor, 
          strokeWidth: 3,
          filter: `drop-shadow(0 0 4px ${edgeGlow})`,
        },
      });

      currentX = layoutNode(child, level + 1, currentX);
    });

    // Center parent above children
    const childEndX = currentX;
    const parentCenterX = childStartX + (childEndX - childStartX - horizontalSpacing) / 2;
    flowNodes.find(n => n.id === node.id)!.position.x = parentCenterX;

    return currentX;
  };

  // Process root nodes - arrange them horizontally at the top
  const rootNodes = nodes.filter((n) => !n.parent);
  
  // Calculate total width needed for root nodes
  const totalRootWidth = rootNodes.length * horizontalSpacing;
  const startX = -totalRootWidth / 2;
  
  let currentX = startX;
  rootNodes.forEach((node, index) => {
    currentX = layoutNode(node, 0, currentX);
    if (index < rootNodes.length - 1) {
      currentX += horizontalSpacing * 0.5; // Reduced spacing between root trees
    }
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
        <Background 
          color="rgba(139, 92, 246, 0.15)" 
          gap={20} 
          size={1.5}
          style={{ backgroundColor: '#1A1A1D' }}
        />
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
