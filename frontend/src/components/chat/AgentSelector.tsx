import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useStore } from '../../store/useStore';
import type { Agent } from '../../types';

export function AgentSelector() {
  const { activeAgent, setActiveAgent } = useStore();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const agents: Agent[] = ['Sub-1', 'Sub-2', 'Sub-3'];

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={dropdownRef} className="relative mb-3">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full h-10 px-3 rounded-md bg-bg-secondary border border-border-subtle hover:border-border-light flex items-center justify-between text-sm font-medium transition-colors"
      >
        <span>Agent</span>
        <motion.svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
        </motion.svg>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.15 }}
            className="absolute top-full mt-1 w-full bg-bg-secondary border border-border-subtle rounded-md overflow-hidden z-50"
          >
            {agents.map((agent) => (
              <button
                key={agent}
                onClick={() => {
                  setActiveAgent(agent);
                  setIsOpen(false);
                }}
                className="w-full px-3 h-9 flex items-center gap-2 hover:bg-bg-tertiary transition-colors text-sm text-left"
              >
                {agent === activeAgent && (
                  <span className="w-2 h-2 rounded-full bg-status-completed"></span>
                )}
                {agent === activeAgent ? <span>• {agent}</span> : <span className="ml-4">{agent}</span>}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
