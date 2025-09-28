"use client";
import { useState } from "react";

export default function AgentUpload({ game }: { game: string }) {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) {
      setError("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(`http://localhost:5001/agents/upload/${game}`, {
      method: "POST",
      body: formData,
      credentials: "include",
    });

    const data = await res.json();
    if (res.ok) {
      setMessage(data.message);
      setError("");
    } else {
      setError(data.error || "Upload failed");
      setMessage("");
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h3>Upload Agent for {game}</h3>
      <input
        type="file"
        accept=".py"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
      />
      <button type="submit">Upload</button>
      {message && <div style={{ color: "green" }}>{message}</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}
    </form>
  );
}
