"use client";
import React, { useState, useEffect } from "react";

type User = {
  id: number;
  email: string;
  isAdmin: boolean;
  name?: string;
  role?: string;
};

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [showUpload, setShowUpload] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");

  async function fetchMe() {
    const res = await fetch("http://localhost:5001/api/me", {
      credentials: "include",
    });
    const data = await res.json();
    if (res.ok) setUser(data.user);
    else setUser(null);
  }

  async function handleLogout() {
    await fetch("http://localhost:5001/api/logout", {
      method: "POST",
      credentials: "include",
    });
    setUser(null);
  }

  useEffect(() => {
    fetchMe();
  }, []);

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) {
      setMessage("Please select a .py file.");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch("http://localhost:5001/api/upload_agent", {
      method: "POST",
      body: formData,
      credentials: "include",
    });
    const data = await res.json();
    setMessage(data.message || data.error);
    if (res.ok) setFile(null);
  }

  return (
    <section>
      <h2>Dashboard</h2>
      {user ? (
        <>
          <p>Welcome, {user.email}!</p>
          {user.isAdmin && (
            <p>
              <strong>You are an admin.</strong>
              <br />
              <a href="/admin">Go to Admin Panel</a>
            </p>
          )}
          <button onClick={handleLogout}>Logout</button>
          <button onClick={() => setShowUpload(true)} style={{ marginLeft: 8 }}>
            Submit Agent
          </button>
          {showUpload && (
            <div
              style={{
                position: "fixed",
                top: 0,
                left: 0,
                width: "100vw",
                height: "100vh",
                background: "rgba(0,0,0,0.5)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <div style={{ background: "#fff", padding: 24, borderRadius: 8 }}>
                <h3>Upload Agent</h3>
                <form onSubmit={handleUpload}>
                  <input
                    type="file"
                    accept=".py"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                  />
                  <button type="submit">Upload</button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowUpload(false);
                      setMessage("");
                    }}
                    style={{ marginLeft: 8 }}
                  >
                    Cancel
                  </button>
                </form>
                {message && <div style={{ marginTop: 8 }}>{message}</div>}
              </div>
            </div>
          )}
        </>
      ) : (
        <ul>
          <li>
            <a href="/register">Register</a>
          </li>
          <li>
            <a href="/login">Login</a>
          </li>
        </ul>
      )}
    </section>
  );
}
