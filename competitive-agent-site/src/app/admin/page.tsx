"use client";
import AgentUpload from "./agents";

export default function AdminPage() {
  return (
    <section>
      <h2>Admin Panel</h2>
      <AgentUpload game="conn4" />
      {/* Add more admin features here */}
    </section>
  );
}
