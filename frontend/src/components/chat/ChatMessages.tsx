import { useRef, useEffect } from 'react';
import { useStore } from '../../store/useStore';

export function ChatMessages() {
  const { messages } = useStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto scrollbar-thin px-4 py-4 space-y-3">
      {messages.map((message) => {
        // User messages
        if (message.type === 'user') {
          return (
            <div key={message.id} className="space-y-1">
              <div className="text-[11px] text-text-tertiary uppercase tracking-wider font-medium">
                YOU
              </div>
              <div className="text-sm text-text-primary leading-relaxed">
                {message.content}
              </div>
            </div>
          );
        }

        // Thinking messages
        if (message.type === 'thinking') {
          return (
            <div key={message.id} className="text-sm text-text-secondary italic">
              Thought for {message.thinkingTime || '2s'}
            </div>
          );
        }

        // Action messages (like "Read file.tsx")
        if (message.type === 'action') {
          return (
            <div key={message.id} className="text-sm text-text-secondary">
              {message.content}
            </div>
          );
        }

        // Code/output blocks
        if (message.type === 'code') {
          return (
            <div key={message.id} className="my-2">
              <pre className="bg-[#0d0d0d] border border-border-subtle rounded-md p-3 overflow-x-auto">
                <code className="text-xs font-mono text-text-secondary">
                  {message.content}
                </code>
              </pre>
            </div>
          );
        }

        // Agent messages
        return (
          <div key={message.id} className="space-y-1">
            <div className="text-[11px] text-text-tertiary uppercase tracking-wider font-medium">
              AGENT
            </div>
            <div className="text-sm text-text-primary leading-relaxed">
              {message.content}
            </div>
          </div>
        );
      })}
      <div ref={messagesEndRef} />
    </div>
  );
}
