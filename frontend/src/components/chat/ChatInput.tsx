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
      <form onSubmit={handleSubmit} className="relative">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type message..."
          className="w-full h-9 px-3 bg-bg-secondary border border-border-subtle rounded text-sm placeholder:text-text-tertiary focus:outline-none focus:border-status-active/50 transition-colors"
        />
        {!input && (
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-text-tertiary pointer-events-none">
            <span className="inline-block animate-blink">|</span>
          </span>
        )}
      </form>
    </div>
  );
}
