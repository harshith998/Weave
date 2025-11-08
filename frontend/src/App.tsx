import { useState, useEffect, useRef } from 'react';
import { TopBar } from './components/layout/TopBar';
import { LeftPanel } from './components/layout/LeftPanel';
import { RightPanel } from './components/layout/RightPanel';
import { StatusBar } from './components/layout/StatusBar';
import { CommandPalette } from './components/common/CommandPalette';
import { NewProjectModal } from './components/common/NewProjectModal';
import { useStore } from './store/useStore';

function App() {
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [newProjectModalOpen, setNewProjectModalOpen] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  
  const leftPanelWidth = useStore((state) => state.leftPanelWidth);
  const setLeftPanelWidth = useStore((state) => state.setLeftPanelWidth);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Command/Ctrl + K for command palette
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(true);
      }

      // Command/Ctrl + N for new project
      if ((e.metaKey || e.ctrlKey) && e.key === 'n') {
        e.preventDefault();
        setNewProjectModalOpen(true);
      }

      // Escape to close modals
      if (e.key === 'Escape') {
        setCommandPaletteOpen(false);
        setNewProjectModalOpen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleCreateProject = (name: string, description: string) => {
    console.log('Creating project:', name, description);
    // TODO: Add to store
  };

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden">
      <TopBar />
      <main className="flex-1 flex overflow-hidden">
        <LeftPanel onNewProject={() => setNewProjectModalOpen(true)} />
        <RightPanel />
      </main>
      <StatusBar />

      <CommandPalette
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
      />

      <NewProjectModal
        isOpen={newProjectModalOpen}
        onClose={() => setNewProjectModalOpen(false)}
        onCreate={handleCreateProject}
      />
    </div>
  );
}

export default App;
