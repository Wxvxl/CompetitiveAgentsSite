"use client";
import React from "react";
import Button from "../components/ui/Button";
import useAuth from "../hooks/useAuth";
import StudentAgentPanel from "../components/agents/StudentAgentPanel";

export default function DashboardPage() {
  const { user, loading, logout, isAdmin } = useAuth();

  return (
    <section>
      <h2>Dashboard</h2>
      {loading ? (
        <div>Loading...</div>
      ) : user ? (
        <>
          <p>Welcome, {user.email}!</p>
          {isAdmin ? (
            <p>
              <strong>You are an admin.</strong>
              <br />
              <a href="/admin">Go to Admin Panel</a>
            </p>
          ) : (
            <StudentAgentPanel />
          )}
          <Button onClick={logout} variant="ghost">
            Logout
          </Button>
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
