"use client";
import React from "react";

export type InputProps = React.InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  error?: string;
};

export default function Input({ label, error, style, ...rest }: InputProps) {
  return (
    <div style={{ marginBottom: 12 }}>
      {label && (
        <label style={{ display: "block", marginBottom: 6, fontWeight: 600 }}>{label}</label>
      )}
      <input
        {...rest}
        style={{
          width: "100%",
          padding: "8px 10px",
          borderRadius: 6,
          border: `1px solid ${error ? "#dc2626" : "#d1d5db"}`,
          outline: "none",
          ...style,
        }}
      />
      {error && <div style={{ color: "#dc2626", marginTop: 6, fontSize: 12 }}>{error}</div>}
    </div>
  );
}


