"use client";
import React from "react";
import Button from "../components/ui/Button";
import Modal from "../components/ui/Modal";
import AgentUploadForm from "../components/forms/AgentUploadForm";
import useAuth from "../hooks/useAuth";
import useModal from "../hooks/useModal";

export default function DashboardPage() {
  const { user, loading, logout, isAdmin } = useAuth();
  const { open, openModal, closeModal } = useModal(false);

  return (
    <section>
      <h2>Dashboard</h2>
      {loading ? (
        <div>Loading...</div>
      ) : user ? (
        <>
          <p>Welcome, {user.email}!</p>
          {isAdmin && (
            <p>
              <strong>You are an admin.</strong>
              <br />
              <a href="/admin">Go to Admin Panel</a>
            </p>
          )}
          <Button onClick={logout} variant="ghost">
            Logout
          </Button>
          <Button onClick={openModal} style={{ marginLeft: 8 }}>
            Submit Agent
          </Button>
          <Modal isOpen={open} onClose={closeModal} title="Upload Agent">
            <AgentUploadForm onUploaded={() => closeModal()} />
          </Modal>
        </>
      ) : (
        <ul>
          <li>
            <a href="/register">Register</a>
          </li>
          <li>
            <a href="/login">Login</a>
          </li>
        </ul>
      )}
    </section>
  );
}
