import { motion } from 'framer-motion';
import type { Tab } from '../../types';

interface TabToggleProps {
  activeTab: Tab;
  onTabChange: (tab: Tab) => void;
}

export function TabToggle({ activeTab, onTabChange }: TabToggleProps) {
  return (
    <div className="flex gap-1 p-1 bg-bg-secondary/40 rounded-lg mb-4">
      <button
        onClick={() => onTabChange('tree')}
        className="relative flex-1 h-10 px-6 rounded-lg text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2"
      >
        {activeTab === 'tree' && (
          <motion.div
            layoutId="activeTab"
            className="absolute inset-0 bg-status-active/15 border border-status-active/30 rounded-lg shadow-md"
            transition={{ type: 'spring', duration: 0.5, bounce: 0.2 }}
          />
        )}
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="relative">
          <circle cx="8" cy="3" r="2" stroke="currentColor" strokeWidth="1.5"/>
          <circle cx="4" cy="10" r="2" stroke="currentColor" strokeWidth="1.5"/>
          <circle cx="12" cy="10" r="2" stroke="currentColor" strokeWidth="1.5"/>
          <path d="M8 5V8M8 8L4 8M8 8L12 8" stroke="currentColor" strokeWidth="1.5"/>
        </svg>
        <span className={`relative ${activeTab === 'tree' ? 'text-text-primary' : 'text-text-secondary'}`}>
          Generation Tree
        </span>
      </button>

      <button
        onClick={() => onTabChange('timeline')}
        className="relative flex-1 h-10 px-6 rounded-lg text-sm font-medium transition-all duration-200 flex items-center justify-center gap-2"
      >
        {activeTab === 'timeline' && (
          <motion.div
            layoutId="activeTab"
            className="absolute inset-0 bg-status-active/15 border border-status-active/30 rounded-lg shadow-md"
            transition={{ type: 'spring', duration: 0.5, bounce: 0.2 }}
          />
        )}
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" className="relative">
          <rect x="2" y="4" width="12" height="8" rx="1" stroke="currentColor" strokeWidth="1.5"/>
          <line x1="5" y1="4" x2="5" y2="12" stroke="currentColor" strokeWidth="1.5"/>
          <line x1="9" y1="4" x2="9" y2="12" stroke="currentColor" strokeWidth="1.5"/>
        </svg>
        <span className={`relative ${activeTab === 'timeline' ? 'text-text-primary' : 'text-text-secondary'}`}>
          Timeline Editor
        </span>
      </button>
    </div>
  );
}
