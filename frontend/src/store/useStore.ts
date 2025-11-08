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
  
  // Layout state
  leftPanelWidth: number;
  setLeftPanelWidth: (width: number) => void;
}

// Mock data for initial state - Complete video production workflow
const mockNodes: TreeNode[] = [
  {
    id: 'root',
    name: 'South Park AI Episode',
    status: 'progress',
    progress: 62,
  },

  // Character Generation Pipeline
  {
    id: 'characters',
    name: 'Character Pipeline',
    status: 'completed',
    progress: 100,
    parent: 'root',
    children: [
      {
        id: 'char-models',
        name: 'Character Models',
        status: 'completed',
        progress: 100,
        parent: 'characters',
        children: [
          {
            id: 'char-cartman',
            name: 'Cartman - AI Mayor',
            status: 'completed',
            parent: 'char-models',
          },
          {
            id: 'char-kyle',
            name: 'Kyle - Resistance Leader',
            status: 'completed',
            parent: 'char-models',
          },
          {
            id: 'char-stan',
            name: 'Stan - Skeptic',
            status: 'completed',
            parent: 'char-models',
          },
        ],
      },
      {
        id: 'char-voices',
        name: 'Voice Synthesis',
        status: 'completed',
        progress: 100,
        parent: 'characters',
        children: [
          {
            id: 'voice-training',
            name: 'Voice Model Training',
            status: 'completed',
            parent: 'char-voices',
          },
          {
            id: 'voice-samples',
            name: 'Sample Generation',
            status: 'completed',
            parent: 'char-voices',
          },
        ],
      },
      {
        id: 'char-animations',
        name: 'Animation Rigs',
        status: 'completed',
        progress: 100,
        parent: 'characters',
      },
    ],
  },

  // Scene 1: Town Hall Meeting
  {
    id: 'scene1',
    name: 'Scene 1: Town Hall',
    status: 'completed',
    progress: 100,
    parent: 'root',
    metadata: {
      duration: '45s',
      lastUpdate: '5m ago',
    },
    children: [
      {
        id: 'scene1-storyboard',
        name: 'Storyboard',
        status: 'completed',
        parent: 'scene1',
      },
      {
        id: 'scene1-bg',
        name: 'Background Assets',
        status: 'completed',
        parent: 'scene1',
        children: [
          {
            id: 'scene1-bg-hall',
            name: 'Town Hall Interior',
            status: 'completed',
            parent: 'scene1-bg',
          },
          {
            id: 'scene1-bg-crowd',
            name: 'Crowd Fill',
            status: 'completed',
            parent: 'scene1-bg',
          },
        ],
      },
      {
        id: 'scene1-camera',
        name: 'Camera Work',
        status: 'completed',
        parent: 'scene1',
        children: [
          {
            id: 'scene1-cam-wide',
            name: 'Wide Establishing Shot',
            status: 'completed',
            parent: 'scene1-camera',
          },
          {
            id: 'scene1-cam-close',
            name: 'Character Close-ups',
            status: 'completed',
            parent: 'scene1-camera',
          },
        ],
      },
      {
        id: 'scene1-dialogue',
        name: 'Dialogue & Timing',
        status: 'completed',
        parent: 'scene1',
      },
      {
        id: 'scene1-lighting',
        name: 'Lighting (Warm)',
        status: 'completed',
        progress: 100,
        parent: 'scene1',
      },
    ],
  },

  // Scene 2: Kyle's House
  {
    id: 'scene2',
    name: 'Scene 2: Kyle\'s House',
    status: 'active',
    progress: 73,
    parent: 'root',
    metadata: {
      workingOn: 'Audio synchronization',
      duration: '38s',
      lastUpdate: '12s ago',
    },
    children: [
      {
        id: 'scene2-storyboard',
        name: 'Storyboard',
        status: 'completed',
        parent: 'scene2',
      },
      {
        id: 'scene2-bg',
        name: 'Background Assets',
        status: 'completed',
        parent: 'scene2',
      },
      {
        id: 'scene2-animation',
        name: 'Character Animation',
        status: 'progress',
        progress: 85,
        parent: 'scene2',
        children: [
          {
            id: 'scene2-anim-kyle',
            name: 'Kyle Gestures',
            status: 'completed',
            parent: 'scene2-animation',
          },
          {
            id: 'scene2-anim-stan',
            name: 'Stan Reactions',
            status: 'progress',
            progress: 60,
            parent: 'scene2-animation',
          },
        ],
      },
      {
        id: 'scene2-audio',
        name: 'Audio Mix',
        status: 'progress',
        progress: 45,
        parent: 'scene2',
        children: [
          {
            id: 'scene2-dialogue',
            name: 'Dialogue Tracks',
            status: 'completed',
            parent: 'scene2-audio',
          },
          {
            id: 'scene2-sfx',
            name: 'Sound Effects',
            status: 'progress',
            progress: 30,
            parent: 'scene2-audio',
          },
        ],
      },
      {
        id: 'scene2-lighting',
        name: 'Lighting',
        status: 'completed',
        parent: 'scene2',
      },
    ],
  },

  // Scene 3: AI Takeover Montage
  {
    id: 'scene3',
    name: 'Scene 3: AI Montage',
    status: 'progress',
    progress: 35,
    parent: 'root',
    metadata: {
      workingOn: 'Generating montage clips',
      duration: '52s',
      estimatedTime: '3m 15s',
    },
    children: [
      {
        id: 'scene3-storyboard',
        name: 'Storyboard',
        status: 'completed',
        parent: 'scene3',
      },
      {
        id: 'scene3-clips',
        name: 'Montage Clips',
        status: 'progress',
        progress: 40,
        parent: 'scene3',
        children: [
          {
            id: 'scene3-clip1',
            name: 'Robot Police Cars',
            status: 'completed',
            parent: 'scene3-clips',
          },
          {
            id: 'scene3-clip2',
            name: 'AI Traffic Lights',
            status: 'completed',
            parent: 'scene3-clips',
          },
          {
            id: 'scene3-clip3',
            name: 'Digital Billboards',
            status: 'progress',
            progress: 60,
            parent: 'scene3-clips',
          },
          {
            id: 'scene3-clip4',
            name: 'Surveillance Drones',
            status: 'pending',
            parent: 'scene3-clips',
          },
        ],
      },
      {
        id: 'scene3-music',
        name: 'Background Music',
        status: 'progress',
        progress: 70,
        parent: 'scene3',
      },
      {
        id: 'scene3-effects',
        name: 'Visual Effects',
        status: 'pending',
        parent: 'scene3',
      },
    ],
  },

  // Scene 4: Confrontation
  {
    id: 'scene4',
    name: 'Scene 4: Showdown',
    status: 'pending',
    parent: 'root',
    metadata: {
      duration: '1m 12s',
      estimatedTime: '8m 45s',
    },
    children: [
      {
        id: 'scene4-storyboard',
        name: 'Storyboard',
        status: 'pending',
        parent: 'scene4',
      },
      {
        id: 'scene4-bg',
        name: 'Background Assets',
        status: 'pending',
        parent: 'scene4',
      },
      {
        id: 'scene4-animation',
        name: 'Character Animation',
        status: 'pending',
        parent: 'scene4',
      },
      {
        id: 'scene4-vfx',
        name: 'Special Effects',
        status: 'pending',
        parent: 'scene4',
      },
    ],
  },

  // Post-Production Pipeline
  {
    id: 'postprod',
    name: 'Post-Production',
    status: 'pending',
    parent: 'root',
    metadata: {
      estimatedTime: '12m 30s',
    },
    children: [
      {
        id: 'transitions',
        name: 'Scene Transitions',
        status: 'pending',
        parent: 'postprod',
        children: [
          {
            id: 'trans-1-2',
            name: 'Scene 1 → 2',
            status: 'pending',
            parent: 'transitions',
          },
          {
            id: 'trans-2-3',
            name: 'Scene 2 → 3',
            status: 'pending',
            parent: 'transitions',
          },
          {
            id: 'trans-3-4',
            name: 'Scene 3 → 4',
            status: 'pending',
            parent: 'transitions',
          },
        ],
      },
      {
        id: 'color-grade',
        name: 'Color Grading',
        status: 'pending',
        parent: 'postprod',
      },
      {
        id: 'master-audio',
        name: 'Master Audio Mix',
        status: 'pending',
        parent: 'postprod',
        children: [
          {
            id: 'audio-dialogue',
            name: 'Dialogue Balance',
            status: 'pending',
            parent: 'master-audio',
          },
          {
            id: 'audio-music',
            name: 'Music Levels',
            status: 'pending',
            parent: 'master-audio',
          },
          {
            id: 'audio-sfx',
            name: 'SFX Mix',
            status: 'pending',
            parent: 'master-audio',
          },
        ],
      },
      {
        id: 'final-render',
        name: 'Final Render',
        status: 'pending',
        parent: 'postprod',
        children: [
          {
            id: 'render-preview',
            name: 'Preview Quality (720p)',
            status: 'pending',
            parent: 'final-render',
          },
          {
            id: 'render-full',
            name: 'Full Quality (4K)',
            status: 'pending',
            parent: 'final-render',
          },
        ],
      },
      {
        id: 'export',
        name: 'Export & Delivery',
        status: 'pending',
        parent: 'postprod',
      },
    ],
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
  {
    id: '12',
    type: 'user',
    content: 'How is the overall production coming along?',
    timestamp: new Date(Date.now() - 2000),
  },
  {
    id: '13',
    type: 'thinking',
    content: 'Analyzing production pipeline status across all nodes',
    timestamp: new Date(Date.now() - 1800),
    thinkingTime: '1s',
  },
  {
    id: '14',
    type: 'agent',
    content: "Great progress! Character pipeline is complete (100%). Scene 1 is finished. Currently working on Scene 2 (73% - audio sync in progress). Scene 3 montage is at 35% with clips being generated. Scene 4 and post-production are queued. Overall episode is 62% complete.",
    timestamp: new Date(Date.now() - 1500),
  },
  {
    id: '15',
    type: 'user',
    content: 'Show me what\'s happening with Scene 2 audio',
    timestamp: new Date(Date.now() - 500),
    nodeContext: 'scene2-audio',
  },
  {
    id: '16',
    type: 'action',
    content: 'Read scene2_audio_mix.json',
    timestamp: new Date(Date.now() - 300),
  },
  {
    id: '17',
    type: 'code',
    content: `{
  "dialogue_tracks": {
    "kyle": { "level": -3.2, "eq": "vocal_clarity", "status": "complete" },
    "stan": { "level": -4.1, "eq": "vocal_clarity", "status": "complete" }
  },
  "sound_effects": {
    "door_open": { "timestamp": "2.4s", "status": "pending" },
    "footsteps": { "timestamp": "5.1s", "status": "pending" },
    "background_ambience": { "level": -18, "status": "processing" }
  },
  "sync_status": "in_progress",
  "estimated_completion": "45s"
}`,
    timestamp: new Date(Date.now() - 200),
  },
  {
    id: '18',
    type: 'agent',
    content: "Dialogue tracks are complete and balanced. Working on sound effects synchronization - door and footstep sounds need to be placed, and background ambience is processing. Should be done in about 45 seconds.",
    timestamp: new Date(Date.now() - 50),
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
  selectedNodeId: 'scene2',
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
  
  // Layout state
  leftPanelWidth: 400,
  setLeftPanelWidth: (width) => set({ leftPanelWidth: width }),
}));
