"use client";
import React, { useState } from "react";
import Button from "../ui/Button";

export type AgentUploadFormProps = {
  endpoint?: string;
  onUploaded?: (filename: string) => void;
  maxSize?: number;
};

export default function AgentUploadForm({
  endpoint = "http://localhost:5000/api/upload_agent",
  onUploaded,
  maxSize = 20,
}: AgentUploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);

  const validateFile = (file: File): string | null => {
    if (!file.name.endsWith(".py")) {
      return "Only Python (.py) files are supported";
    }
    if (file.size > maxSize * 1024 * 1024) {
      return `File size cannot exceed ${maxSize}MB`;
    }
    return null;
  };

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) {
      setMessage("Please select a .py file.");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    setLoading(true);
    try {
      const res = await fetch(endpoint, {
        method: "POST",
        body: formData,
        credentials: "include",
      });
      const data = await res.json();
      setMessage(data.message || data.error || "");
      if (res.ok && onUploaded) onUploaded(file.name);
      if (res.ok) setFile(null);
    } catch (e) {
      setMessage("Upload failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="file"
        accept=".py"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />
      <Button type="submit" isLoading={loading} style={{ marginLeft: 8 }}>
        Upload
      </Button>
      {message && <div style={{ marginTop: 8 }}>{message}</div>}
    </form>
  );
}
