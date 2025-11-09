import { AgentSelector } from '../chat/AgentSelector';
import { ConversationList } from '../chat/ConversationList';
import { ChatMessages } from '../chat/ChatMessages';
import { ChatInput } from '../chat/ChatInput';

interface LeftPanelProps {
  onNewProject: () => void;
}

export function LeftPanel({ onNewProject }: LeftPanelProps) {
  return (
    <aside className="w-full h-full border-r border-border-subtle flex flex-col bg-bg-primary">
      <div className="p-4">
        <AgentSelector />
        <ConversationList onNewProject={onNewProject} />
      </div>

      <ChatMessages />
      <ChatInput />
    </aside>
  );
}
