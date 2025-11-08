import { create } from 'zustand';
import type { TreeNode, ChatMessage, Conversation, Tab, Agent } from '../types';

interface WeaveStore {
  // Tree state
  nodes: TreeNode[];
  selectedNodeId: string | null;
  setSelectedNode: (id: string | null) => void;

  // Chat state
  messages: ChatMessage[];
  addMessage: (message: Omit<ChatMessage, 'id' | 'timestamp'>) => void;

  // UI state
  activeTab: Tab;
  setActiveTab: (tab: Tab) => void;

  activeAgent: Agent;
  setActiveAgent: (agent: Agent) => void;

  conversations: Conversation[];
}

// Mock data for initial state
const mockNodes: TreeNode[] = [
  {
    id: 'root',
    name: 'Main Goal',
    status: 'completed',
    progress: 100,
  },
  {
    id: 'character',
    name: 'Character Agent',
    status: 'progress',
    progress: 67,
    parent: 'root',
    metadata: {
      workingOn: 'Voice profile generation',
      estimatedTime: '2m 34s',
    },
    children: [
      {
        id: 'voice',
        name: 'Voice Profile',
        status: 'progress',
        progress: 80,
        parent: 'character',
      },
      {
        id: 'appearance',
        name: 'Appearance',
        status: 'pending',
        parent: 'character',
      },
    ],
  },
  {
    id: 'scene1',
    name: 'Scene 1 Agent',
    status: 'active',
    progress: 85,
    parent: 'root',
    metadata: {
      workingOn: 'Adjusting warm lighting filter',
      lastUpdate: '2s ago',
    },
    children: [
      {
        id: 'lighting',
        name: 'Lighting',
        status: 'progress',
        progress: 85,
        parent: 'scene1',
      },
      {
        id: 'camera',
        name: 'Camera Angles',
        status: 'pending',
        parent: 'scene1',
      },
    ],
  },
  {
    id: 'scene2',
    name: 'Scene 2 Agent',
    status: 'pending',
    parent: 'root',
  },
];

// Cursor-style messages with thinking, actions, and code output
const mockMessages: ChatMessage[] = [
  {
    id: '1',
    type: 'user',
    content: 'Create a South Park style episode about AI taking over a small town',
    timestamp: new Date(Date.now() - 10000),
  },
  {
    id: '2',
    type: 'thinking',
    content: 'Planning scene breakdown and character generation',
    timestamp: new Date(Date.now() - 9800),
    thinkingTime: '2s',
  },
  {
    id: '3',
    type: 'action',
    content: 'Read character_templates.json',
    timestamp: new Date(Date.now() - 9500),
  },
  {
    id: '4',
    type: 'action',
    content: 'Read scene_generator.py',
    timestamp: new Date(Date.now() - 9300),
  },
  {
    id: '5',
    type: 'agent',
    content: "Perfect! I'm generating the character profiles and scene breakdown. The tree view shows the generation progress in real-time.",
    timestamp: new Date(Date.now() - 9000),
  },
  {
    id: '6',
    type: 'user',
    content: 'Make the lighting warmer in scene 1',
    timestamp: new Date(Date.now() - 5000),
    nodeContext: 'scene1',
  },
  {
    id: '7',
    type: 'thinking',
    content: 'Analyzing current lighting settings',
    timestamp: new Date(Date.now() - 4800),
    thinkingTime: '1s',
  },
  {
    id: '8',
    type: 'action',
    content: 'Read scene_1_lighting.json',
    timestamp: new Date(Date.now() - 4500),
  },
  {
    id: '9',
    type: 'code',
    content: `{
  "temperature": 3200,
  "intensity": 0.8,
  "filter": "cool"
}`,
    timestamp: new Date(Date.now() - 4300),
  },
  {
    id: '10',
    type: 'action',
    content: 'Updating lighting parameters...',
    timestamp: new Date(Date.now() - 4000),
  },
  {
    id: '11',
    type: 'agent',
    content: "Adjusted lighting to warmer tones (4500K). Scene 1 will now have a golden hour feel with increased temperature and amber filter.",
    timestamp: new Date(Date.now() - 3500),
  },
];

const mockConversations: Conversation[] = [
  {
    id: '1',
    name: 'South Park Episode',
    lastActivity: '2d ago',
    active: true,
  },
];

export const useStore = create<WeaveStore>((set) => ({
  // Tree state
  nodes: mockNodes,
  selectedNodeId: 'scene1',
  setSelectedNode: (id) => set({ selectedNodeId: id }),

  // Chat state
  messages: mockMessages,
  addMessage: (message) => set((state) => ({
    messages: [
      ...state.messages,
      {
        ...message,
        id: Math.random().toString(36).substr(2, 9),
        timestamp: new Date(),
      },
    ],
  })),

  // UI state
  activeTab: 'tree',
  setActiveTab: (tab) => set({ activeTab: tab }),

  activeAgent: 'Sub-1',
  setActiveAgent: (agent) => set({ activeAgent: agent }),

  conversations: mockConversations,
}));
