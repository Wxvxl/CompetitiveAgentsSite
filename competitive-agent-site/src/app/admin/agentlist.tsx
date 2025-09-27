"use client";
import { useEffect, useState } from "react";
import Table, { Column } from "../../components/ui/Table";

type Agent = {
  id: number;
  filename: string;
  uploader: string;
  upload_time: string;
};

export default function AgentListPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const res = await fetch("http://localhost:5000/api/agents", {
          credentials: "include",
        });
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
  }, []);

  const columns: Column<Agent>[] = [
    { key: "filename", header: "Filename" },
    { key: "uploader", header: "Uploader" },
    { key: "upload_time", header: "Upload Time", width: 180 },
  ];

  return (
    <section>
      <h2>All Uploaded Agents</h2>
      <Table
        columns={columns}
        data={agents}
        isLoading={loading}
        emptyText="No agents uploaded yet"
      />
    </section>
  );
}
