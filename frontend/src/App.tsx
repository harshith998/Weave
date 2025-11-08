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

  const handleMouseDown = () => {
    setIsResizing(true);
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;
      
      const newWidth = e.clientX;
      if (newWidth >= 300 && newWidth <= 800) {
        setLeftPanelWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, setLeftPanelWidth]);

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden">
      <TopBar />
      <main className="flex-1 flex overflow-hidden">
        <div style={{ width: `${leftPanelWidth}px` }} className="relative">
          <LeftPanel onNewProject={() => setNewProjectModalOpen(true)} />
          <div
            className="absolute top-0 right-0 w-1 h-full cursor-col-resize bg-border-subtle hover:bg-accent-purple transition-colors z-10"
            onMouseDown={handleMouseDown}
            style={{
              cursor: 'col-resize',
            }}
          />
        </div>
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
