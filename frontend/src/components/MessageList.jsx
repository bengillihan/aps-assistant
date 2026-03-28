/**
 * Renders the conversation history.
 * Each message has a role: "user" or "assistant".
 * User messages may have failed: true when the backend call errored.
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
        <div key={i} className={`message ${msg.role}${msg.failed ? " failed" : ""}`}>
          <div className="bubble">{msg.text}</div>
          {msg.failed && (
            <div className="meta error-meta">&#x26A0; {msg.error}</div>
          )}
          {msg.meta && !msg.failed && (
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
