"use client";

import { useState } from "react";

type SummaryRow = {
  group: string;
  wins: number;
  losses: number;
  draws: number;
  games: number;
  win_rate: number;
};

type MatchRow = {
  first_group: string;
  first_agent: string;
  second_group: string;
  second_agent: string;
  winner_symbol: string;
  winner_group: string | null;
  winner_agent: string | null;
};

const API_BASE = "http://localhost:5001";
const GAMES = [
  { id: "conn4", label: "Connect 4" },
  { id: "tictactoe", label: "Tic Tac Toe" },
];

function formatWinRate(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export default function RoundRobinPanel() {
  const [game, setGame] = useState<string>(GAMES[0]?.id ?? "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<SummaryRow[]>([]);
  const [matches, setMatches] = useState<MatchRow[]>([]);
  const [totalMatches, setTotalMatches] = useState(0);

  async function handleRun() {
    if (!game) {
      setError("choose a game");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/admin/tournaments/${game}/round_robin`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Request failed");
      }
      setSummary(data.summary ?? []);
      setMatches(data.matches ?? []);
      setTotalMatches(data.total_matches ?? 0);
    } catch (err) {
      setError((err as Error).message);
      setSummary([]);
      setMatches([]);
      setTotalMatches(0);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section style={{ border: "1px solid #ccc", padding: 16, marginTop: 24 }}>
      <h3>Round Robin Tournament</h3>
      <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 12 }}>
        <label htmlFor="round-robin-game">Game:</label>
        <select
          id="round-robin-game"
          value={game}
          onChange={(event) => setGame(event.target.value)}
          disabled={loading}
        >
          {GAMES.map((item) => (
            <option key={item.id} value={item.id}>
              {item.label}
            </option>
          ))}
        </select>
        <button type="button" onClick={handleRun} disabled={loading}>
          {loading ? "Running..." : "Run Tournament"}
        </button>
      </div>

      {error && <div style={{ color: "#b00020", marginBottom: 12 }}>{error}</div>}

      {summary.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <h4>Summary</h4>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", paddingBottom: 6 }}>Group</th>
                <th style={{ textAlign: "right", borderBottom: "1px solid #ccc", paddingBottom: 6 }}>Wins</th>
                <th style={{ textAlign: "right", borderBottom: "1px solid #ccc", paddingBottom: 6 }}>Losses</th>
                <th style={{ textAlign: "right", borderBottom: "1px solid #ccc", paddingBottom: 6 }}>Draws</th>
                <th style={{ textAlign: "right", borderBottom: "1px solid #ccc", paddingBottom: 6 }}>Games</th>
                <th style={{ textAlign: "right", borderBottom: "1px solid #ccc", paddingBottom: 6 }}>Win Rate</th>
              </tr>
            </thead>
            <tbody>
              {summary.map((row) => (
                <tr key={row.group}>
                  <td style={{ padding: "6px 0" }}>{row.group}</td>
                  <td style={{ textAlign: "right", padding: "6px 0" }}>{row.wins}</td>
                  <td style={{ textAlign: "right", padding: "6px 0" }}>{row.losses}</td>
                  <td style={{ textAlign: "right", padding: "6px 0" }}>{row.draws}</td>
                  <td style={{ textAlign: "right", padding: "6px 0" }}>{row.games}</td>
                  <td style={{ textAlign: "right", padding: "6px 0" }}>{formatWinRate(row.win_rate)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {matches.length > 0 && (
        <div>
          <h4>
            Matches <span style={{ color: "#666", fontSize: "0.9em" }}>({totalMatches} total)</span>
          </h4>
          <div style={{ maxHeight: 240, overflowY: "auto", border: "1px solid #eee" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr>
                  <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", paddingBottom: 6 }}>First</th>
                  <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", paddingBottom: 6 }}>Second</th>
                  <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", paddingBottom: 6 }}>Winner</th>
                </tr>
              </thead>
              <tbody>
                {matches.map((match, index) => (
                  <tr key={`${match.first_group}-${match.second_group}-${index}`}>
                    <td style={{ padding: "6px 8px" }}>
                      <strong>{match.first_group}</strong>
                      <div style={{ fontSize: "0.85em", color: "#555" }}>{match.first_agent}</div>
                    </td>
                    <td style={{ padding: "6px 8px" }}>
                      <strong>{match.second_group}</strong>
                      <div style={{ fontSize: "0.85em", color: "#555" }}>{match.second_agent}</div>
                    </td>
                    <td style={{ padding: "6px 8px" }}>
                      {match.winner_group ? (
                        <>
                          <strong>{match.winner_group}</strong>
                          <div style={{ fontSize: "0.85em", color: "#555" }}>{match.winner_agent}</div>
                        </>
                      ) : (
                        <span>Draw</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}
