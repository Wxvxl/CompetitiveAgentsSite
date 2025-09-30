"use client";
import { useState, useEffect } from "react";
import Table, { Column } from "../ui/Table";

type User = {
  id: number;
  username: string;
  email: string;
  role: string;
  group_id: number | null;
};

type Group = {
  group_id: number;
  groupname: string;
};

export default function UserGroupManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [groups, setGroups] = useState<Group[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchUsers();
    fetchGroups();
  }, []);

  async function fetchUsers() {
    try {
      const res = await fetch("http://localhost:5000/api/users", {
        credentials: "include",
      });
      const data = await res.json();
      if (res.ok) setUsers(data.users);
    } catch (err) {
      setError("Failed to fetch users");
    }
  }

  async function fetchGroups() {
    try {
      const res = await fetch("http://localhost:5000/api/groups", {
        credentials: "include",
      });
      const data = await res.json();
      if (res.ok) setGroups(data.groups);
    } catch (err) {
      setError("Failed to fetch groups");
    }
  }

  async function handleAssignGroup(userId: number, groupId: string) {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:5000/api/admin/assign-group", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          user_id: userId,
          group_id: groupId === "" ? null : Number(groupId),
        }),
      });

      if (!res.ok) throw new Error("Failed to assign group");
      await fetchUsers(); // Refresh user list
    } catch (err) {
      setError("Failed to assign group");
    } finally {
      setLoading(false);
    }
  }

  if (error) return <div className="text-red-500">{error}</div>;

  const columns: Column<User>[] = [
    {
      key: "username",
      header: "Username",
    },
    {
      key: "email",
      header: "Email",
    },
    {
      key: "group",
      header: "Current Group",
      render: (row) =>
        groups.find((g) => g.group_id === row.group_id)?.groupname || "None",
    },
    {
      key: "actions",
      header: "Actions",
      render: (row) => (
        <select
          value={row.group_id || ""}
          onChange={(e) => handleAssignGroup(row.id, e.target.value)}
          disabled={loading || row.role === "admin"}
        >
          <option value="">No Group</option>
          {groups.map((group) => (
            <option key={group.group_id} value={group.group_id}>
              {group.groupname}
            </option>
          ))}
        </select>
      ),
    },
  ];

  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <Table<User>
      columns={columns}
      data={users}
      isLoading={loading}
      emptyText="No users found"
    />
  );
}
