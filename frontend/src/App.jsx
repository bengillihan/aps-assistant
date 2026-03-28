/**
 * Root component — owns all state and orchestrates child components.
 *
 * State:
 *   messages  — conversation history [ {role, text, meta?} ]
 *   mode      — current chat mode ("general" | "email")
 *   loading   — true while waiting for backend response
 *   error     — last error string, shown inline
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
  const [error, setError] = useState(null);

  async function handleSend(text, files) {
    // Append the user's message immediately for responsiveness
    setMessages((prev) => [...prev, { role: "user", text }]);
    setError(null);
    setLoading(true);

    try {
      const data = await sendMessage(text, mode, files);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.reply,
          meta: { server_used: data.server_used, latency_ms: data.latency_ms },
        },
      ]);
    } catch (err) {
      setError(err.message || "Something went wrong.");
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
        {error && <div className="error-banner">{error}</div>}
        <MessageInput onSend={handleSend} loading={loading} />
      </footer>
    </div>
  );
}
