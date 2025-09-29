"use client";
import RoleGuard from "../../components/auth/RoleGuard";
import AgentList from "../../components/agents/AgentList";

export default function AdminPage() {
  return (
    <RoleGuard allow="admin" fallback={<div>Access denied.</div>}>
      <section>
        <h2>Admin Panel</h2>
        <h3>All Uploaded Agents</h3>
        <AgentList scope="all" />
      </section>
    </RoleGuard>
  );
}
