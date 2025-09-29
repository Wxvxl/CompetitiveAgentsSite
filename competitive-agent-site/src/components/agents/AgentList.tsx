"use client";
import { useEffect, useState } from "react";
import Table, { Column } from "../ui/Table";

export type Agent = {
  id: number;
  filename: string;
  uploader: string;
  upload_time: string;
};

export type AgentListProps = {
  scope: "all" | "mine";
};

export default function AgentList({ scope }: AgentListProps) {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const endpoint =
          scope === "all"
            ? "http://localhost:5000/api/agents"
            : "http://localhost:5000/api/my_agents";
        const res = await fetch(endpoint, { credentials: "include" });
        const data = await res.json();
        if (active) setAgents(Array.isArray(data) ? data : []);
      } catch (_) {
        if (active) setAgents([]);
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, [scope]);

  const columns: Column<Agent>[] = [
    { key: "filename", header: "Filename" },
    { key: "uploader", header: "Uploader" },
    { key: "upload_time", header: "Upload Time", width: 180 },
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
