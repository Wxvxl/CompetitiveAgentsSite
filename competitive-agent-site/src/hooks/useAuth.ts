import { useCallback, useEffect, useState } from "react";

export type AuthUser = {
  id: number;
  email: string;
  name?: string;
  role?: string;
  isAdmin?: boolean;
} | null;

export default function useAuth() {
  const [user, setUser] = useState<AuthUser>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:5000/api/me", { credentials: "include" });
      const data = await res.json();
      setUser(res.ok ? data.user : null);
    } catch (e) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await fetch("http://localhost:5000/api/logout", { method: "POST", credentials: "include" });
    } finally {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const isAdmin = !!(user && (user.isAdmin || user.role === "admin"));

  return { user, loading, refresh, logout, isAdmin } as const;
}


