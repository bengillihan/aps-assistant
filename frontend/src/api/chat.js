/**
 * All backend communication lives here.
 * The backend URL is read from an env variable so it works in both
 * Vite dev (proxied) and Electron production builds.
 */

const API_BASE = import.meta.env.VITE_API_URL || "";

/**
 * Send a chat message to the backend.
 *
 * @param {string} message - User's text message
 * @param {string} mode    - "general" | "email" | "rag"
 * @param {File[]} files   - Optional file attachments
 * @returns {Promise<{reply: string, mode: string, server_used: string, latency_ms: number}>}
 */
export async function sendMessage(message, mode, files = []) {
  const formData = new FormData();
  formData.append("message", message);
  formData.append("mode", mode);

  for (const file of files) {
    formData.append("files", file);
  }

  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `Server error: ${response.status}`);
  }

  return response.json();
}
