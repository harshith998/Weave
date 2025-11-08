import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface NewProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreate: (name: string, description: string) => void;
}

export function NewProjectModal({ isOpen, onClose, onCreate }: NewProjectModalProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (name.trim()) {
      onCreate(name, description);
      setName('');
      setDescription('');
      onClose();
    }
  };

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

          <div className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ type: 'spring', duration: 0.3 }}
              className="w-full max-w-md bg-bg-secondary border border-border-light rounded-lg shadow-2xl pointer-events-auto"
            >
              <div className="p-6 border-b border-border-subtle">
                <h2 className="text-lg font-semibold text-text-primary">Create New Project</h2>
                <p className="text-sm text-text-secondary mt-1">
                  Start a new AI video generation project
                </p>
              </div>

              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    Project Name
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g., South Park Episode"
                    autoFocus
                    className="w-full h-10 px-3 bg-bg-primary border border-border-subtle rounded-md text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-status-active/50 transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-text-primary mb-2">
                    Description (optional)
                  </label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe what you want to create..."
                    rows={3}
                    className="w-full px-3 py-2 bg-bg-primary border border-border-subtle rounded-md text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-status-active/50 transition-colors resize-none"
                  />
                </div>

                <div className="pt-4 flex items-center justify-end gap-2">
                  <button
                    type="button"
                    onClick={onClose}
                    className="h-9 px-4 bg-bg-tertiary hover:bg-bg-primary border border-border-subtle rounded-md text-sm font-medium text-text-primary transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={!name.trim()}
                    className="h-9 px-4 bg-status-active hover:bg-status-active/90 disabled:bg-status-active/50 disabled:cursor-not-allowed text-white rounded-md text-sm font-medium transition-colors"
                  >
                    Create Project
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
