"use client";
import { useState } from "react";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";

export default function LoginPage() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSuccess("");
    const res = await fetch("http://localhost:5001/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
      credentials: "include",
    });
    const data = await res.json();
    if (res.ok) {
      setSuccess("Login successful!");
      if (data.user.role === "admin" || data.user.isAdmin) {
        window.location.href = "/admin";
      } else {
        window.location.href = "/";
      }
    } else setError(data.error || "Login failed");
  }

  return (
    <form onSubmit={handleSubmit} style={{ maxWidth: 420 }}>
      <h2>Login</h2>
      <Input
        type="email"
        placeholder="Email"
        value={form.email}
        onChange={(e) => setForm({ ...form, email: e.target.value })}
        required
      />
      <Input
        type="password"
        placeholder="Password"
        value={form.password}
        onChange={(e) => setForm({ ...form, password: e.target.value })}
        required
      />
      <Button type="submit">Login</Button>
      {error && <div style={{ color: "red", marginTop: 8 }}>{error}</div>}
      {success && <div style={{ color: "green", marginTop: 8 }}>{success}</div>}
    </form>
  );
}
