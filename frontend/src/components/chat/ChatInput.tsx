import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useStore } from '../../store/useStore';

export function ChatInput() {
  const { addMessage, selectedNodeId, nodes } = useStore();
  const [input, setInput] = useState('');

  const selectedNode = nodes.find((n) => n.id === selectedNodeId);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    addMessage({
      type: 'user',
      content: input,
      nodeContext: selectedNodeId || undefined,
    });

    setInput('');
  };

  return (
    <div className="p-4 pt-2 border-t border-border-subtle">
      <AnimatePresence>
        {selectedNodeId && selectedNode && (
          <motion.div
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -5 }}
            className="mb-2 inline-flex items-center gap-2 px-2 py-1 bg-bg-tertiary/50 rounded text-xs text-text-secondary"
          >
            <span>💬</span>
            <span>{selectedNode.name}</span>
            <button
              onClick={() => useStore.setState({ selectedNodeId: null })}
              className="ml-1 hover:text-text-primary transition-colors"
            >
              ×
            </button>
          </motion.div>
        )}
      </AnimatePresence>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type message..."
          className="w-full h-9 px-3 bg-bg-secondary border border-border-subtle rounded text-sm placeholder:text-text-tertiary focus:outline-none focus:border-status-active/50 transition-colors"
        />
      </form>
    </div>
  );
}
