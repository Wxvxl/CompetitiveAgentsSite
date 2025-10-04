"use client";

import { useState, useEffect } from "react";
import Table from "../ui/Table";

interface AgentWithRecord {
  agent_id: number;
  agent_name: string;
  wins: number;
  losses: number;
  draws: number;
  total_contests: number;
  win_rate?: string;
}

export default function AgentRecordsList() {
  const [agents, setAgents] = useState<AgentWithRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchAgentsWithRecords();
  }, []);

  const fetchAgentsWithRecords = async () => {
    try {
      // First fetch all agents
      const agentsResponse = await fetch(
        "http://localhost:5001/api/admin/agents",
        {
          credentials: "include",
        }
      );

      if (!agentsResponse.ok) {
        setError("Failed to fetch agents");
        return;
      }

      const agentsData = await agentsResponse.json();
      const allAgents = agentsData.agents || [];

      // Fetch records for each agent
      const agentsWithRecords = await Promise.all(
        allAgents.map(async (agent: any) => {
          try {
            const recordResponse = await fetch(
              `http://localhost:5001/api/agents/${agent.id}/record`,
              {
                credentials: "include",
              }
            );

            if (recordResponse.ok) {
              const recordData = await recordResponse.json();
              const winRate =
                recordData.total_contests > 0
                  ? (
                      (recordData.wins / recordData.total_contests) *
                      100
                    ).toFixed(1)
                  : "0.0";

              return {
                agent_id: agent.id,
                agent_name: agent.name,
                wins: recordData.wins,
                losses: recordData.losses,
                draws: recordData.draws,
                total_contests: recordData.total_contests,
                win_rate: winRate,
              };
            }
            return null;
          } catch (err) {
            console.error(`Failed to fetch record for agent ${agent.id}:`, err);
            return null;
          }
        })
      );

      const validRecords = agentsWithRecords.filter(
        (r) => r !== null
      ) as AgentWithRecord[];
      setAgents(validRecords);
    } catch (err) {
      setError("An error occurred while fetching agent records");
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { key: "agent_name", header: "Agent Name" },
    { key: "wins", header: "Wins" },
    { key: "losses", header: "Losses" },
    { key: "draws", header: "Draws" },
    { key: "total_contests", header: "Total Contests" },
    {
      key: "win_rate",
      header: "Win Rate",
      render: (row: AgentWithRecord) => (
        <span className="font-medium">{row.win_rate}%</span>
      ),
    },
  ];

  if (loading) {
    return <p>Loading agent records...</p>;
  }

  if (error) {
    return <p className="text-red-500">{error}</p>;
  }

  return (
    <div>
      <div className="mb-4">
        <h3 className="text-lg font-bold">Agent Win/Loss Records (FR3.4)</h3>
        <p className="text-sm text-gray-600">
          Track each agent's performance across all contests
        </p>
      </div>

      {agents.length === 0 ? (
        <p className="text-gray-500">No agent records found.</p>
      ) : (
        <Table data={agents} columns={columns} />
      )}
    </div>
  );
}
