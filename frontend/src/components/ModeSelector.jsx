/**
 * Mode selector — lets the user switch between chat modes.
 * Modes map 1:1 to backend mode_config entries.
 */

const MODES = [
  { value: "general", label: "General Help" },
  { value: "email", label: "Email Response Help" },
  // RAG will be enabled once the backend retrieval is implemented
  // { value: "rag", label: "Document Search" },
];

export default function ModeSelector({ mode, onChange }) {
  return (
    <div className="mode-selector">
      {MODES.map((m) => (
        <button
          key={m.value}
          className={`mode-btn ${mode === m.value ? "active" : ""}`}
          onClick={() => onChange(m.value)}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}
