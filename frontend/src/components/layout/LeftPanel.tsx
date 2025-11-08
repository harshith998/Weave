import { AgentSelector } from '../chat/AgentSelector';
import { ConversationList } from '../chat/ConversationList';
import { ChatMessages } from '../chat/ChatMessages';
import { ChatInput } from '../chat/ChatInput';

export function LeftPanel() {
  return (
    <aside className="w-[30%] min-w-[320px] max-w-[500px] h-full border-r border-border-subtle flex flex-col bg-bg-primary">
      <div className="p-4">
        <AgentSelector />
        <ConversationList />
      </div>

      <ChatMessages />
      <ChatInput />
    </aside>
  );
}
