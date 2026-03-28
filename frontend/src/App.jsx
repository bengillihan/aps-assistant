/**
 * Root component — owns all state and orchestrates child components.
 *
 * State:
 *   messages  — conversation history [ {role, text, meta?, failed?} ]
 *   mode      — current chat mode ("general" | "email")
 *   loading   — true while waiting for backend response
 */

import { useState } from "react";
import ModeSelector from "./components/ModeSelector";
import MessageList from "./components/MessageList";
import MessageInput from "./components/MessageInput";
import { sendMessage } from "./api/chat";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [mode, setMode] = useState("general");
  const [loading, setLoading] = useState(false);

  async function handleSend(text, files) {
    // Build the history the backend needs BEFORE appending the new user turn.
    // Only include successfully completed turns (skip failed assistant messages).
    const history = messages
      .filter((m) => !m.failed)
      .map((m) => ({ role: m.role, content: m.text }));

    // Optimistically append the user message
    const userMsg = { role: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const data = await sendMessage(text, mode, files, history);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.reply,
          meta: { server_used: data.server_used, latency_ms: data.latency_ms },
        },
      ]);
    } catch (err) {
      // Mark the optimistic user message as failed so the user knows it didn't go through
      setMessages((prev) =>
        prev.map((m, i) =>
          i === prev.length - 1 ? { ...m, failed: true, error: err.message || "Send failed." } : m
        )
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <span className="app-title">APS Assistant</span>
        <ModeSelector mode={mode} onChange={setMode} />
      </header>

      <main className="chat-area">
        <MessageList messages={messages} />
      </main>

      <footer className="chat-footer">
        <MessageInput onSend={handleSend} loading={loading} />
      </footer>
    </div>
  );
}
