"use client";

import { useEffect, useMemo, useState } from "react";

type Group = {
  id: number;
  name: string;
};

type User = {
  id: number;
  username: string;
  email: string;
  role: string;
  group_id: number | null;
  group_name?: string | null;
};

type Message = {
  type: "success" | "error";
  text: string;
};

const API_BASE = "http://localhost:5001";

async function readJson(res: Response) {
  const contentType = res.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return res.json();
  }
  return {};
}

export default function GroupManagement() {
  const [groups, setGroups] = useState<Group[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [newGroup, setNewGroup] = useState("");
  const [message, setMessage] = useState<Message | null>(null);
  const [loading, setLoading] = useState(false);

  const sortedUsers = useMemo(() => {
    return [...users].sort((a, b) => a.username.localeCompare(b.username));
  }, [users]);

  useEffect(() => {
    fetchGroups();
    fetchUsers();
  }, []);

  async function fetchGroups() {
    try {
      const res = await fetch(`${API_BASE}/api/groups`, {
        credentials: "include",
      });
      if (!res.ok) {
        const data = await readJson(res);
        throw new Error(data.error || "Failed to load groups");
      }
      const data = await res.json();
      setGroups(data.groups ?? []);
    } catch (error) {
      setMessage({ type: "error", text: (error as Error).message });
    }
  }

  async function fetchUsers() {
    try {
      const res = await fetch(`${API_BASE}/api/users`, {
        credentials: "include",
      });
      if (!res.ok) {
        const data = await readJson(res);
        throw new Error(data.error || "Failed to load users");
      }
      const data = await res.json();
      const students = (data.users ?? []).filter((user: User) => user.role === "student");
      setUsers(students);
    } catch (error) {
      setMessage({ type: "error", text: (error as Error).message });
    }
  }

  async function handleCreateGroup(e: React.FormEvent) {
    e.preventDefault();
    if (!newGroup.trim()) {
      setMessage({ type: "error", text: "Group name cannot be empty" });
      return;
    }
    setLoading(true);
    setMessage(null);
    try {
      const res = await fetch(`${API_BASE}/api/groups`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ name: newGroup.trim() }),
      });
      const data = await readJson(res);
      if (!res.ok) {
        throw new Error(data.error || "Failed to create group");
      }
      setGroups((prev) => [...prev, data.group]);
      setNewGroup("");
      setMessage({ type: "success", text: `Created group "${data.group.name}"` });
    } catch (error) {
      setMessage({ type: "error", text: (error as Error).message });
    } finally {
      setLoading(false);
    }
  }

  async function handleAssign(userId: number, groupId: number | null) {
    setLoading(true);
    setMessage(null);
    try {
      const res = await fetch(`${API_BASE}/api/users/${userId}/group`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ group_id: groupId }),
      });
      const data = await readJson(res);
      if (!res.ok) {
        throw new Error(data.error || "Failed to update user");
      }
      setUsers((prev) =>
        prev.map((user) =>
          user.id === userId
            ? { ...user, group_id: data.user.group_id, group_name: data.user.group_name ?? null }
            : user,
        ),
      );
      const groupName = groupId ? groups.find((g) => g.id === groupId)?.name ?? data.user.group_name : "No group";
      setMessage({ type: "success", text: `Updated ${data.user.username} -> ${groupName}` });
    } catch (error) {
      setMessage({ type: "error", text: (error as Error).message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <section style={{ border: "1px solid #ccc", padding: 16, marginTop: 24 }}>
      <h3>Group Management</h3>
      <form onSubmit={handleCreateGroup} style={{ marginBottom: 16 }}>
        <input
          type="text"
          value={newGroup}
          onChange={(event) => setNewGroup(event.target.value)}
          placeholder="New group name"
        />
        <button type="submit" disabled={loading} style={{ marginLeft: 8 }}>
          Create
        </button>
      </form>

      {message && (
        <div style={{
          marginBottom: 16,
          color: message.type === "error" ? "#b00020" : "#0f730c",
        }}>
          {message.text}
        </div>
      )}

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", paddingBottom: 8 }}>Username</th>
            <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", paddingBottom: 8 }}>Email</th>
            <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", paddingBottom: 8 }}>Role</th>
            <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", paddingBottom: 8 }}>Group</th>
          </tr>
        </thead>
        <tbody>
          {sortedUsers.map((user) => (
            <tr key={user.id}>
              <td style={{ padding: "8px 0" }}>{user.username}</td>
              <td style={{ padding: "8px 0" }}>{user.email}</td>
              <td style={{ padding: "8px 0" }}>{user.role}</td>
              <td style={{ padding: "8px 0" }}>
                <select
                  value={user.group_id ?? ""}
                  onChange={(event) => {
                    const value = event.target.value;
                    const nextGroup = value === "" ? null : Number(value);
                    handleAssign(user.id, nextGroup);
                  }}
                  disabled={loading}
                >
                  <option value="">No group</option>
                  {groups.map((group) => (
                    <option key={group.id} value={group.id}>
                      {group.name}
                    </option>
                  ))}
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
