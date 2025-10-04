"use client";

import { useState, useEffect } from "react";
import Table from "../ui/Table";
import Button from "../ui/Button";

interface Contest {
  contest_id: number;
  name: string;
  game: string;
  agent1_name: string;
  agent2_name: string;
  winner_id: number | null;
  status: string;
  created_at: string;
  completed_at: string | null;
}

interface ContestListProps {
  onViewDetails?: (contestId: number) => void;
}

export default function ContestList({ onViewDetails }: ContestListProps) {
  const [contests, setContests] = useState<Contest[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("all");
  const [runningContest, setRunningContest] = useState<number | null>(null);

  useEffect(() => {
    fetchContests();

    // Listen for contest creation events
    const handleContestCreated = () => {
      fetchContests();
    };

    window.addEventListener("contestCreated", handleContestCreated);
    return () =>
      window.removeEventListener("contestCreated", handleContestCreated);
  }, [statusFilter]);

  const fetchContests = async () => {
    try {
      console.log("Fetching contests with status:", statusFilter);
      const response = await fetch(
        `http://localhost:5001/api/contests?status=${statusFilter}`,
        {
          credentials: "include",
        }
      );

      console.log("Response status:", response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log("Contests data:", data);
        setContests(data.contests || []);
      } else {
        const errorData = await response.json();
        console.error("Error response:", errorData);
      }
    } catch (err) {
      console.error("Failed to fetch contests:", err);
      console.error("Error details:", err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleRunContest = async (contestId: number) => {
    setRunningContest(contestId);

    try {
      const response = await fetch(
        `http://localhost:5001/api/contests/${contestId}/run`,
        {
          method: "POST",
          credentials: "include",
        }
      );

      if (response.ok) {
        // Refresh the list to show updated status
        await fetchContests();
        alert("Contest completed successfully!");
      } else {
        const data = await response.json();
        alert(`Failed to run contest: ${data.error}`);
      }
    } catch (err) {
      alert("An error occurred while running the contest");
    } finally {
      setRunningContest(null);
    }
  };

  const columns = [
    { key: "name", header: "Name" },
    { key: "game", header: "Game" },
    { key: "agent1_name", header: "Agent 1" },
    { key: "agent2_name", header: "Agent 2" },
    {
      key: "status",
      header: "Status",
      render: (row: Contest) => (
        <span
          className={`px-2 py-1 rounded text-xs ${
            row.status === "completed"
              ? "bg-green-100 text-green-800"
              : "bg-yellow-100 text-yellow-800"
          }`}
        >
          {row.status}
        </span>
      ),
    },
    {
      key: "created_at",
      header: "Created",
      render: (row: Contest) => new Date(row.created_at).toLocaleString(),
    },
    {
      key: "contest_id",
      header: "Actions",
      render: (row: Contest) => (
        <div className="flex gap-2">
          {row.status === "pending" && (
            <Button
              onClick={() => handleRunContest(row.contest_id)}
              disabled={runningContest === row.contest_id}
              className="text-xs"
            >
              {runningContest === row.contest_id ? "Running..." : "Run"}
            </Button>
          )}
          <Button
            onClick={() => onViewDetails?.(row.contest_id)}
            className="text-xs bg-blue-500 hover:bg-blue-600"
          >
            View
          </Button>
        </div>
      ),
    },
  ];

  if (loading) {
    return <p>Loading contests...</p>;
  }

  return (
    <div>
      <div className="mb-4 flex gap-2">
        <label className="text-sm font-medium">Filter by status:</label>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="border rounded px-2 py-1 text-sm"
        >
          <option value="all">All</option>
          <option value="pending">Pending</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      {contests.length === 0 ? (
        <p className="text-gray-500">No contests found.</p>
      ) : (
        <Table data={contests} columns={columns} />
      )}
    </div>
  );
}
