"use client";
import { useState } from "react";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";

export default function RegisterPage() {
  const [form, setForm] = useState({
    email: "",
    password: "",
    username: "",
    role: "student",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSuccess("");
    console.log("Sending form data:", form);

    try {
      const res = await fetch("http://localhost:5000/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
        credentials: "include",
      });
      const data = await res.json();
      console.log("Server response:", data);

      if (res.ok) {
        setSuccess("Registration successful!");
        window.location.href = "/login";
      } else {
        setError(data.error || "Registration failed");
        console.error("Registration failed:", data.error);
      }
    } catch (err) {
      console.error("Registration error:", err);
      setError("Failed to connect to server");
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: 480 }}>
      <h2>Register</h2>
      <Input
        type="email"
        placeholder="Email"
        value={form.email}
        onChange={(e) => setForm({ ...form, email: e.target.value })}
        required
      />
      <Input
        type="text"
        placeholder="Username"
        value={form.username}
        onChange={(e) => setForm({ ...form, username: e.target.value })}
        required
      />
      <Input
        type="password"
        placeholder="Password"
        value={form.password}
        onChange={(e) => setForm({ ...form, password: e.target.value })}
        required
      />
      <div style={{ marginBottom: 12 }}>
        <select
          value={form.role}
          onChange={(e) => setForm({ ...form, role: e.target.value })}
          required
          style={{
            width: "100%",
            padding: "8px 10px",
            borderRadius: 6,
            border: "1px solid #d1d5db",
            outline: "none",
          }}
        >
          <option value="student">Student</option>
          <option value="admin">Admin</option>
        </select>
      </div>
      <Button type="submit">Register</Button>
      {error && <div style={{ color: "red", marginTop: 8 }}>{error}</div>}
      {success && <div style={{ color: "green", marginTop: 8 }}>{success}</div>}
    </form>
  );
}
