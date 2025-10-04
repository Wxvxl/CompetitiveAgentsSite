"use client";

import { useState, useEffect } from "react";
import Button from "../ui/Button";
import Input from "../ui/Input";

interface Agent {
  id: number;
  name: string;
  game: string;
  groupname: string;
}

interface ContestCreationFormProps {
  onSuccess?: () => void;
}

export default function ContestCreationForm({
  onSuccess,
}: ContestCreationFormProps) {
  const [name, setName] = useState("");
  const [game, setGame] = useState("conn4");
  const [agent1Id, setAgent1Id] = useState("");
  const [agent2Id, setAgent2Id] = useState("");
  const [autoMatch, setAutoMatch] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [agents, setAgents] = useState<Agent[]>([]);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch("http://localhost:5001/api/admin/agents", {
        credentials: "include",
      });

      if (response.ok) {
        const data = await response.json();
        setAgents(data.agents || []);
      }
    } catch (err) {
      console.error("Failed to fetch agents:", err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:5001/api/contests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          name,
          game,
          agent1_id: autoMatch ? null : parseInt(agent1Id),
          agent2_id: autoMatch ? null : parseInt(agent2Id),
          auto_match: autoMatch,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setName("");
        setAgent1Id("");
        setAgent2Id("");
        setAutoMatch(false);

        // Dispatch custom event to notify other components
        window.dispatchEvent(new Event("contestCreated"));

        if (onSuccess) {
          onSuccess();
        }
      } else {
        setError(data.error || "Failed to create contest");
      }
    } catch (err) {
      setError("An error occurred while creating the contest");
    } finally {
      setLoading(false);
    }
  };

  const filteredAgents = agents.filter((agent) => agent.game === game);

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">Contest Name</label>
        <Input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter contest name"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Game</label>
        <select
          value={game}
          onChange={(e) => setGame(e.target.value)}
          className="w-full border rounded px-3 py-2"
          required
        >
          <option value="conn4">Connect 4</option>
          <option value="tictactoe">Tic-Tac-Toe</option>
        </select>
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="autoMatch"
          checked={autoMatch}
          onChange={(e) => setAutoMatch(e.target.checked)}
          className="rounded"
        />
        <label htmlFor="autoMatch" className="text-sm">
          Auto-match agents (FR3.2)
        </label>
      </div>

      {!autoMatch && (
        <>
          <div>
            <label className="block text-sm font-medium mb-1">Agent 1</label>
            <select
              value={agent1Id}
              onChange={(e) => setAgent1Id(e.target.value)}
              className="w-full border rounded px-3 py-2"
              required={!autoMatch}
            >
              <option value="">Select Agent 1</option>
              {filteredAgents.map((agent) => (
                <option key={agent.id} value={agent.id}>
                  {agent.name} ({agent.groupname})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Agent 2</label>
            <select
              value={agent2Id}
              onChange={(e) => setAgent2Id(e.target.value)}
              className="w-full border rounded px-3 py-2"
              required={!autoMatch}
            >
              <option value="">Select Agent 2</option>
              {filteredAgents
                .filter((agent) => agent.id.toString() !== agent1Id)
                .map((agent) => (
                  <option key={agent.id} value={agent.id}>
                    {agent.name} ({agent.groupname})
                  </option>
                ))}
            </select>
          </div>
        </>
      )}

      {error && <p className="text-red-500 text-sm">{error}</p>}

      <Button type="submit" disabled={loading}>
        {loading ? "Creating..." : "Create Contest"}
      </Button>
    </form>
  );
}
