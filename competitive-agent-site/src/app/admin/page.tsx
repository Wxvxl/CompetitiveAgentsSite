"use client";
import AgentUpload from "./agents";
import GroupManagement from "./group-management";

export default function AdminPage() {
  return (
    <section>
      <h2>Admin Panel</h2>
      <AgentUpload game="conn4" />
      <GroupManagement />
    </section>
  );
}
