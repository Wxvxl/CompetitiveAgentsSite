"use client";

import { useState, useEffect } from "react";
import Button from "../ui/Button";

interface ContestDetails {
  contest: {
    contest_id: number;
    name: string;
    game: string;
    agent1: { id: number; name: string; group: string };
    agent2: { id: number; name: string; group: string };
    winner_id: number | null;
    status: string;
    created_at: string;
    completed_at: string | null;
  };
  actions: Array<{
    move_number: number;
    agent_id: number;
    agent_name: string;
    action: string;
    board_state: string;
  }>;
}

interface ContestDetailsViewProps {
  contestId: number;
  onClose?: () => void;
}

export default function ContestDetailsView({
  contestId,
  onClose,
}: ContestDetailsViewProps) {
  const [details, setDetails] = useState<ContestDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchContestDetails();
  }, [contestId]);

  const fetchContestDetails = async () => {
    try {
      const response = await fetch(
        `http://localhost:5001/api/contests/${contestId}`,
        {
          credentials: "include",
        }
      );

      if (response.ok) {
        const data = await response.json();
        setDetails(data);
      } else {
        setError("Failed to fetch contest details");
      }
    } catch (err) {
      setError("An error occurred while fetching contest details");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-4">Loading contest details...</div>;
  }

  if (error || !details) {
    return (
      <div className="p-4">
        <p className="text-red-500">{error || "Contest not found"}</p>
        {onClose && (
          <Button onClick={onClose} className="mt-4">
            Close
          </Button>
        )}
      </div>
    );
  }

  const { contest, actions } = details;
  const winnerName = contest.winner_id
    ? contest.winner_id === contest.agent1.id
      ? contest.agent1.name
      : contest.agent2.name
    : "Draw";

  return (
    <div className="p-4 space-y-6">
      {/* Contest Info */}
      <div className="border rounded-lg p-4">
        <h2 className="text-2xl font-bold mb-4">{contest.name}</h2>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-sm text-gray-600">Game</p>
            <p className="font-medium">{contest.game}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Status</p>
            <p className="font-medium capitalize">{contest.status}</p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="border rounded p-3 bg-blue-50">
            <p className="text-sm text-gray-600">Agent 1</p>
            <p className="font-medium">{contest.agent1.name}</p>
            <p className="text-sm text-gray-500">
              Group: {contest.agent1.group}
            </p>
          </div>
          <div className="border rounded p-3 bg-green-50">
            <p className="text-sm text-gray-600">Agent 2</p>
            <p className="font-medium">{contest.agent2.name}</p>
            <p className="text-sm text-gray-500">
              Group: {contest.agent2.group}
            </p>
          </div>
        </div>

        {contest.status === "completed" && (
          <div className="border-t pt-4">
            <p className="text-sm text-gray-600">Winner</p>
            <p className="text-xl font-bold text-green-600">{winnerName}</p>
            <p className="text-sm text-gray-500">
              Completed:{" "}
              {contest.completed_at
                ? new Date(contest.completed_at).toLocaleString()
                : "N/A"}
            </p>
          </div>
        )}
      </div>

      {/* FR3.3: Action History */}
      {actions.length > 0 && (
        <div className="border rounded-lg p-4">
          <h3 className="text-xl font-bold mb-4">Match History (FR3.3)</h3>
          <p className="text-sm text-gray-600 mb-4">
            Total moves: {actions.length}
          </p>

          <div className="space-y-2 max-h-96 overflow-y-auto">
            {actions.map((action, idx) => {
              const isAgent1 = action.agent_id === contest.agent1.id;
              return (
                <div
                  key={idx}
                  className={`p-3 rounded ${
                    isAgent1
                      ? "bg-blue-50 border-l-4 border-blue-500"
                      : "bg-green-50 border-l-4 border-green-500"
                  }`}
                >
                  <div className="flex justify-between items-start mb-1">
                    <span className="font-medium">
                      Move {action.move_number + 1}: {action.agent_name}
                    </span>
                    <span className="text-sm text-gray-600">
                      Action: {action.action}
                    </span>
                  </div>
                  <details className="text-xs text-gray-600 mt-2">
                    <summary className="cursor-pointer hover:text-gray-800">
                      View board state
                    </summary>
                    <pre className="mt-2 p-2 bg-white rounded border overflow-x-auto">
                      {action.board_state}
                    </pre>
                  </details>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Close Button */}
      {onClose && (
        <div className="flex justify-end">
          <Button onClick={onClose}>Close</Button>
        </div>
      )}
    </div>
  );
}
