"use client";
import { useEffect, useState } from "react";
import Table, { Column } from "../ui/Table";

export type Agent = {
  id: number;
  name: string;
  game: string;
  file_path: string;
  created_at: string;
  groupname?: string;
};

export type AgentListProps = {
  scope: "all" | "mine";
};

export default function AgentList({ scope }: AgentListProps) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let active = true;

    const fetchAgents = async () => {
      try {
        const endpoint =
          scope === "all"
            ? "http://localhost:5001/api/admin/agents"
            : "http://localhost:5001/api/user/agents";
        const res = await fetch(endpoint, { credentials: "include" });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error);
        if (active) setAgents(data.agents || []);
      } catch (err) {
        console.error("Failed to fetch agents:", err);
        if (active) setAgents([]);
      } finally {
        if (active) setLoading(false);
      }
    };

    fetchAgents();
    window.addEventListener("agentUploaded", fetchAgents);

    return () => {
      active = false;
      window.removeEventListener("agentUploaded", fetchAgents);
    };
  }, [scope]);

  const columns: Column<Agent>[] = [
    { key: "name", header: "Name" },
    { key: "game", header: "Game" },
    { key: "file_path", header: "Filename" },
    ...(scope === "all" ? [{ key: "groupname", header: "Group" }] : []),
    {
      key: "created_at",
      header: "Upload Time",
      width: 180,
      render: (row) => new Date(row.created_at).toLocaleString(),
    },
  ];

  return (
    <Table
      columns={columns}
      data={agents}
      isLoading={loading}
      emptyText="No agents uploaded yet"
    />
  );
}
