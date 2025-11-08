# Weave Frontend

Modern React + TypeScript interface for Weave AI Video Orchestration, inspired by Linear's design language with glassmorphism effects.

## Quick Start

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

## Tech Stack

- React 18 + TypeScript
- Vite
- Tailwind CSS
- Framer Motion
- Zustand

## Project Structure

```
src/
├── components/
│   ├── layout/         # TopBar, LeftPanel, RightPanel
│   ├── chat/           # Chat interface components
│   ├── tree/           # Tree view and node components
│   └── common/         # Reusable components (GlassCard, TabToggle)
├── store/              # Zustand state management
├── types/              # TypeScript interfaces
└── App.tsx
```

## Features

✅ Linear-inspired dark UI with glassmorphism
✅ Real-time tree visualization with status indicators
✅ Interactive chat interface with context awareness
✅ Smooth animations with Framer Motion
✅ Multi-color node system (green/orange/blue/purple)
✅ Hover tooltips with node details
✅ Tab switching (Tree View / Timeline Editor)

## Design System

See `../DESIGN_SYSTEM.md` for complete specifications.

**Colors**: Dark theme with glassmorphic overlays
**Typography**: Inter font family
**Animations**: Pulse, glow, shimmer effects
**Status Colors**: Green (completed), Orange (progress), Blue (pending), Purple (active)
