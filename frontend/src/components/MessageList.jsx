/**
 * Renders the conversation history.
 * Each message has a role: "user" or "assistant".
 */

import { useEffect, useRef } from "react";

export default function MessageList({ messages }) {
  const bottomRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="message-list empty">
        <p>Ask anything. Switch modes above to change how the assistant responds.</p>
      </div>
    );
  }

  return (
    <div className="message-list">
      {messages.map((msg, i) => (
        <div key={i} className={`message ${msg.role}`}>
          <div className="bubble">{msg.text}</div>
          {msg.meta && (
            <div className="meta">
              {msg.meta.server_used} · {msg.meta.latency_ms}ms
            </div>
          )}
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
