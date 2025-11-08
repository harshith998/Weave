import { TopBar } from './components/layout/TopBar';
import { LeftPanel } from './components/layout/LeftPanel';
import { RightPanel } from './components/layout/RightPanel';

function App() {
  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden">
      <TopBar />
      <main className="flex-1 flex overflow-hidden">
        <LeftPanel />
        <RightPanel />
      </main>
    </div>
  );
}

export default App;
