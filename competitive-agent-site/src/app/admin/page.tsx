"use client";
import RoleGuard from "../../components/auth/RoleGuard";
import AgentList from "../../components/agents/AgentList";
import UserGroupManagement from "../../components/admin/UserGroupManagement";

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
      </section>
    </RoleGuard>
  );
}
