"use client";
import Link from "next/link"; // Import Link from Next.js
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
          <div className="flex items-center justify-between mb-4">
            <h3>All Uploaded Agents</h3>
            {/* Start Contest Button */}
            <Link href="/contests">
              <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                Contest Management
              </button>
            </Link>
          </div>
          <AgentList scope="all" />
        </div>
      </section>
    </RoleGuard>
  );
}
