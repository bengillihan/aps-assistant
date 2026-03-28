/**
 * Text input + file upload + send button.
 * Shift+Enter adds a newline; Enter alone submits.
 */

import { useRef, useState } from "react";

export default function MessageInput({ onSend, loading }) {
  const [text, setText] = useState("");
  const [files, setFiles] = useState([]);
  const fileInputRef = useRef(null);

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  function submit() {
    const trimmed = text.trim();
    if (!trimmed && files.length === 0) return;
    onSend(trimmed, files);
    setText("");
    setFiles([]);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

  function handleFileChange(e) {
    setFiles(Array.from(e.target.files));
  }

  return (
    <div className="message-input">
      {files.length > 0 && (
        <div className="file-chips">
          {files.map((f, i) => (
            <span key={i} className="chip">{f.name}</span>
          ))}
        </div>
      )}
      <div className="input-row">
        <textarea
          rows={2}
          placeholder="Type a message… (Enter to send, Shift+Enter for newline)"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button
          className="attach-btn"
          title="Attach file"
          onClick={() => fileInputRef.current?.click()}
          disabled={loading}
        >
          📎
        </button>
        <button
          className="send-btn"
          onClick={submit}
          disabled={loading || (!text.trim() && files.length === 0)}
        >
          {loading ? "…" : "Send"}
        </button>
      </div>
      <input
        ref={fileInputRef}
        type="file"
        multiple
        style={{ display: "none" }}
        onChange={handleFileChange}
      />
    </div>
  );
}
