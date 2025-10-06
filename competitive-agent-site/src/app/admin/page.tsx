"use client";
import RoleGuard from "../../components/auth/RoleGuard";
import AgentList from "../../components/agents/AgentList";
import UserGroupManagement from "../../components/admin/UserGroupManagement";
import TournamentManager from "../../components/admin/TournamentManager";

export default function AdminPage() {
  return (
    <RoleGuard allow="admin" fallback={<div>Access denied.</div>}>
      <section>
        <h2>Admin Panel</h2>
        <div className="mb-8">
          <h3>User Group Management</h3>
          <UserGroupManagement />
        </div>
        <div>
          <h3>All Uploaded Agents</h3>
          <AgentList scope="all" />
        </div>
        <div className="mt-8">
          <TournamentManager />
        </div>
      </section>
    </RoleGuard>
  );
}
