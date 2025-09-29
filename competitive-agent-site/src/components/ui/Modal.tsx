"use client";
import React from "react";

export type ModalProps = {
  isOpen: boolean;
  title?: string;
  onClose: () => void;
  footer?: React.ReactNode;
  children: React.ReactNode;
};

export default function Modal({ isOpen, title, onClose, footer, children }: ModalProps) {
  if (!isOpen) return null;
  return (
    <div
      role="dialog"
      aria-modal="true"
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.5)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 50,
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{ background: "#fff", padding: 20, borderRadius: 8, minWidth: 360, maxWidth: 720 }}
      >
        {title && <h3 style={{ marginTop: 0 }}>{title}</h3>}
        <div>{children}</div>
        {footer && <div style={{ marginTop: 16 }}>{footer}</div>}
      </div>
    </div>
  );
}


