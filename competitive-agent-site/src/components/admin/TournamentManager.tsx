"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import Table, { Column } from "../ui/Table";

type LeaderboardEntry = {
  agent_id: number;
  groupname: string;
  agent_name: string;
  points: number;
  rounds_played: number;
};

type TournamentSummary = {
  id: number;
  name: string;
  game: string;
  rounds: number | null;
  status: string;
  created_at: string | null;
  completed_rounds: number;
  leaderboard: LeaderboardEntry[];
};

type TournamentMatch = {
  id: number;
  agent1_id: number;
  agent2_id: number | null;
  agent1_score: number;
  agent2_score: number;
  result: string;
  winner_agent_id: number | null;
  metadata: any;
  created_at: string | null;
};

type TournamentRound = {
  round_id: number;
  round_number: number;
  created_at: string | null;
  matches: TournamentMatch[];
};

type TournamentStanding = LeaderboardEntry;

type TournamentDetail = {
  tournament: {
    id: number;
    name: string;
    game: string;
    rounds: number | null;
    status: string;
    created_at: string | null;
  };
  rounds: TournamentRound[];
  standings: TournamentStanding[];
};

const GAME_OPTIONS = [
  { value: "conn4", label: "Conn 4" },
  { value: "tictactoe", label: "Tic Tac Toe" },
];

export default function TournamentManager() {
  const [summaries, setSummaries] = useState<TournamentSummary[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<TournamentDetail | null>(null);
  const [loadingList, setLoadingList] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string>("");
  const [formState, setFormState] = useState({
    game: GAME_OPTIONS[0].value,
  });

  useEffect(() => {
    refreshSummaries();
  }, []);

  async function refreshSummaries() {
    setLoadingList(true);
    setError("");
    try {
      const res = await fetch("http://localhost:5001/api/admin/tournaments", {
        credentials: "include",
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to load tournaments");
      setSummaries(data.tournaments || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tournaments");
    } finally {
      setLoadingList(false);
    }
  }

  async function loadDetail(tournamentId: number) {
    setLoadingDetail(true);
    setError("");
    try {
      const res = await fetch(
        `http://localhost:5001/api/admin/tournaments/${tournamentId}`,
        {
          credentials: "include",
        }
      );
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to load tournament details");
      setDetail(data);
      setSelectedId(tournamentId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tournament details");
    } finally {
      setLoadingDetail(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setCreating(true);
    setError("");
    try {
      const res = await fetch("http://localhost:5001/api/admin/tournaments", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          game: formState.game,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to start tournament");
      await refreshSummaries();
      if (data.tournament_id) {
        await loadDetail(data.tournament_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start tournament");
    } finally {
      setCreating(false);
    }
  }

  const summaryColumns: Column<TournamentSummary>[] = useMemo(
    () => [
      { key: "name", header: "Name" },
      { key: "game", header: "Game" },
      { key: "status", header: "Status" },
      {
        key: "created_at",
        header: "Created",
        render: (row) => (row.created_at ? new Date(row.created_at).toLocaleString() : "-"),
        width: 200,
      },
      {
        key: "completed_rounds",
        header: "Rounds Played",
        render: (row) => row.completed_rounds,
        width: 140,
      },
      {
        key: "actions",
        header: "Actions",
        render: (row) => (
          <button
            onClick={() => loadDetail(row.id)}
            disabled={loadingDetail && selectedId === row.id}
            style={{ padding: "4px 8px" }}
          >
            View
          </button>
        ),
        width: 120,
      },
    ],
    [loadingDetail, selectedId]
  );

  const standingsColumns: Column<TournamentStanding>[] = [
    {
      key: "groupname",
      header: "Group",
    },
    {
      key: "agent_name",
      header: "Agent",
    },
    {
      key: "points",
      header: "Points",
      render: (row) => row.points,
      width: 120,
    },
    {
      key: "rounds_played",
      header: "Rounds",
      width: 100,
    },
  ];

  function renderMatch(match: TournamentMatch) {
    const metadata = match.metadata || {};
    const agent1Label = metadata.agent1
      ? `${metadata.agent1.group} (${metadata.agent1.name})`
      : `Agent ${match.agent1_id}`;
    const agent2Label =
      match.result === "bye"
        ? "BYE"
        : metadata.agent2
        ? `${metadata.agent2.group} (${metadata.agent2.name})`
        : match.agent2_id
        ? `Agent ${match.agent2_id}`
        : "Unknown";
    return (
      <div
        key={match.id}
        style={{
          display: "flex",
          justifyContent: "space-between",
          padding: "6px 0",
          borderBottom: "1px solid #f3f4f6",
        }}
      >
        <div style={{ flex: 2 }}>
          <strong>{agent1Label}</strong> vs <strong>{agent2Label}</strong>
        </div>
        <div style={{ flex: 1, textAlign: "right" }}>
          {match.agent1_score} - {match.agent2_score}
        </div>
        <div style={{ flex: 1, textAlign: "right", color: "#374151" }}>
          {match.result === "bye" ? "Bye" : metadata.winner || match.result}
        </div>
      </div>
    );
  }

  return (
    <div>
      <h3>Knockout Tournament</h3>
      <form onSubmit={handleSubmit} style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 16 }}>
        <label style={{ display: "flex", flexDirection: "column", fontSize: 12, color: "#6b7280" }}>
          Game Type
          <select
            value={formState.game}
            onChange={(e) => setFormState((prev) => ({ ...prev, game: e.target.value }))}
            style={{ padding: 8, minWidth: 180 }}
          >
            {GAME_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" disabled={creating} style={{ padding: "8px 16px" }}>
          {creating ? "Starting..." : "Start"}
        </button>
      </form>

      {error && <div style={{ color: "#dc2626", marginBottom: 12 }}>{error}</div>}

      <Table<TournamentSummary>
        columns={summaryColumns}
        data={summaries}
        isLoading={loadingList}
        emptyText="No tournaments yet"
      />

      {selectedId && detail && (
        <div style={{ marginTop: 24 }}>
          <h4>
            {detail.tournament.name} – {detail.tournament.game}
          </h4>
          <p style={{ color: "#6b7280", marginBottom: 12 }}>
            Status: {detail.tournament.status} · Created at: {detail.tournament.created_at ? new Date(detail.tournament.created_at).toLocaleString() : "Unknown"}
          </p>

          <div style={{ marginBottom: 24 }}>
            <h5>Standings</h5>
            <Table<TournamentStanding>
              columns={standingsColumns}
              data={detail.standings}
              isLoading={loadingDetail}
              emptyText="No standings yet"
            />
          </div>

          <div>
            <h5>Rounds</h5>
            {detail.rounds.length === 0 ? (
              <p style={{ color: "#6b7280" }}>No rounds recorded.</p>
            ) : (
              detail.rounds.map((round) => (
                <div key={round.round_id} style={{ border: "1px solid #e5e7eb", borderRadius: 8, padding: 12, marginBottom: 16 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                    <strong>Round {round.round_number}</strong>
                    <span style={{ color: "#6b7280" }}>
                      {round.created_at ? new Date(round.created_at).toLocaleString() : ""}
                    </span>
                  </div>
                  {round.matches.length === 0 ? (
                    <p style={{ color: "#6b7280" }}>No matches recorded for this round.</p>
                  ) : (
                    <div>
                      {round.matches.map((match) => renderMatch(match))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
