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

  // Helper to determine RPS winner given two moves
  const determineRpsWinner = (
    move1: string | undefined,
    move2: string | undefined,
    name1: string,
    name2: string
  ) => {
    if (!move1 || !move2) return "Pending";
    const a = move1.toLowerCase().trim();
    const b = move2.toLowerCase().trim();
    if (a === b) return "Draw";
    const wins = (x: string, y: string) =>
      (x === "rock" && y === "scissors") ||
      (x === "scissors" && y === "paper") ||
      (x === "paper" && y === "rock");
    if (wins(a, b)) return name1;
    if (wins(b, a)) return name2;
    return "Invalid";
  };

  return (
    <div className="p-4 space-y-6">
      {/* Contest Info */}
      <div className="border rounded-lg p-4">
        <h2 className="text-2xl font-bold mb-4">{contest.name}</h2>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-sm text-gray-600">Game</p>
            <p className="font-medium capitalize">{contest.game}</p>
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

      {/* Action / Round History */}
      {actions.length > 0 && (
        <div className="border rounded-lg p-4">
          {contest.game === "rps" ? (
            // -------------------------
            // Round-based game (RPS)
            // -------------------------
            <>
              <h3 className="text-xl font-bold mb-4">Round History</h3>
              <p className="text-sm text-gray-600 mb-4">
                Total rounds: {Math.floor(actions.length / 2)}
                {actions.length % 2 === 1 ? " (1 round incomplete)" : ""}
              </p>

              <div className="space-y-2 max-h-96 overflow-y-auto">
                {Array.from({ length: Math.floor(actions.length / 2) }).map(
                  (_, roundIdx) => {
                    const a1 = actions[roundIdx * 2];
                    const a2 = actions[roundIdx * 2 + 1];
                    const move1 = a1?.action ?? "";
                    const move2 = a2?.action ?? "";
                    const winner = determineRpsWinner(
                      move1,
                      move2,
                      a1?.agent_name ?? contest.agent1.name,
                      a2?.agent_name ?? contest.agent2.name
                    );

                    return (
                      <div
                        key={roundIdx}
                        className="p-3 rounded bg-yellow-50 border-l-4 border-yellow-500"
                      >
                        <p className="font-medium">
                          Round {roundIdx + 1}: {a1?.agent_name ?? "Agent1"} (
                          {move1}) vs {a2?.agent_name ?? "Agent2"} ({move2})
                        </p>
                        <p className="text-sm text-gray-700 mt-1">
                          Winner: {winner}
                        </p>
                        {/* optional: show any round summary text if backend stored one */}
                        {a2?.board_state && a2.board_state !== "[]" && (
                          <details className="text-xs text-gray-600 mt-2">
                            <summary className="cursor-pointer hover:text-gray-800">
                              View round summary (raw)
                            </summary>
                            <pre className="mt-2 p-2 bg-white rounded border overflow-x-auto">
                              {a2.board_state}
                            </pre>
                          </details>
                        )}
                      </div>
                    );
                  }
                )}

                {/* Show incomplete round if exists */}
                {actions.length % 2 === 1 && (
                  <div className="p-3 rounded bg-gray-50 border-l-4 border-gray-300">
                    <p className="font-medium">
                      🕹️ Incomplete Round:{" "}
                      {actions[actions.length - 1].agent_name} (
                      {actions[actions.length - 1].action}) - waiting for
                      opponent move
                    </p>
                  </div>
                )}
              </div>
            </>
          ) : (
            // -------------------------
            // Move-based games (Connect4, TTT)
            // -------------------------
            <>
              <h3 className="text-xl font-bold mb-4">Move History</h3>
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
            </>
          )}
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
