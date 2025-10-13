"use client";
import React, { useState } from "react"; 

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";
type ButtonSize = "sm" | "md" | "lg";

export type ButtonProps = {
  children: React.ReactNode;
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
} & React.ButtonHTMLAttributes<HTMLButtonElement>;

const baseStyle: React.CSSProperties = {
  border: 0,
  borderRadius: 6,
  cursor: "pointer",
  fontWeight: 600,
  transition: "all 0.2s ease-in-out",
};

const variantStyle: Record<ButtonVariant, React.CSSProperties> = {
  primary: { background: "#2563eb", color: "#fff" },
  secondary: { background: "#e5e7eb", color: "#111827" },
  danger: { background: "#dc2626", color: "#fff" },
  ghost: { background: "transparent", color: "#2563eb", border: "1px solid #2563eb" },
};

const sizeStyle: Record<ButtonSize, React.CSSProperties> = {
  sm: { padding: "6px 10px", fontSize: 12 },
  md: { padding: "8px 14px", fontSize: 14 },
  lg: { padding: "12px 18px", fontSize: 16 },
};

export default function Button({ children, variant = "primary", size = "md", isLoading = false, style, disabled, ...rest }: ButtonProps) {

  const [isHovered, setIsHovered] = useState(false);


  const hoverStyle: React.CSSProperties = {
    transform: "scale(1.05)",
    boxShadow: "0 4px 15px rgba(0, 0, 0, 0.2)", 
  };

  return (
    <button
      {...rest}
      disabled={disabled || isLoading}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        ...baseStyle,
        ...variantStyle[variant],
        ...sizeStyle[size],
        opacity: disabled || isLoading ? 0.7 : 1,
        ...style,
        ...(isHovered && !disabled && !isLoading ? hoverStyle : {}),
      }}
    >
      {isLoading ? "Loading..." : children}
    </button>
  );
}