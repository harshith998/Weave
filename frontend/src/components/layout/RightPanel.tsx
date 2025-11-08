import { TabToggle } from '../common/TabToggle';
import { FlowChart } from '../tree/FlowChart';
import { useStore } from '../../store/useStore';

export function RightPanel() {
  const { activeTab, setActiveTab } = useStore();

  return (
    <section className="flex-1 h-full overflow-hidden flex flex-col bg-bg-primary p-6">
      <TabToggle activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="flex-1 overflow-hidden rounded-lg border border-border-subtle bg-bg-primary">
        {activeTab === 'tree' ? (
          <FlowChart />
        ) : (
          <div className="h-full flex flex-col items-center justify-center gap-4 text-center p-8">
            <svg width="64" height="64" viewBox="0 0 64 64" fill="none" className="text-text-tertiary">
              <rect x="8" y="20" width="48" height="24" rx="2" stroke="currentColor" strokeWidth="2"/>
              <line x1="20" y1="20" x2="20" y2="44" stroke="currentColor" strokeWidth="2"/>
              <line x1="32" y1="20" x2="32" y2="44" stroke="currentColor" strokeWidth="2"/>
              <line x1="44" y1="20" x2="44" y2="44" stroke="currentColor" strokeWidth="2"/>
            </svg>
            <h3 className="text-lg font-semibold text-text-primary">Timeline Editor</h3>
            <p className="text-sm text-text-secondary max-w-md">
              Coming soon: Video timeline with drag-and-drop clips, transitions, and frame-by-frame control
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
