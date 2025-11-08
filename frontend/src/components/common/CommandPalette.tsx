import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Command {
  id: string;
  name: string;
  description: string;
  icon: string;
  shortcut?: string;
  action: () => void;
}

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const [search, setSearch] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);

  const commands: Command[] = [
    {
      id: 'new-project',
      name: 'New Project',
      description: 'Create a new video generation project',
      icon: '✨',
      shortcut: '⌘N',
      action: () => console.log('New project'),
    },
    {
      id: 'switch-agent',
      name: 'Switch Agent',
      description: 'Change the active agent',
      icon: '🤖',
      action: () => console.log('Switch agent'),
    },
    {
      id: 'toggle-tree',
      name: 'Toggle Tree View',
      description: 'Show/hide the generation tree',
      icon: '🌳',
      action: () => console.log('Toggle tree'),
    },
    {
      id: 'timeline',
      name: 'Open Timeline',
      description: 'Switch to timeline editor',
      icon: '⏱️',
      action: () => console.log('Timeline'),
    },
  ];

  const filteredCommands = commands.filter((cmd) =>
    cmd.name.toLowerCase().includes(search.toLowerCase()) ||
    cmd.description.toLowerCase().includes(search.toLowerCase())
  );

  useEffect(() => {
    if (!isOpen) {
      setSearch('');
      setSelectedIndex(0);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((i) => (i + 1) % filteredCommands.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((i) => (i - 1 + filteredCommands.length) % filteredCommands.length);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        filteredCommands[selectedIndex]?.action();
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, selectedIndex, filteredCommands, onClose]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
          />

          <div className="fixed inset-0 flex items-start justify-center pt-[20vh] z-50 pointer-events-none">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -20 }}
              transition={{ type: 'spring', duration: 0.3 }}
              className="w-full max-w-2xl bg-bg-secondary border border-border-light rounded-lg shadow-2xl pointer-events-auto overflow-hidden"
            >
              <div className="p-3 border-b border-border-subtle">
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Type a command or search..."
                  autoFocus
                  className="w-full bg-transparent text-base text-text-primary placeholder:text-text-tertiary focus:outline-none"
                />
              </div>

              <div className="max-h-[400px] overflow-y-auto">
                {filteredCommands.length === 0 ? (
                  <div className="p-8 text-center text-text-secondary text-sm">
                    No commands found
                  </div>
                ) : (
                  <div className="py-2">
                    {filteredCommands.map((cmd, index) => (
                      <button
                        key={cmd.id}
                        onClick={() => {
                          cmd.action();
                          onClose();
                        }}
                        onMouseEnter={() => setSelectedIndex(index)}
                        className={`w-full px-4 py-3 flex items-center gap-3 hover:bg-bg-tertiary transition-colors ${
                          index === selectedIndex ? 'bg-bg-tertiary' : ''
                        }`}
                      >
                        <span className="text-2xl">{cmd.icon}</span>
                        <div className="flex-1 text-left">
                          <div className="text-sm font-medium text-text-primary">
                            {cmd.name}
                          </div>
                          <div className="text-xs text-text-secondary">
                            {cmd.description}
                          </div>
                        </div>
                        {cmd.shortcut && (
                          <kbd className="px-2 py-1 bg-bg-primary border border-border-subtle rounded text-xs font-mono text-text-tertiary">
                            {cmd.shortcut}
                          </kbd>
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <div className="px-4 py-2 border-t border-border-subtle bg-bg-primary/50 flex items-center justify-between text-xs text-text-tertiary">
                <div className="flex items-center gap-4">
                  <span className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-bg-secondary border border-border-subtle rounded text-[10px]">
                      ↑↓
                    </kbd>
                    navigate
                  </span>
                  <span className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-bg-secondary border border-border-subtle rounded text-[10px]">
                      ↵
                    </kbd>
                    select
                  </span>
                  <span className="flex items-center gap-1">
                    <kbd className="px-1.5 py-0.5 bg-bg-secondary border border-border-subtle rounded text-[10px]">
                      esc
                    </kbd>
                    close
                  </span>
                </div>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
