"use client";
import React, { useState } from "react"; 
import Button from "../ui/Button";
import useAuth from "../../hooks/useAuth";

export default function Header() {
  const { user, isAdmin, logout, loading } = useAuth();


  const [isAdminHovered, setIsAdminHovered] = useState(false);
  const [isRegisterHovered, setIsRegisterHovered] = useState(false);
  const [isLoginHovered, setIsLoginHovered] = useState(false);



  const headerStyle: React.CSSProperties = {
    background: "#ffffff",
    color: "#1f2937",
    padding: "1rem 1.5rem",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    borderBottom: "1px solid #e5e7eb",
    boxShadow: "0 2px 4px rgba(0, 0, 0, 0.05)",
  };

  const logoStyle: React.CSSProperties = {
    color: "#111827",
    textDecoration: "none",
    margin: 0,
    fontSize: 20
  };

  const navContainerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem' 
  };

  const userInfoStyle: React.CSSProperties = {
    marginRight: 12,
    fontWeight: 500,
    color: "#4b5563",
    fontSize: "0.9rem",
  };


  const baseLinkStyle: React.CSSProperties = {
    padding: "8px 14px",
    borderRadius: 6,
    fontWeight: 600,
    textDecoration: "none",
    display: "inline-block",
    transition: "all 0.2s ease-in-out", 
  };


  const secondaryLinkStyle: React.CSSProperties = {
    ...baseLinkStyle,
    background: "#f3f4f6",
    color: "#111827",
    border: "1px solid #e5e7eb",
    marginRight: 8,
  };


  const primaryLinkStyle: React.CSSProperties = {
    ...baseLinkStyle,
    background: "#2563eb",
    color: "#fff",
  };
  

  const hoverStyle: React.CSSProperties = {
    transform: "scale(1.05)",
    boxShadow: "0 4px 15px rgba(0, 0, 0, 0.1)",
  };

  return (
    <header style={headerStyle}>
      <a href="/" style={{ textDecoration: "none" }}>
        <h1 style={logoStyle}>
          Competitive Agents Dashboard
        </h1>
      </a>
      <div style={navContainerStyle}>
        {loading ? (
          <span>Loading...</span>
        ) : user ? (
          <>
            <span style={userInfoStyle}>
              {user.email}
              {isAdmin ? " (Admin)" : ""}
            </span>
            {isAdmin && (
              <a
                href="/admin"
                onMouseEnter={() => setIsAdminHovered(true)}
                onMouseLeave={() => setIsAdminHovered(false)}
                style={{
                  ...secondaryLinkStyle,
                  ...(isAdminHovered ? hoverStyle : {}), 
                }}
              >
                Admin
              </a>
            )}
            <Button onClick={logout} variant="ghost">
              Logout
            </Button>
          </>
        ) : (
          <>
            <a
              href="/register"
              onMouseEnter={() => setIsRegisterHovered(true)}
              onMouseLeave={() => setIsRegisterHovered(false)}
              style={{
                ...secondaryLinkStyle,
                ...(isRegisterHovered ? hoverStyle : {}), 
              }}
            >
              Register
            </a>
            <a
              href="/login"
              onMouseEnter={() => setIsLoginHovered(true)}
              onMouseLeave={() => setIsLoginHovered(false)}
              style={{
                ...primaryLinkStyle,
                ...(isLoginHovered ? hoverStyle : {}),
              }}
            >
              Login
            </a>
          </>
        )}
      </div>
    </header>
  );
}