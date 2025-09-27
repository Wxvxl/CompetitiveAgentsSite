"use client";
import React from "react";
import Button from "../ui/Button";
import useAuth from "../../hooks/useAuth";

export default function Header() {
  const { user, isAdmin, logout, loading } = useAuth();

  return (
    <header
      style={{
        background: "#343a40",
        color: "#fff",
        padding: "1rem",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
      }}
    >
      <a href="/" style={{ color: "#fff", textDecoration: "none" }}>
        <h1 style={{ margin: 0, fontSize: 20 }}>
          Competitive Agents Dashboard
        </h1>
      </a>
      <div>
        {loading ? (
          <span>Loading...</span>
        ) : user ? (
          <>
            <span style={{ marginRight: 12 }}>
              {user.email}
              {isAdmin ? " (Admin)" : ""}
            </span>
            {isAdmin && (
              <a
                href="/admin"
                style={{
                  background: "#e5e7eb",
                  color: "#111827",
                  padding: "8px 14px",
                  borderRadius: 6,
                  fontWeight: 600,
                  textDecoration: "none",
                  marginRight: 8,
                  display: "inline-block",
                }}
              >
                Admin
              </a>
            )}
            <Button onClick={logout} variant="ghost">
              Logout
            </Button>
          </>
        ) : (
          <>
            <a
              href="/register"
              style={{
                background: "#e5e7eb",
                color: "#111827",
                padding: "8px 14px",
                borderRadius: 6,
                fontWeight: 600,
                textDecoration: "none",
                marginRight: 8,
                display: "inline-block",
              }}
            >
              Register
            </a>
            <a
              href="/login"
              style={{
                background: "#2563eb",
                color: "#fff",
                padding: "8px 14px",
                borderRadius: 6,
                fontWeight: 600,
                textDecoration: "none",
                display: "inline-block",
              }}
            >
              Login
            </a>
          </>
        )}
      </div>
    </header>
  );
}
