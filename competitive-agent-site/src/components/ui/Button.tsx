"use client";
import React from "react";

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
  return (
    <button
      {...rest}
      disabled={disabled || isLoading}
      style={{
        ...baseStyle,
        ...variantStyle[variant],
        ...sizeStyle[size],
        opacity: disabled || isLoading ? 0.7 : 1,
        ...style,
      }}
    >
      {isLoading ? "Loading..." : children}
    </button>
  );
}


