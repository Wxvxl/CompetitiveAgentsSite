"use client";
import React from "react";
import useAuth from "../../hooks/useAuth";

export type RoleGuardProps = {
  allow: "admin" | "student" | "any";
  fallback?: React.ReactNode;
  children: React.ReactNode;
};

export default function RoleGuard({
  allow,
  fallback = null,
  children,
}: RoleGuardProps) {
  const { user, loading, isAdmin } = useAuth();

  if (loading) return <div>Loading...</div>;

  if (!user) return <>{fallback}</>;

  if (allow === "any") return <>{children}</>;

  if (allow === "admin" && isAdmin) return <>{children}</>;
  if (allow === "student" && !isAdmin) return <>{children}</>;

  return <>{fallback}</>;
}
